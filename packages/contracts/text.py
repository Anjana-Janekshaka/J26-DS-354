"""Shared text conventions and the embedding interface.

These define *one* vocabulary for what counts as an identifier, a content word and a code
signature, so the conversation manager, the three strategy modules and the evaluators measure
the same thing. ``HashingEmbedder`` is a dependency-free reference implementation of the
``Embedder`` protocol used as a test double and as an offline fallback; production wiring injects
a sentence-transformer embedder (see ``retrieval.embedder``).
"""

from __future__ import annotations

import ast
import hashlib
import re
from typing import Iterable, Protocol, runtime_checkable

import numpy as np

STOPWORDS = frozenset(
    """a an the and or but if then else of to in on at for from by with without about into over
    under is are was were be been being am do does did doing have has had having i me my mine we
    us our ours you your yours he him his she her hers it its they them their theirs this that
    these those there here what which who whom whose when where why how all any both each few
    more most other some such no nor not only own same so than too very can will just should
    would could may might must shall also as up down out off again further once s t don now
    let lets ok okay yeah yes hey hi oh well really like get got go going one thing things
    """.split()
)

# Separator between independently rankable blocks inside a string ``candidate_context`` (RAG
# chunks). Block headers carry ``turns: t0001 t0002 ...`` so assemblers can de-duplicate.
CONTEXT_BLOCK_SEPARATOR = "\n\n---\n\n"
BLOCK_TURNS = re.compile(r"turns: ((?:t\d+ ?)+)")

_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?")
_IDENT = re.compile(
    r"\b(?:[a-z]+(?:_[a-z0-9]+)+|[a-z]+[A-Z][A-Za-z0-9]*|[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+"
    r"|[A-Za-z_]\w*\.\w+(?:\.\w+)*)\b"
)
_CALL = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
_CODE_FENCE = re.compile(r"```[a-zA-Z0-9_+-]*\n(.*?)```", re.S)
_DEF_LINE = re.compile(
    r"^[ \t]*(?:async[ \t]+)?def[ \t]+([A-Za-z_]\w*)[ \t]*\(([^)]*)\)[ \t]*(?:->[ \t]*([^:]+))?:", re.M
)
_CLASS_LINE = re.compile(r"^[ \t]*class[ \t]+([A-Za-z_]\w*)[ \t]*(\([^)]*\))?[ \t]*:", re.M)
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'`])|\n+")


def words(text: str) -> list[str]:
    return [w.lower() for w in _WORD.findall(text)]


def content_words(text: str) -> list[str]:
    return [w for w in words(text) if w not in STOPWORDS and len(w) > 1]


def identifiers(text: str) -> set[str]:
    """Code-like identifiers: snake_case, camelCase, PascalCase compounds, dotted paths, calls."""
    found = set(_IDENT.findall(text))
    found.update(m for m in _CALL.findall(text) if len(m) > 2 and m.lower() not in STOPWORDS)
    return found


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text) if s and s.strip()]


def code_blocks(text: str) -> list[str]:
    return _CODE_FENCE.findall(text)


def strip_code(text: str) -> str:
    return _CODE_FENCE.sub(" ", text)


def has_code(text: str) -> bool:
    return bool(code_blocks(text) or _DEF_LINE.search(text) or _CLASS_LINE.search(text))


def code_signatures(text: str) -> dict[str, str]:
    """Map ``func:<name>`` / ``class:<name>`` to the exact normalized signature line.

    Parses fenced code with ``ast`` when possible (exact, comment-insensitive); falls back to a
    line regex for fragments that do not parse. Later definitions of the same name win.
    """
    sigs: dict[str, str] = {}
    sources = code_blocks(text) or ([text] if (_DEF_LINE.search(text) or _CLASS_LINE.search(text)) else [])
    for src in sources:
        try:
            tree = ast.parse(src)
        except SyntaxError:
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
                    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                    sigs[f"func:{node.name}"] = f"{prefix} {node.name}({ast.unparse(node.args)}){ret}"
                elif isinstance(node, ast.ClassDef):
                    bases = ", ".join(ast.unparse(b) for b in node.bases)
                    sigs[f"class:{node.name}"] = f"class {node.name}({bases})" if bases else f"class {node.name}"
        else:
            for name, args, ret in _DEF_LINE.findall(src):
                args = re.sub(r"\s+", " ", args.strip())
                sigs[f"func:{name}"] = f"def {name}({args})" + (f" -> {ret.strip()}" if ret.strip() else "")
            for name, bases in _CLASS_LINE.findall(src):
                b = bases.strip("() ")
                sigs[f"class:{name}"] = f"class {name}({b})" if b else f"class {name}"
    return sigs


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


@runtime_checkable
class Embedder(Protocol):
    """Maps texts to L2-normalized float32 vectors (so inner product == cosine)."""

    dim: int

    def encode(self, texts: list[str]) -> np.ndarray: ...


class HashingEmbedder:
    """Deterministic bag-of-content-words embedder (feature hashing + L2 norm). No model needed."""

    def __init__(self, dim: int = 512):
        self.dim = dim

    def _vec(self, text: str) -> np.ndarray:
        v = np.zeros(self.dim, dtype=np.float32)
        toks = content_words(text)
        for tok in toks + [f"{a}_{b}" for a, b in zip(toks, toks[1:])]:
            h = int.from_bytes(hashlib.blake2b(tok.encode(), digest_size=8).digest(), "little")
            v[h % self.dim] += 1.0 if (h >> 63) & 1 else -1.0
        n = np.linalg.norm(v)
        return v / n if n > 0 else v

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.stack([self._vec(t) for t in texts]).astype(np.float32)


class CachingEmbedder:
    """Wraps any embedder with a text->vector cache so shared texts are encoded once."""

    def __init__(self, inner: Embedder, max_items: int = 200_000):
        self.inner = inner
        self.dim = inner.dim
        self._cache: dict[str, np.ndarray] = {}
        self._max = max_items

    def encode(self, texts: list[str]) -> np.ndarray:
        missing = list(dict.fromkeys(t for t in texts if t not in self._cache))
        if missing:
            vecs = self.inner.encode(missing)
            if len(self._cache) + len(missing) > self._max:
                self._cache.clear()
            for t, v in zip(missing, vecs):
                self._cache[t] = v
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.stack([self._cache[t] for t in texts]).astype(np.float32)


def cosine_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine between rows, assuming both inputs are already L2-normalized."""
    if a.size == 0 or b.size == 0:
        return np.zeros((a.shape[0], b.shape[0]), dtype=np.float32)
    return a @ b.T


def unique(seq: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(seq))
