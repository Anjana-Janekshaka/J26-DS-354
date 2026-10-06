"""Write-time granularity decision: does the incoming turn continue the open segment or start a new one?

Boundary score (hand-set weights, documented; a learned version is future work):

    p_t = sigmoid(b + w_s * semantic_drop + w_l * length_pressure + w_n * turn_pressure + w_x * shift)

* semantic_drop   = 1 - cos(turn, centroid of open segment)
* length_pressure = tokens(open segment + turn) / max_segment_tokens
* turn_pressure   = turns(open segment) / max_segment_turns
* shift           = 1 if the conversation manager flagged ``shift_detected`` for this turn

A boundary is placed when ``p_t > 0.5``. Turns that define code symbols are always closed as their
own turn-level chunk (precise retrieval targets). A closed segment holding one turn is tagged
``turn``; otherwise ``segment``. ``mode='turn'`` / ``mode='segment'`` give the fixed baselines.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np

Mode = Literal["turn", "segment", "adaptive"]


@dataclass
class BoundaryConfig:
    bias: float = -3.6
    w_semantic: float = 4.0
    w_length: float = 3.5
    w_turns: float = 1.5
    w_shift: float = 4.0
    max_segment_tokens: int = 200
    max_segment_turns: int = 6
    fixed_segment_turns: int = 4


@dataclass
class BoundaryDecision:
    boundary: bool
    probability: float
    semantic_drop: float
    length_pressure: float
    turn_pressure: float
    shift: bool
    reason: str


def decide_boundary(
    mode: Mode,
    cfg: BoundaryConfig,
    open_vecs: list[np.ndarray],
    open_tokens: int,
    turn_vec: np.ndarray,
    turn_tokens: int,
    shift: bool,
    turn_defines_code: bool,
    open_defines_code: bool,
) -> BoundaryDecision:
    n = len(open_vecs)
    if n == 0:
        return BoundaryDecision(False, 0.0, 0.0, 0.0, 0.0, shift, "empty_segment")
    if mode == "turn":
        return BoundaryDecision(True, 1.0, 0.0, 0.0, 0.0, shift, "fixed_turn")
    if mode == "segment":
        b = n >= cfg.fixed_segment_turns
        return BoundaryDecision(b, float(b), 0.0, 0.0, 0.0, shift, "fixed_segment")

    centroid = np.mean(open_vecs, axis=0)
    norm = float(np.linalg.norm(centroid))
    cos = float(turn_vec @ centroid / norm) if norm > 0 else 0.0
    sem = 1.0 - max(-1.0, min(1.0, cos))
    lp = (open_tokens + turn_tokens) / cfg.max_segment_tokens
    tp = n / cfg.max_segment_turns
    if turn_defines_code or open_defines_code:
        return BoundaryDecision(True, 1.0, sem, lp, tp, shift, "code_definition_isolated")
    z = cfg.bias + cfg.w_semantic * sem + cfg.w_length * lp + cfg.w_turns * tp + cfg.w_shift * float(shift)
    p = 1.0 / (1.0 + math.exp(-z))
    return BoundaryDecision(p > 0.5, p, sem, lp, tp, shift, "boundary_score")
