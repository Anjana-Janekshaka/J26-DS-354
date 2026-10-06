"""Shared token counting so every module reports ``token_count`` on the same scale.

Uses tiktoken's ``cl100k_base`` when installed; otherwise a deterministic regex approximation
(word pieces + punctuation), which tracks BPE counts within roughly 10-20% on English and code.
"""

from __future__ import annotations

import re
from functools import lru_cache

_FALLBACK = re.compile(r"\w{1,4}|[^\w\s]")


@lru_cache(maxsize=1)
def _encoder():
    try:
        import tiktoken

        return tiktoken.get_encoding("cl100k_base")
    except Exception:  # pragma: no cover - depends on environment
        return None


def tokenizer_name() -> str:
    return "tiktoken/cl100k_base" if _encoder() is not None else "regex-approx"


@lru_cache(maxsize=65536)
def count_tokens(text: str) -> int:
    if not text:
        return 0
    enc = _encoder()
    if enc is not None:
        return len(enc.encode(text, disallowed_special=()))
    return len(_FALLBACK.findall(text))
