"""Baselines the DSW is benchmarked against (build guide 6.2).

* ``RecencyOnlyWindow``  - the last ``k`` turns, regardless of content (a fixed k-turn window).
* ``FixedTokenWindow``   - the most recent turns that fit the token budget.

Both return a contract-shaped ``StrategyModuleOutput`` so they plug into the same harnesses.
"""

from __future__ import annotations

import time

from contracts import (
    CompositeScores,
    ConversationTurn,
    Readiness,
    SlidingWindowQuality,
    StrategyModuleOutput,
    TurnSignal,
    count_tokens,
)


class _RecencyBase:
    name = "sliding_window"

    def __init__(self) -> None:
        self.turns: list[ConversationTurn] = []
        self._tokens: list[int] = []

    def observe_signal(self, signal: TurnSignal) -> None:
        pass

    def ingest(self, turn: ConversationTurn) -> None:
        self.turns.append(turn)
        self._tokens.append(count_tokens(turn.render()))

    def _pick(self, budget: int) -> list[int]:
        raise NotImplementedError

    def build_context(self, signal: TurnSignal, query: str) -> StrategyModuleOutput:
        t0 = time.perf_counter()
        idx = self._pick(signal.token_usage.budget)
        turns = [self.turns[i] for i in idx]
        n = len(self.turns)
        fresh = [0.5 ** ((n - 1 - i) / 8.0) for i in idx]
        return StrategyModuleOutput(
            module="sliding_window",
            candidate_context=turns,
            readiness=Readiness(available=True, estimated_latency_ms=(time.perf_counter() - t0) * 1000),
            quality=SlidingWindowQuality(
                selected_turn_ids=[t.turn_id for t in turns],
                scores=CompositeScores(
                    relevance=0.0,
                    freshness=round(sum(fresh) / len(fresh), 4) if fresh else 0.0,
                    importance=0.0,
                    state=0.0,
                    composite=0.0,
                ),
            ),
            token_count=sum(self._tokens[i] for i in idx),
        )


class RecencyOnlyWindow(_RecencyBase):
    """Last ``k`` turns (dropping the oldest of them if they overflow the budget)."""

    def __init__(self, k: int = 6) -> None:
        super().__init__()
        self.k = k

    def _pick(self, budget: int) -> list[int]:
        idx = list(range(max(0, len(self.turns) - self.k), len(self.turns)))
        while idx and sum(self._tokens[i] for i in idx) > budget:
            idx.pop(0)
        return idx


class FixedTokenWindow(_RecencyBase):
    """Most recent turns that fit the token budget."""

    def _pick(self, budget: int) -> list[int]:
        idx: list[int] = []
        used = 0
        for i in range(len(self.turns) - 1, -1, -1):
            if used + self._tokens[i] > budget:
                break
            idx.append(i)
            used += self._tokens[i]
        return sorted(idx)
