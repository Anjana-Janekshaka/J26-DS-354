"""External memory baselines, run inside the Syno harness under identical conditions.

Settings are fixed in docs/baselines_protocol.md. Each system ingests a LoCoMo conversation once
(``ingest``), then returns a memory context for each question (``context``). Every system counts
the LLM calls it makes while storing (``write_llm_calls``).
"""

from __future__ import annotations

import os
import tempfile
import time
from dataclasses import dataclass

import numpy as np

from contracts import count_tokens


@dataclass
class Line:
    speaker: str
    text: str
    date: str
    session: int

    def render(self) -> str:  # identical to ConversationTurn.render() with date metadata
        return f"[{self.date}] {self.speaker}: {self.text}"


def fit_budget(blocks: list[str], budget: int, sep: str = "\n\n") -> str:
    """Keep blocks in the given order while they fit into ``budget`` tokens."""
    out, used = [], 0
    for b in blocks:
        t = count_tokens(b) + count_tokens(sep)
        if used + t > budget:
            continue
        out.append(b)
        used += t
    return sep.join(out)


class MemoryBaseline:
    name = "base"

    def __init__(self) -> None:
        self.write_llm_calls = 0
        self.ingest_seconds = 0.0

    def ingest(self, lines: list[Line]) -> None:
        raise NotImplementedError

    def context(self, question: str, budget: int) -> str:
        raise NotImplementedError


# --------------------------------------------------------------------------- fixed-chunk RAG
class FixedChunkRAG(MemoryBaseline):
    """The Mem0 paper's RAG baseline: fixed-size chunks of the whole conversation, cosine top-k."""

    name = "fixed_chunk_rag"

    def __init__(self, embedder, chunk_tokens: int = 256) -> None:
        super().__init__()
        self.embedder = embedder
        self.chunk_tokens = chunk_tokens
        self.chunks: list[str] = []
        self.vecs: np.ndarray | None = None

    def ingest(self, lines: list[Line]) -> None:
        t0 = time.time()
        cur, used = [], 0
        for ln in lines:
            r = ln.render()
            n = count_tokens(r) + 1
            if cur and used + n > self.chunk_tokens:
                self.chunks.append("\n".join(cur))
                cur, used = [], 0
            cur.append(r)
            used += n
        if cur:
            self.chunks.append("\n".join(cur))
        self.vecs = self.embedder.encode(self.chunks)
        self.ingest_seconds = time.time() - t0

    def context(self, question: str, budget: int) -> str:
        q = self.embedder.encode([question])[0]
        order = np.argsort(-(self.vecs @ q))
        return fit_budget([self.chunks[i] for i in order], budget)


# --------------------------------------------------------------------------- summary buffer
SUMMARY_SYSTEM = (
    "Progressively summarize the lines of conversation provided, adding onto the previous summary "
    "and returning a new summary. Keep names, dates, places, numbers and personal facts. "
    "Write at most 250 words."
)


class SummaryBuffer(MemoryBaseline):
    """LangChain ConversationSummaryBufferMemory approach (recent turns verbatim + running summary).

    Deviation (documented in the protocol): the buffer is pruned in batches, from ``max_tokens`` down
    to ``prune_to`` tokens, instead of one message at a time, to keep the number of LLM calls feasible.
    """

    name = "summary_buffer"

    def __init__(self, llm, max_tokens: int = 600, prune_to: int = 300) -> None:
        super().__init__()
        self.llm = llm
        self.max_tokens, self.prune_to = max_tokens, prune_to
        self.summary = ""
        self.buffer: list[str] = []

    def _buffer_tokens(self) -> int:
        return sum(count_tokens(b) + 1 for b in self.buffer)

    def ingest(self, lines: list[Line]) -> None:
        t0 = time.time()
        for ln in lines:
            self.buffer.append(ln.render())
            if self._buffer_tokens() > self.max_tokens:
                pruned = []
                while self.buffer and self._buffer_tokens() > self.prune_to:
                    pruned.append(self.buffer.pop(0))
                user = f"Current summary:\n{self.summary or '(empty)'}\n\nNew lines of conversation:\n" + "\n".join(pruned) + "\n\nNew summary:"
                self.summary = self.llm(SUMMARY_SYSTEM, user).strip()
                self.write_llm_calls += 1
        self.ingest_seconds = time.time() - t0

    def context(self, question: str, budget: int) -> str:
        recent = "[Recent turns]\n" + "\n".join(self.buffer)
        room = budget - count_tokens(recent) - 4
        summary = self.summary
        while summary and count_tokens(summary) > room:  # keep the buffer; trim the summary from the end
            summary = summary[: int(len(summary) * 0.9)]
        return (f"[Summary]\n{summary}\n\n" if summary else "") + recent


# --------------------------------------------------------------------------- full context
class FullContext(MemoryBaseline):
    name = "full_context"

    def __init__(self) -> None:
        super().__init__()
        self.text = ""

    def ingest(self, lines: list[Line]) -> None:
        self.text = "\n".join(ln.render() for ln in lines)

    def context(self, question: str, budget: int) -> str:
        return self.text  # no budget: this is the ceiling


# --------------------------------------------------------------------------- Mem0
class Mem0Baseline(MemoryBaseline):
    """The ``mem0ai`` open-source library with a local Ollama LLM, MiniLM embeddings and FAISS.

    One ``add()`` per session per speaker. Each speaker has their own memory scope, with their own
    turns as ``user`` and the other speaker as ``assistant``. Session dates are prefixed to messages.
    """

    name = "mem0"

    def __init__(self, conv_id: str, model: str, base_url: str, embed_model: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        super().__init__()
        os.environ.setdefault("MEM0_TELEMETRY", "False")
        from mem0 import Memory

        d = tempfile.mkdtemp(prefix=f"mem0-{conv_id}-")
        self.mem = Memory.from_config({
            "llm": {"provider": "ollama", "config": {"model": model, "ollama_base_url": base_url, "temperature": 0.0, "max_tokens": int(os.environ.get("CEAI_MEM0_MAX_TOKENS", "1500"))}},
            "embedder": {"provider": "huggingface", "config": {"model": embed_model, "embedding_dims": 384}},
            "vector_store": {"provider": "faiss", "config": {"collection_name": "mem", "path": os.path.join(d, "faiss"), "embedding_model_dims": 384}},
            "history_db_path": os.path.join(d, "history.db"),
        })
        inner = self.mem.llm.generate_response

        def counted(*a, **k):
            self.write_llm_calls += 1
            return inner(*a, **k)

        self.mem.llm.generate_response = counted
        self.conv_id = conv_id
        self.scopes: list[str] = []
        self.add_failures = 0

    def ingest(self, lines: list[Line]) -> None:
        t0 = time.time()
        speakers = list(dict.fromkeys(ln.speaker for ln in lines))
        self.scopes = [f"{self.conv_id}:{s}" for s in speakers]
        for s in sorted({ln.session for ln in lines}):
            sess = [ln for ln in lines if ln.session == s]
            for spk, scope in zip(speakers, self.scopes):
                msgs = [{"role": "user" if ln.speaker == spk else "assistant", "content": f"[{ln.date}] {ln.speaker}: {ln.text}"} for ln in sess]
                try:
                    self.mem.add(msgs, user_id=scope)
                except Exception:  # noqa: BLE001 - counted and reported, never hidden
                    self.add_failures += 1
        self.ingest_seconds = time.time() - t0

    def context(self, question: str, budget: int) -> str:
        hits = []
        for scope in self.scopes:
            res = self.mem.search(question, top_k=30, filters={"user_id": scope})
            items = res.get("results", res) if isinstance(res, dict) else res
            for it in items or []:
                hits.append((float(it.get("score") or 0.0), f"{scope.split(':', 1)[1]}: {it.get('memory', '')}"))
        hits.sort(key=lambda x: -x[0])
        return fit_budget([h for _, h in hits], budget, sep="\n")
