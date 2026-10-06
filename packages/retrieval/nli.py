"""Pretrained NLI scorer (no fine-tuning) for the contradiction stage."""

from __future__ import annotations

import os
import threading
from typing import Protocol

import numpy as np

DEFAULT_NLI_MODEL = os.environ.get("CEAI_NLI_MODEL", "cross-encoder/nli-deberta-v3-base")


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


class NLIScorer(Protocol):
    def contradiction_prob(self, pairs: list[tuple[str, str]]) -> list[float]:
        """P(contradiction) for each (premise, hypothesis) pair."""


class CrossEncoderNLI:
    def __init__(self, model_name: str = DEFAULT_NLI_MODEL, batch_size: int = 16):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None
        self._idx: int | None = None
        self._lock = threading.Lock()
        self.calls = 0

    def _load(self):
        with self._lock:
            if self._model is None:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self.model_name, device=_device())
                labels = {int(k): v.lower() for k, v in self._model.config.id2label.items()}
                self._idx = next(i for i, v in labels.items() if v.startswith("contra"))
        return self._model

    def contradiction_prob(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        model = self._load()
        with self._lock:
            logits = np.asarray(model.predict(pairs, batch_size=self.batch_size, show_progress_bar=False), dtype=np.float64)
        self.calls += len(pairs)
        logits = logits - logits.max(axis=1, keepdims=True)
        probs = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
        return [float(p) for p in probs[:, self._idx]]
