"""Optional second-stage reranker for the read path.

FAISS returns candidates by bi-encoder cosine; a cross-encoder then scores each (query, chunk)
pair jointly, which is much better at deciding which turn actually answers the question. Loaded
lazily, and only when ``RetrievalConfig.reranker`` names a model.
"""

from __future__ import annotations

import threading
from typing import Protocol

import numpy as np

from .nli import _device

DEFAULT_RERANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker(Protocol):
    def score(self, query: str, passages: list[str]) -> list[float]:
        """Relevance in [0, 1] for each passage (higher = more relevant)."""


class CrossEncoderReranker:
    def __init__(self, model_name: str = DEFAULT_RERANKER, batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None
        self._lock = threading.Lock()
        self.calls = 0

    def _load(self):
        with self._lock:
            if self._model is None:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self.model_name, device=_device())
        return self._model

    def score(self, query: str, passages: list[str]) -> list[float]:
        if not passages:
            return []
        logits = np.asarray(self._load().predict([(query, p) for p in passages], batch_size=self.batch_size), dtype=np.float64)
        self.calls += len(passages)
        return (1.0 / (1.0 + np.exp(-logits.reshape(-1)))).tolist()
