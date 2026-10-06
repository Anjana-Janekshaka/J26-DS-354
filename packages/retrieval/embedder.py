"""Sentence-transformer embedder (P0). Lazy-loads the model on first use."""

from __future__ import annotations

import os
import threading

import numpy as np

DEFAULT_MODEL = os.environ.get("CEAI_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def _device() -> str:
    """CEAI_TORCH_DEVICE if set, else CUDA when available (e.g. a Kaggle / Colab GPU), else CPU."""
    forced = os.environ.get("CEAI_TORCH_DEVICE")
    if forced:
        return forced
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:  # pragma: no cover
        return "cpu"


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = DEFAULT_MODEL, batch_size: int = 64):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None
        self._lock = threading.Lock()
        self._dim: int | None = None

    def _load(self):
        with self._lock:
            if self._model is None:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name, device=_device())
                getdim = getattr(self._model, "get_embedding_dimension", None) or self._model.get_sentence_embedding_dimension
                self._dim = int(getdim())
        return self._model

    @property
    def dim(self) -> int:  # type: ignore[override]
        if self._dim is None:
            self._load()
        return int(self._dim)  # type: ignore[arg-type]

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        model = self._load()
        with self._lock:
            vecs = model.encode(
                texts, batch_size=self.batch_size, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False
            )
        return vecs.astype(np.float32)
