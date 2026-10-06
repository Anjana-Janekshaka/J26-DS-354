"""FAISS inner-product index (IndexFlatIP) with stable integer ids and removal support."""

from __future__ import annotations

import numpy as np

try:
    import faiss  # type: ignore

    HAVE_FAISS = True
except Exception:  # pragma: no cover - depends on environment
    faiss = None
    HAVE_FAISS = False


class VectorIndex:
    """Exact cosine search over L2-normalized vectors (IndexIDMap2 over IndexFlatIP)."""

    def __init__(self, dim: int):
        self.dim = dim
        if not HAVE_FAISS:
            raise ImportError("faiss-cpu is required for the retrieval index (pip install faiss-cpu)")
        self._index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))

    @property
    def ntotal(self) -> int:
        return int(self._index.ntotal)

    def add(self, ids: list[int], vecs: np.ndarray) -> None:
        if not ids:
            return
        self._index.add_with_ids(np.ascontiguousarray(vecs, dtype=np.float32), np.asarray(ids, dtype=np.int64))

    def remove(self, ids: list[int]) -> None:
        if ids:
            self._index.remove_ids(np.asarray(ids, dtype=np.int64))

    def search(self, vec: np.ndarray, k: int) -> list[tuple[int, float]]:
        if self.ntotal == 0 or k <= 0:
            return []
        scores, ids = self._index.search(np.ascontiguousarray(vec.reshape(1, -1), dtype=np.float32), min(k, self.ntotal))
        return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]

    def reconstruct(self, i: int) -> np.ndarray:
        return self._index.reconstruct(int(i))
