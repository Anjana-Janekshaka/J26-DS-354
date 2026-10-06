"""Information-loss score (Method 1: anchor recall) and Symbol Retention Rate.

Method 1 - anchor recall. Anchors are the checkable atoms of the summarized source turns:
identifiers, exact code signatures, numbers/dates, proper nouns and quoted strings. The loss score
is the fraction of those anchors that do not appear in the emitted summary text:

    loss = 1 - |anchors found in summary| / |anchors in summarized turns|

It is a *live* control signal: it is computed every time a summary is emitted and, when it exceeds
``LOSS_THRESHOLD`` (0.15), raises an escalation the controller consumes on the next turn (sec. 5).

The scorer runs on a background worker so that a more expensive scorer (Method 2, QA consistency,
``# TODO: v2``) can be dropped in without touching the turn's critical path.
"""

from __future__ import annotations

import re
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Iterable

from contracts import ConversationTurn
from contracts.text import code_signatures, identifiers, normalize, strip_code

_PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]{2,}(?: [A-Z][a-z]{2,})*)\b")
_NUMBER = re.compile(r"\b\d[\d,.:/-]*\d\b|\b\d{2,}\b")
_QUOTED = re.compile(r"[\"'`]([^\"'`\n]{3,40})[\"'`]")
_IGNORE = {"The", "This", "That", "And", "But", "Yes", "Yeah", "Sure", "Thanks", "Okay", "Hey"}


def anchors(turns: Iterable[ConversationTurn]) -> set[str]:
    out: set[str] = set()
    for t in turns:
        text = t.content
        out.update(code_signatures(text).values())
        # Code bodies contribute only their exact signatures; identifiers count from prose.
        prose = strip_code(text)
        out.update(identifiers(prose))
        out.update(p for p in _PROPER.findall(prose) if p not in _IGNORE)
        out.update(_NUMBER.findall(prose))
        out.update(q.strip() for q in _QUOTED.findall(prose))
    return {a for a in out if len(a) >= 2}


def anchor_loss(source_turns: list[ConversationTurn], summary_text: str) -> tuple[float, int, int]:
    """Return (loss_score, anchors_found, anchors_total)."""
    found_in = normalize(summary_text)
    anc = anchors(source_turns)
    if not anc:
        return 0.0, 0, 0
    hit = sum(1 for a in anc if normalize(a) in found_in)
    return 1.0 - hit / len(anc), hit, len(anc)


def current_signatures(turns: Iterable[ConversationTurn]) -> dict[str, str]:
    """Ground-truth latest signature per symbol across the raw history (later definitions win)."""
    sigs: dict[str, str] = {}
    for t in turns:
        sigs.update(code_signatures(t.content))
    return sigs


def symbol_retention_rate(turns: list[ConversationTurn], context_text: str) -> float | None:
    """Fraction of current exact signatures present verbatim in ``context_text``; None if no code."""
    sigs = current_signatures(turns)
    if not sigs:
        return None
    ctx = normalize(context_text)
    return sum(1 for s in sigs.values() if normalize(s) in ctx) / len(sigs)


class LossWorker:
    """Background scorer. ``submit`` returns a Future; late results are delivered via ``on_late``."""

    def __init__(self, scorer: Callable[[list[ConversationTurn], str], tuple[float, int, int]] = anchor_loss):
        self._scorer = scorer
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="loss-worker")
        self._lock = threading.Lock()
        self.last_score: float | None = None

    def submit(self, source_turns: list[ConversationTurn], summary_text: str) -> Future:
        fut = self._pool.submit(self._scorer, list(source_turns), summary_text)

        def _remember(f: Future) -> None:
            if not f.exception():
                with self._lock:
                    self.last_score = f.result()[0]

        fut.add_done_callback(_remember)
        return fut

    def shutdown(self) -> None:
        self._pool.shutdown(wait=False)
