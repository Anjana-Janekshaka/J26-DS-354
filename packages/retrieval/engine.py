"""Retrieval Engine (RAG) as a strategy module.

Write path (per ingested turn):
  1. embed the turn, run the write-time granularity decision against the open segment;
  2. index the turn immediately as a provisional turn-level chunk (FAISS IndexFlatIP) so it is
     retrievable at once, and run the two-stage contradiction check against older chunks;
  3. when a boundary closes the open segment, a multi-turn segment replaces its provisional turn
     chunks (flags are carried over and ids aliased); a single-turn segment stays turn-level.

Read path: top-K cosine search, packed into the token budget; a flagged (stale) chunk is never
dropped silently - it is annotated and its superseding chunk is pulled in next to it.
"""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from contracts import (
    ContradictionFlag,
    ConversationTurn,
    RagQuality,
    Readiness,
    StrategyModuleOutput,
    TurnSignal,
    count_tokens,
)
from contracts.text import CONTEXT_BLOCK_SEPARATOR, Embedder, code_signatures

from .chunking import BoundaryConfig, BoundaryDecision, Mode, decide_boundary
from .contradiction import ContradictionChecker, ContradictionConfig
from .index import VectorIndex
from .lexical import BM25Index, reciprocal_rank_fusion
from .nli import NLIScorer


class RetrievalConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mode: Mode = "adaptive"
    top_k: int = Field(default=24, ge=1)  # upper bound; the token budget is the binding limit
    min_score: float = 0.15
    check_contradictions: bool = True
    # Read-path options (selected on the LoCoMo dev split; see CLAUDE.md 12.4):
    compact_headers: bool = True  # "[turns: t0012]" instead of "[chunk turn:t0012 | turn | turns: t0012 | score 0.45]"
    reranker: str | None = None  # cross-encoder model name; reranks the top ``rerank_candidates`` FAISS hits
    rerank_candidates: int = Field(default=50, ge=1)
    # The reranker is trained on web QA (MS MARCO) and ranks prose above source code, so code tasks
    # (per the TurnSignal task type) keep the bi-encoder ranking. See CLAUDE.md section 12.
    rerank_skip_task_types: tuple[str, ...] = ("code_generation", "code_refactor")
    neighbors: int = Field(default=0, ge=0)  # adjacent turns added around each retrieved turn chunk
    # v2 options, evaluated on dev only after the 2026-10-15 test run (off in the frozen system):
    hybrid: bool = False  # fuse dense and BM25 rankings with reciprocal rank fusion
    rrf_k: int = Field(default=60, ge=1)
    mmr_lambda: float | None = Field(default=None, ge=0.0, le=1.0)  # redundancy-aware order (1 = pure relevance)
    boundary: BoundaryConfig = Field(default_factory=BoundaryConfig)
    contradiction: ContradictionConfig = Field(default_factory=ContradictionConfig)


@dataclass
class Chunk:
    chunk_id: str
    granularity: str
    turns: list[ConversationTurn]
    text: str
    vec: np.ndarray
    faiss_id: int
    seq: int
    symbols: dict[str, str]
    provisional: bool = False
    active: bool = True
    superseded_by: str | None = None
    confidence: float = 0.0
    verifier: str | None = None
    evidence: tuple[str, str] | None = None

    @property
    def turn_ids(self) -> list[str]:
        return [t.turn_id for t in self.turns]


@dataclass
class _OpenSegment:
    turns: list[ConversationTurn] = field(default_factory=list)
    vecs: list[np.ndarray] = field(default_factory=list)
    tokens: int = 0
    defines_code: bool = False


class RetrievalEngine:
    name = "rag"

    def __init__(self, embedder: Embedder | None = None, nli: NLIScorer | None = None, config: RetrievalConfig | None = None):
        self.config = config or RetrievalConfig()
        if embedder is None:
            from .embedder import SentenceTransformerEmbedder

            embedder = SentenceTransformerEmbedder()
        if nli is None and self.config.check_contradictions:
            from .nli import CrossEncoderNLI

            nli = CrossEncoderNLI()
        self.embedder = embedder
        self.checker = ContradictionChecker(embedder, nli if self.config.check_contradictions else None, self.config.contradiction)
        self.index = VectorIndex(embedder.dim)
        self.chunks: dict[str, Chunk] = {}
        self._by_faiss: dict[int, str] = {}
        self._alias: dict[str, str] = {}
        self._open = _OpenSegment()
        self._shift: dict[str, bool] = {}
        self._next_faiss = 0
        self._seq = 0
        self.boundary_log: list[tuple[str, BoundaryDecision]] = []
        self._latency_ema_ms = 1.0
        self._lexical = BM25Index() if self.config.hybrid else None
        self._turns: list[ConversationTurn] = []
        self._pos: dict[str, int] = {}
        self._reranker = None
        if self.config.reranker:
            from .rerank import CrossEncoderReranker

            self._reranker = CrossEncoderReranker(self.config.reranker)

    # ------------------------------------------------------------------ helpers
    def resolve(self, chunk_id: str) -> str:
        seen = set()
        while chunk_id in self._alias and chunk_id not in seen:
            seen.add(chunk_id)
            chunk_id = self._alias[chunk_id]
        return chunk_id

    def _add_chunk(self, turns: list[ConversationTurn], granularity: str, provisional: bool, vec: np.ndarray | None = None) -> Chunk:
        text = "\n".join(t.render() for t in turns)
        if vec is None:
            vec = self.embedder.encode(["\n".join(t.content for t in turns)])[0]
        cid = f"turn:{turns[0].turn_id}" if granularity == "turn" else f"seg:{turns[0].turn_id}-{turns[-1].turn_id}"
        symbols: dict[str, str] = {}
        for t in turns:
            symbols.update(code_signatures(t.content))
        self._seq += 1
        chunk = Chunk(cid, granularity, list(turns), text, vec, self._next_faiss, self._seq, symbols, provisional)
        self.index.add([self._next_faiss], vec.reshape(1, -1))
        self._by_faiss[self._next_faiss] = cid
        self._next_faiss += 1
        self.chunks[cid] = chunk
        if self._lexical is not None:
            self._lexical.add(cid, "\n".join(t.content for t in turns))
        return chunk

    def _deactivate(self, chunk: Chunk) -> None:
        chunk.active = False
        self.index.remove([chunk.faiss_id])
        if self._lexical is not None:
            self._lexical.remove(chunk.chunk_id)

    def _flag(self, older_id: str, newer_id: str, confidence: float, verifier: str, evidence: tuple[str, str]) -> None:
        older = self.chunks[self.resolve(older_id)]
        if older.superseded_by is None or self.chunks[self.resolve(older.superseded_by)].seq < self.chunks[self.resolve(newer_id)].seq:
            older.superseded_by = newer_id
            older.confidence = confidence
            older.verifier = verifier
            older.evidence = evidence

    def _check(self, chunk: Chunk) -> None:
        if not self.config.check_contradictions and not chunk.symbols:
            return
        older = [
            (c.chunk_id, c.text, c.vec, c.symbols)
            for c in self.chunks.values()
            if c.active and c.chunk_id != chunk.chunk_id and c.seq < chunk.seq
        ]
        for v in self.checker.check(chunk.chunk_id, chunk.text, chunk.vec, chunk.symbols, older):
            self._flag(v.older_id, v.newer_id, v.confidence, v.verifier, v.evidence)

    def _close_open_segment(self) -> None:
        seg = self._open
        self._open = _OpenSegment()
        if len(seg.turns) < 2:
            for t in seg.turns:
                c = self.chunks.get(f"turn:{t.turn_id}")
                if c is not None:
                    c.provisional = False
            return
        members = [self.chunks[f"turn:{t.turn_id}"] for t in seg.turns]
        vec = np.mean(seg.vecs, axis=0)
        vec = (vec / (np.linalg.norm(vec) or 1.0)).astype(np.float32)
        new = self._add_chunk(seg.turns, "segment", provisional=False, vec=vec)
        new.seq = max(m.seq for m in members)  # keep write-order of its newest turn
        flagged = [m for m in members if m.superseded_by]
        if flagged:
            worst = max(flagged, key=lambda m: m.confidence)
            new.superseded_by, new.confidence, new.verifier, new.evidence = worst.superseded_by, worst.confidence, worst.verifier, worst.evidence
        for m in members:
            self._deactivate(m)
            self._alias[m.chunk_id] = new.chunk_id
        if new.superseded_by and self.resolve(new.superseded_by) == new.chunk_id:
            # The superseding claim is inside this same segment: the segment carries both versions.
            new.superseded_by, new.confidence, new.verifier, new.evidence = None, 0.0, None, None

    # ------------------------------------------------------------------ StrategyModule
    def observe_signal(self, signal: TurnSignal) -> None:
        self._shift[signal.turn_id] = signal.shift_detected

    def ingest(self, turn: ConversationTurn) -> None:
        self._pos[turn.turn_id] = len(self._turns)
        self._turns.append(turn)
        vec = self.embedder.encode([turn.content])[0]
        tokens = count_tokens(turn.render())
        defines = bool(code_signatures(turn.content))
        decision = decide_boundary(
            self.config.mode,
            self.config.boundary,
            self._open.vecs,
            self._open.tokens,
            vec,
            tokens,
            self._shift.get(turn.turn_id, False),
            defines,
            self._open.defines_code,
        )
        self.boundary_log.append((turn.turn_id, decision))
        if decision.boundary:
            self._close_open_segment()
        self._open.turns.append(turn)
        self._open.vecs.append(vec)
        self._open.tokens += tokens
        self._open.defines_code = self._open.defines_code or defines
        chunk = self._add_chunk([turn], "turn", provisional=True, vec=vec)
        self._check(chunk)
        if self.config.mode == "turn":
            self._close_open_segment()

    def search(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        qv = self.embedder.encode([query])[0]
        out = []
        for fid, score in self.index.search(qv, k):
            cid = self._by_faiss.get(fid)
            if cid is not None and self.chunks[cid].active:
                out.append((self.chunks[cid], score))
        return out

    def _candidates(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        """Dense top-k, or (``hybrid``) dense and BM25 rankings fused by reciprocal rank fusion.
        The dense similarity floor still applies to dense-only hits; a chunk that matches the query's
        exact terms (BM25 > 0) is kept even when its embedding similarity is low."""
        dense = [(c, sc) for c, sc in self.search(query, k) if sc >= self.config.min_score]
        if self._lexical is None:
            return dense
        lex = [(cid, sc) for cid, sc in self._lexical.search(query, k) if cid in self.chunks and self.chunks[cid].active]
        fused = reciprocal_rank_fusion([[c.chunk_id for c, _ in dense], [cid for cid, _ in lex]], self.config.rrf_k)
        # Same candidate count as dense-only, so the reranker's cost does not grow with fusion.
        return [(self.chunks[cid], sc) for cid, sc in sorted(fused.items(), key=lambda x: -x[1])][:k]

    def _mmr(self, results: list[tuple[Chunk, float]], lam: float, pool: int = 60) -> list[tuple[Chunk, float]]:
        """Maximal marginal relevance over the top ``pool`` results: prefer relevant chunks that are not
        near-duplicates of chunks already chosen (agent memory is full of near-repeats)."""
        head, tail = results[:pool], results[pool:]
        if len(head) < 2:
            return results
        n = len(head)
        rel = [1.0 - i / n for i in range(n)]  # rank-based relevance, comparable across score scales
        vecs = np.stack([c.vec for c, _ in head])
        sims = vecs @ vecs.T
        chosen: list[int] = []
        left = list(range(n))
        while left:
            best = max(left, key=lambda i: lam * rel[i] - (1 - lam) * (max(sims[i, j] for j in chosen) if chosen else 0.0))
            chosen.append(best)
            left.remove(best)
        return [head[i] for i in chosen] + tail

    def _with_neighbors(self, chunk: Chunk, exclude: set[str] | frozenset[str] = frozenset()) -> list[ConversationTurn]:
        """The chunk's turns plus ``neighbors`` adjacent turns on each side (dialogue answers often
        sit in the reply right after the turn that matches the question). Neighbours already shown
        in an earlier block (``exclude``) are left out; the chunk's own turns never are."""
        n = self.config.neighbors
        if n == 0 or chunk.granularity != "turn":
            return list(chunk.turns)
        i = self._pos.get(chunk.turns[0].turn_id)
        if i is None:
            return list(chunk.turns)
        own = set(chunk.turn_ids)
        return [t for t in self._turns[max(0, i - n) : i + n + 1] if t.turn_id in own or t.turn_id not in exclude]

    def _render(self, chunk: Chunk, score: float | None, note: str = "", exclude: set[str] | frozenset[str] = frozenset()) -> str:
        turns = self._with_neighbors(chunk, exclude)
        ids = " ".join(t.turn_id for t in turns)
        if self.config.compact_headers:
            head = f"[turns: {ids}" + (f" | {note}]" if note else "]")
        else:
            head = f"[chunk {chunk.chunk_id} | {chunk.granularity} | turns: {ids}"
            head += f" | score {score:.2f}" if score is not None else ""
            head += f" | {note}]" if note else "]"
        body = "\n".join(t.render() for t in turns) if len(turns) != len(chunk.turns) else chunk.text
        if chunk.superseded_by:
            body += (
                f"\n[!] stale: superseded by {chunk.superseded_by} "
                f"({chunk.verifier}, confidence {chunk.confidence:.2f}) - prefer the newer chunk"
            )
        return head + "\n" + body

    def build_context(self, signal: TurnSignal, query: str) -> StrategyModuleOutput:
        t0 = time.perf_counter()
        budget = signal.token_usage.budget
        top_k = self.config.top_k
        if self._reranker is not None and signal.task_type not in self.config.rerank_skip_task_types:
            cands = self._candidates(query, max(top_k * 3, self.config.rerank_candidates))
            rel = self._reranker.score(query, [c.text for c, _ in cands])
            results = sorted(((c, r) for (c, _), r in zip(cands, rel)), key=lambda x: -x[1])
            floor = 0.0  # the bi-encoder floor was applied before reranking
        elif self._lexical is not None:
            results = self._candidates(query, max(top_k * 3, self.config.rerank_candidates))
            floor = float("-inf")  # fused scores are rank-based; the dense floor was applied above
        else:
            results = self.search(query, top_k * 3)
            floor = self.config.min_score
        if self.config.mmr_lambda is not None:
            results = self._mmr(results, self.config.mmr_lambda)
        picked: list[tuple[Chunk, str]] = []
        covered: set[str] = set()
        picked_ids: set[str] = set()
        used = 0
        sep = count_tokens(CONTEXT_BLOCK_SEPARATOR)
        for chunk, score in results:
            if len(picked) >= top_k:
                break
            if score < floor:
                break
            if chunk.chunk_id in picked_ids or set(chunk.turn_ids) <= covered:
                continue  # already shown, e.g. as a neighbour of an earlier hit
            block = self._render(chunk, score, exclude=covered)
            tok = count_tokens(block) + sep
            if used + tok > budget:
                continue
            picked.append((chunk, block))
            picked_ids.add(chunk.chunk_id)
            covered.update(t.turn_id for t in self._with_neighbors(chunk, covered))
            used += tok
            if chunk.superseded_by:
                newer = self.chunks.get(self.resolve(chunk.superseded_by))
                if newer is not None and newer.active and newer.chunk_id not in picked_ids:
                    nblock = self._render(newer, None, note=f"supersedes {chunk.chunk_id}")
                    ntok = count_tokens(nblock) + sep
                    if used + ntok <= budget:
                        picked.append((newer, nblock))
                        picked_ids.add(newer.chunk_id)
                        used += ntok

        context = CONTEXT_BLOCK_SEPARATOR.join(b for _, b in picked)
        chunks = [c for c, _ in picked]
        grans = Counter(c.granularity for c in chunks)
        tag = "segment" if grans["segment"] >= grans["turn"] and grans["segment"] > 0 else "turn"
        flags = [
            ContradictionFlag(chunk_id=c.chunk_id, nli_confidence=round(c.confidence, 4), superseded_by=self.resolve(c.superseded_by))
            for c in chunks
            if c.superseded_by
        ]
        elapsed = (time.perf_counter() - t0) * 1000
        self._latency_ema_ms = 0.8 * self._latency_ema_ms + 0.2 * elapsed
        return StrategyModuleOutput(
            module="rag",
            candidate_context=context,
            readiness=Readiness(available=self.index.ntotal > 0, estimated_latency_ms=round(self._latency_ema_ms, 3)),
            quality=RagQuality(granularity_tag=tag, retrieved_chunk_ids=[c.chunk_id for c in chunks], contradiction_flags=flags),
            token_count=count_tokens(context),
        )
