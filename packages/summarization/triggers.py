"""Semantic-drift trigger for token-driven summarization.

``DriftMonitor`` embeds the buffered turns (embeddings cached per turn id) and reports drift when
the newest turn is less similar to the centroid of the earlier buffered turns than ``threshold``.
The embedding function is injected (``embed(list[str]) -> vectors``) so this package never imports
another package's encoder; integration can pass the same instance retrieval uses.
"""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np

from contracts import ConversationTurn

EmbedFn = Callable[[list[str]], Sequence[Sequence[float]]]


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    return float(np.dot(a, b) / (na * nb)) if na and nb else 0.0


class DriftMonitor:
    def __init__(self, embed: EmbedFn, threshold: float):
        self._embed = embed
        self.threshold = threshold
        self._cache: dict[str, np.ndarray] = {}

    def _vectors(self, turns: list[ConversationTurn]) -> list[np.ndarray]:
        missing = [t for t in turns if t.turn_id not in self._cache]
        if missing:
            for t, v in zip(missing, self._embed([t.render() for t in missing])):
                self._cache[t.turn_id] = np.asarray(v, dtype=float)
        return [self._cache[t.turn_id] for t in turns]

    def similarity_to_buffer(self, turns: list[ConversationTurn]) -> float | None:
        """Cosine of the newest turn against the centroid of the earlier ones (None if < 2 turns)."""
        if len(turns) < 2:
            return None
        vecs = self._vectors(turns)
        return cosine(vecs[-1], np.mean(vecs[:-1], axis=0))

    def drifted(self, turns: list[ConversationTurn]) -> bool:
        sim = self.similarity_to_buffer(turns)
        return sim is not None and sim < self.threshold
