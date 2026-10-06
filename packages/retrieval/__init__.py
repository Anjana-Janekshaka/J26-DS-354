"""Component 3: Retrieval (RAG) - FAISS + sentence embeddings, write-time adaptive granularity,
two-stage (prefilter -> NLI / signature-diff) contradiction and staleness flagging."""

from .chunking import BoundaryConfig, BoundaryDecision, decide_boundary
from .contradiction import ContradictionChecker, ContradictionConfig, Verdict
from .embedder import SentenceTransformerEmbedder
from .engine import Chunk, RetrievalConfig, RetrievalEngine
from .index import VectorIndex
from .nli import CrossEncoderNLI, NLIScorer

__all__ = [
    "BoundaryConfig",
    "BoundaryDecision",
    "Chunk",
    "ContradictionChecker",
    "ContradictionConfig",
    "CrossEncoderNLI",
    "NLIScorer",
    "RetrievalConfig",
    "RetrievalEngine",
    "SentenceTransformerEmbedder",
    "Verdict",
    "VectorIndex",
    "decide_boundary",
]
