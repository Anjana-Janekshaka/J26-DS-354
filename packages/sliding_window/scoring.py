"""The four cheap, rule-based scoring factors for the Dynamic Sliding Window."""

from __future__ import annotations

import math
import re

import numpy as np

from contracts.text import code_signatures, has_code, identifiers

_DECISION = re.compile(
    r"\b(we decided|decided to|let'?s (go with|use|keep|switch)|we'?ll (use|go with|keep)|agreed|going with|"
    r"final(ly)? (answer|choice|decision)|settled on|the plan is)\b",
    re.I,
)
_CONSTRAINT = re.compile(
    r"\b(must|must not|never|always|don'?t|do not|required|requirement|should not|shouldn'?t|cannot|can'?t|"
    r"has to|have to|only use|no more than|at least|at most|deadline)\b",
    re.I,
)
_ERROR = re.compile(r"\b(traceback|error|exception|failed|failing|stack trace)\b", re.I)
_NUMBER = re.compile(r"\b\d[\d,.:/-]*\b")
_ACK = re.compile(r"^\s*(ok(ay)?|thanks?( you)?|thx|cool|great|nice|got it|sure|sounds good|perfect|yes|no|yep|nope)[.!\s]*$", re.I)


def importance(text: str) -> float:
    """Content importance in [0, 1] from structural cues (definitions, decisions, constraints...)."""
    if _ACK.match(text):
        return 0.0
    score = 0.0
    if code_signatures(text):
        score += 0.4
    elif has_code(text):
        score += 0.2
    if _DECISION.search(text):
        score += 0.25
    if _CONSTRAINT.search(text):
        score += 0.2
    if _ERROR.search(text):
        score += 0.15
    score += min(0.2, 0.05 * len(identifiers(text)))
    if _NUMBER.search(text):
        score += 0.1
    return float(min(1.0, score))


def freshness(age_turns: np.ndarray, half_life: float) -> np.ndarray:
    """Exponential recency decay: 1.0 for the newest turn, 0.5 after ``half_life`` turns."""
    return np.exp(-math.log(2) * age_turns / half_life)


def relevance(query_vec: np.ndarray, turn_vecs: np.ndarray) -> np.ndarray:
    """Cosine similarity to the current query, clipped to [0, 1]."""
    if turn_vecs.size == 0:
        return np.zeros(0, dtype=np.float32)
    return np.clip(turn_vecs @ query_vec, 0.0, 1.0)


def state_alignment(turn_segments: np.ndarray, current_segment: int, decay: float) -> np.ndarray:
    """1.0 for turns in the active conversation-state segment, ``decay**k`` for k segments back."""
    back = np.maximum(0, current_segment - turn_segments)
    return np.power(decay, back).astype(np.float32)
