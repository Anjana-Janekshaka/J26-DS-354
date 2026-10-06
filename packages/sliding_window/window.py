"""Dynamic Sliding Window (DSW): composite-scored, budget-bounded short-term memory selector.

composite = w_r * relevance + w_f * freshness + w_i * importance + w_s * state   (weights normalized)

Selection is binary include/exclude: the most recent ``min_recent_turns`` are pinned, then turns
are added in descending composite order while they clear ``include_threshold`` and fit the token
budget. The selected turns are restored to chronological order before being returned.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np

from contracts import (
    CompositeScores,
    ConversationTurn,
    Readiness,
    SlidingWindowQuality,
    StrategyModuleOutput,
    TurnSignal,
    count_tokens,
)
from contracts.text import Embedder, HashingEmbedder

from .config import SlidingWindowConfig, Weights
from .scoring import freshness, importance, relevance, state_alignment


@dataclass
class ScoredTurn:
    turn: ConversationTurn
    relevance: float
    freshness: float
    importance: float
    state: float
    composite: float
    tokens: int


class DynamicSlidingWindow:
    name = "sliding_window"

    def __init__(self, embedder: Embedder | None = None, config: SlidingWindowConfig | None = None):
        self.embedder = embedder or HashingEmbedder()
        self.config = config or SlidingWindowConfig.from_env()
        self.turns: list[ConversationTurn] = []
        self._vecs: list[np.ndarray] = []
        self._importance: list[float] = []
        self._tokens: list[int] = []
        self._segment_of: dict[str, int] = {}
        self._segment = 0
        self._latency_ema_ms = 1.0

    # ------------------------------------------------------------------ runtime config
    def set_weights(self, weights: Weights | dict | str) -> None:
        if isinstance(weights, str):
            weights = Weights.parse(weights)
        elif isinstance(weights, dict):
            weights = Weights(**weights)
        self.config.weights = weights

    # ------------------------------------------------------------------ StrategyModule
    def observe_signal(self, signal: TurnSignal) -> None:
        if signal.shift_detected:
            self._segment += 1
        self._segment_of[signal.turn_id] = self._segment

    def ingest(self, turn: ConversationTurn) -> None:
        self.turns.append(turn)
        self._vecs.append(self.embedder.encode([turn.content])[0])
        self._importance.append(importance(turn.content))
        self._tokens.append(count_tokens(turn.render()))
        self._segment_of.setdefault(turn.turn_id, self._segment)

    def score(self, signal: TurnSignal, query: str) -> list[ScoredTurn]:
        n = len(self.turns)
        if n == 0:
            return []
        cfg = self.config
        qv = self.embedder.encode([query])[0]
        rel = relevance(qv, np.stack(self._vecs))
        age = np.arange(n - 1, -1, -1, dtype=np.float32)
        fre = freshness(age, cfg.freshness_half_life_turns)
        imp = np.asarray(self._importance, dtype=np.float32)
        segs = np.asarray([self._segment_of.get(t.turn_id, 0) for t in self.turns])
        current = self._segment_of.get(signal.turn_id, self._segment)
        sta = state_alignment(segs, current, cfg.state_decay)
        wr, wf, wi, ws = cfg.weights.normalized()
        comp = np.clip(wr * rel + wf * fre + wi * imp + ws * sta, 0.0, 1.0)
        return [
            ScoredTurn(self.turns[i], float(rel[i]), float(fre[i]), float(imp[i]), float(sta[i]), float(comp[i]), self._tokens[i])
            for i in range(n)
        ]

    def select(self, scored: list[ScoredTurn], budget: int) -> list[ScoredTurn]:
        chosen: dict[int, ScoredTurn] = {}
        used = 0
        n = len(scored)
        for i in range(n - 1, max(-1, n - 1 - self.config.min_recent_turns), -1):
            if used + scored[i].tokens <= budget:
                chosen[i] = scored[i]
                used += scored[i].tokens
        for i in sorted(range(n), key=lambda k: scored[k].composite, reverse=True):
            if i in chosen:
                continue
            if scored[i].composite < self.config.include_threshold:
                break
            if used + scored[i].tokens <= budget:
                chosen[i] = scored[i]
                used += scored[i].tokens
        return [chosen[i] for i in sorted(chosen)]  # chronological restore

    def build_context(self, signal: TurnSignal, query: str) -> StrategyModuleOutput:
        t0 = time.perf_counter()
        scored = self.score(signal, query)
        selected = self.select(scored, signal.token_usage.budget)
        if selected:
            means = {
                k: float(np.mean([getattr(s, k) for s in selected]))
                for k in ("relevance", "freshness", "importance", "state", "composite")
            }
        else:
            means = dict.fromkeys(("relevance", "freshness", "importance", "state", "composite"), 0.0)
        elapsed = (time.perf_counter() - t0) * 1000
        self._latency_ema_ms = 0.8 * self._latency_ema_ms + 0.2 * elapsed
        return StrategyModuleOutput(
            module="sliding_window",
            candidate_context=[s.turn for s in selected],
            readiness=Readiness(available=True, estimated_latency_ms=round(self._latency_ema_ms, 3)),
            quality=SlidingWindowQuality(
                selected_turn_ids=[s.turn.turn_id for s in selected],
                scores=CompositeScores(**{k: round(min(1.0, max(0.0, v)), 4) for k, v in means.items()}),
            ),
            token_count=sum(s.tokens for s in selected),
        )
