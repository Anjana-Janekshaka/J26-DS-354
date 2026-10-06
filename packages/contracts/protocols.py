"""Interfaces every strategy module implements. Integration wires modules through these only."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .schemas import ConversationTurn, StrategyModuleOutput, StrategyName, TurnSignal


@runtime_checkable
class StrategyModule(Protocol):
    name: StrategyName

    def observe_signal(self, signal: TurnSignal) -> None:
        """Receive the per-turn broadcast (subscribed to the conversation manager's bus)."""

    def ingest(self, turn: ConversationTurn) -> None:
        """Add a completed turn to the module's memory."""

    def build_context(self, signal: TurnSignal, query: str) -> StrategyModuleOutput:
        """Produce a candidate context for ``query`` that fits ``signal.token_usage.budget``."""
