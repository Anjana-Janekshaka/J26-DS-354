"""BM25 over the active chunks, kept incrementally (no extra dependency).

Dense embeddings blur exact tokens such as code identifiers (``get_user_tasks``), names and numbers;
a lexical index catches those. Fused with the dense ranking by reciprocal rank fusion
(``RetrievalConfig.hybrid``), following the dense + BM25 hybrids in DPR (Karpukhin et al., 2020)
and Zep (Rasmussen et al., 2025).
"""

from __future__ import annotations

import math
from collections import Counter

from contracts.text import STOPWORDS, identifiers, words


def lexical_terms(text: str) -> list[str]:
    """Lower-cased content words, plus each snake_case / dotted identifier split into its parts."""
    terms = [w for w in words(text) if w not in STOPWORDS and len(w) > 1]
    for ident in identifiers(text):
        terms += [p.lower() for p in ident.replace(".", "_").split("_") if len(p) > 1]
    return terms


class BM25Index:
    def __init__(self, k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs: dict[str, Counter] = {}
        self.lengths: dict[str, int] = {}
        self.df: Counter = Counter()
        self.total_len = 0

    def add(self, doc_id: str, text: str) -> None:
        if doc_id in self.docs:
            self.remove(doc_id)
        tf = Counter(lexical_terms(text))
        self.docs[doc_id] = tf
        self.lengths[doc_id] = sum(tf.values())
        self.total_len += self.lengths[doc_id]
        self.df.update(tf.keys())

    def remove(self, doc_id: str) -> None:
        tf = self.docs.pop(doc_id, None)
        if tf is None:
            return
        self.total_len -= self.lengths.pop(doc_id)
        self.df.subtract(tf.keys())

    def search(self, query: str, k: int) -> list[tuple[str, float]]:
        n = len(self.docs)
        if n == 0:
            return []
        avg = self.total_len / n or 1.0
        q = set(lexical_terms(query))
        scores: dict[str, float] = {}
        for term in q:
            df = self.df.get(term, 0)
            if df <= 0:
                continue
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            for doc_id, tf in self.docs.items():
                f = tf.get(term)
                if f:
                    norm = f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.lengths[doc_id] / avg))
                    scores[doc_id] = scores.get(doc_id, 0.0) + idf * norm
        return sorted(scores.items(), key=lambda x: -x[1])[:k]


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return fused
