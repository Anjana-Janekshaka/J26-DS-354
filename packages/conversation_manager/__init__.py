"""Conversation Manager & State Tracker: turn counter, token budget, task type, TurnSignal bus."""

from .bus import SignalBus
from .classifier import Classification, ClassifierConfig, TaskTypeClassifier
from .manager import ConversationManager, ObservedTurn

__all__ = [
    "Classification",
    "ClassifierConfig",
    "ConversationManager",
    "ObservedTurn",
    "SignalBus",
    "TaskTypeClassifier",
]
