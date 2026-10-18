"""Two-stage contradiction / staleness check, run at write time on each new chunk.

Stage 1 - cheap prefilter (no model): candidate (older, newer) pairs where the older chunk is
  topically close (cosine >= ``topic_threshold``, top ``max_candidates`` by similarity) or defines
  the same code symbol. Within each candidate pair, only the most similar sentence pairs
  (cosine >= ``sentence_threshold``) go forward, so the verifier sees focused claims.
Stage 2 - verification:
  * prose: pretrained NLI cross-encoder. Score = min(P(contra | newer => older), P(contra | older => newer)),
    flagged when >= ``nli_threshold``. Requiring both directions is deliberate: a real supersession
    ("I live in London" / "I moved to Paris") contradicts symmetrically, while the NLI model's
    one-directional "contradictions" on dialogue are mostly non-entailment noise (measured on the
    demo session: 3 of 6 one-directional flags were false positives, all removed by this rule);
  * code symbols: exact signature comparison (AST-normalized). The NLI model cannot tell
    identifiers apart (measured: ``create_task(title, due)`` vs ``create_task(title, due_date)``
    scores 0.00 contradiction), so a changed signature for the same symbol is verified
    structurally and reported with confidence 1.0, ``verifier='signature_diff'``.

Only the older chunk is flagged, ``superseded_by`` the newer one. Nothing is deleted.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

import numpy as np

from contracts.text import Embedder, content_words, normalize, sentences, strip_code

from .nli import NLIScorer


@dataclass
class ContradictionConfig:
    topic_threshold: float = 0.25
    sentence_threshold: float = 0.30
    max_candidates: int = 4
    max_sentence_pairs: int = 3
    nli_threshold: float = 0.95  # selected on the dev split of eval/synthetic/retrieval (max F1)
    bidirectional: bool = True
    min_content_words: int = 3
    # v4 option (docs/v4_preregistration.md section 2; off in the frozen system): score NLI-verified
    # chunks with a logistic regression over (min-direction NLI, max-direction NLI, chunk cosine,
    # change cue in the newer text), weights fitted on the dev contradiction pairs.
    ensemble: tuple[float, float, float, float, float] | None = None  # (intercept, w_min, w_max, w_cos, w_cue)
    ensemble_threshold: float = 0.5


@dataclass
class Verdict:
    older_id: str
    newer_id: str
    confidence: float
    verifier: str  # "nli" | "signature_diff"
    evidence: tuple[str, str]


CHANGE_CUE = re.compile(r"\b(moved|now|no longer|anymore|any more|switched|changed|left|quit|instead|these days|used to|"
                        r"not anymore|stopped|started|new)\b", re.I)
_ROLE_PREFIX = re.compile(r"^(?:\[[^\]]*\]\s*)?[\w .'-]{1,40}:\s+", re.M)
_REQUEST = re.compile(
    r"^(?:please |can you |could you |let'?s |now |also |next,? )?(?:add|write|create|make|build|implement|update|configure|set up|"
    r"fix|rename|refactor|walk me|show|explain|use|switch|move|remove|delete|run|call|debug)\b",
    re.I,
)


def _claims(text: str) -> list[str]:
    """Declarative sentences only: no questions, no imperative requests, no speaker prefixes."""
    out = []
    for s in sentences(strip_code(text)):
        s = _ROLE_PREFIX.sub("", s, count=1).strip()
        if len(content_words(s)) >= 2 and not s.endswith("?") and not _REQUEST.match(s):
            out.append(s)
    return out


class ContradictionChecker:
    def __init__(self, embedder: Embedder, nli: NLIScorer | None, config: ContradictionConfig | None = None):
        self.embedder = embedder
        self.nli = nli
        self.config = config or ContradictionConfig()
        self.pairs_prefiltered = 0
        self.pairs_verified = 0

    def check(
        self,
        new_id: str,
        new_text: str,
        new_vec: np.ndarray,
        new_symbols: dict[str, str],
        older: list[tuple[str, str, np.ndarray, dict[str, str]]],
        return_all: bool = False,
    ) -> list[Verdict]:
        """``older`` is a list of (chunk_id, text, vec, symbols) for active, older chunks.

        ``return_all=True`` (evaluation) returns the best raw NLI score for every pair that survived
        the prefilter, ignoring ``nli_threshold``, so thresholds can be swept and calibrated."""
        cfg = self.config
        verdicts: list[Verdict] = []
        if not older:
            return verdicts

        # ---- code symbols: same symbol, different exact signature -> superseded
        if new_symbols:
            for cid, _text, _vec, syms in older:
                for key, sig in new_symbols.items():
                    if key in syms and normalize(syms[key]) != normalize(sig):
                        verdicts.append(Verdict(cid, new_id, 1.0, "signature_diff", (sig, syms[key])))
                        break

        # ---- prose: stage 1 prefilter
        if self.nli is None or len(content_words(strip_code(new_text))) < cfg.min_content_words:
            return verdicts
        new_claims = _claims(new_text)
        if not new_claims:
            return verdicts
        flagged = {v.older_id for v in verdicts}
        sims = np.asarray([float(vec @ new_vec) for _, _, vec, _ in older])
        order = [i for i in np.argsort(-sims) if sims[i] >= cfg.topic_threshold][: cfg.max_candidates]
        new_claim_vecs = self.embedder.encode(new_claims)
        batch: list[tuple[str, str]] = []
        owners: list[str] = []
        for i in order:
            cid, text, _vec, _ = older[i]
            if cid in flagged:
                continue
            old_claims = _claims(text)
            if not old_claims:
                continue
            self.pairs_prefiltered += 1
            sim = new_claim_vecs @ self.embedder.encode(old_claims).T
            flat = np.argsort(-sim, axis=None)[: cfg.max_sentence_pairs]
            for f in flat:
                a, b = np.unravel_index(f, sim.shape)
                if sim[a, b] < cfg.sentence_threshold:
                    break
                batch.append((new_claims[a], old_claims[b]))
                owners.append(cid)

        # ---- stage 2: NLI on the surviving sentence pairs
        if batch:
            probs = self.nli.contradiction_prob(batch)
            rev = self.nli.contradiction_prob([(b, a) for a, b in batch]) if (cfg.bidirectional or cfg.ensemble) else probs
            self.pairs_verified += len(batch)
            if cfg.ensemble is not None:
                return verdicts + self._ensemble(new_id, owners, batch, probs, rev, sims, older, new_text, return_all)
            if cfg.bidirectional:
                probs = [min(p, r) for p, r in zip(probs, rev)]
            best: dict[str, tuple[float, tuple[str, str]]] = {}
            floor = -1.0 if return_all else cfg.nli_threshold
            for cid, p, pair in zip(owners, probs, batch):
                if p >= floor and p > best.get(cid, (-1.0, pair))[0]:
                    best[cid] = (p, pair)
            for cid, (p, pair) in best.items():
                verdicts.append(Verdict(cid, new_id, p, "nli", pair))
        return verdicts

    def _ensemble(self, new_id, owners, batch, fwd, rev, sims, older, new_text, return_all) -> list[Verdict]:
        b, w_min, w_max, w_cos, w_cue = self.config.ensemble
        cue = float(bool(CHANGE_CUE.search(new_text)))
        cos_of = {cid: float(sims[i]) for i, (cid, *_rest) in enumerate(older)}
        agg: dict[str, list] = {}
        for cid, f, r, pair in zip(owners, fwd, rev, batch):
            lo, hi, best_pair = agg.get(cid, (-1.0, -1.0, pair))
            agg[cid] = (max(lo, min(f, r)), max(hi, f, r), pair if min(f, r) > lo else best_pair)
        out = []
        for cid, (lo, hi, pair) in agg.items():
            p = 1.0 / (1.0 + math.exp(-(b + w_min * lo + w_max * hi + w_cos * cos_of[cid] + w_cue * cue)))
            if return_all or p >= self.config.ensemble_threshold:
                out.append(Verdict(cid, new_id, p, "nli_ensemble", pair))
        return out
