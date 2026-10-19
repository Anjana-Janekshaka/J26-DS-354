"""Conversation Manager & State Tracker.

Owns turn numbering, token-budget accounting, task-type classification and conversation state,
and publishes one ``TurnSignal`` per turn on the shared bus. It never tracks controller history
(``prior_strategy`` / ``time_since_last_switch`` belong to the controller, section 4.2).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from contracts import ConversationTurn, TokenUsage, TurnSignal, count_tokens, utcnow
from contracts.text import Embedder

from .bus import SignalBus
from .classifier import Classification, ClassifierConfig, TaskTypeClassifier


@dataclass
class ObservedTurn:
    turn: ConversationTurn
    signal: TurnSignal
    classification: Classification


class ConversationManager:
    def __init__(
        self,
        conversation_id: str,
        token_budget: int,
        bus: SignalBus | None = None,
        embedder: Embedder | None = None,
        classifier_config: ClassifierConfig | None = None,
    ):
        if token_budget <= 0:
            raise ValueError("token_budget must be positive")
        self.conversation_id = conversation_id
        self.token_budget = token_budget
        self.bus = bus or SignalBus()
        self.classifier = TaskTypeClassifier(embedder=embedder, config=classifier_config or ClassifierConfig())
        self.turn_count = 0
        self.tokens_used = 0
        self._task_index = 1
        self.task_type = "chat"
        self.turns: list[ConversationTurn] = []

    @property
    def active_task_id(self) -> str:
        return f"task-{self._task_index}"

    def _next_turn_id(self) -> str:
        return f"t{self.turn_count + 1:04d}"

    def observe(
        self,
        role: str,
        content: str,
        *,
        decision_point: bool | None = None,
        speaker: str | None = None,
        timestamp: datetime | None = None,
        metadata: dict | None = None,
        publish: bool = True,
    ) -> ObservedTurn:
        """Register one message, update state, publish its ``TurnSignal`` and return both.

        ``decision_point`` (default: ``role == 'user'``) marks turns where the controller will be
        asked to pick a strategy; only those are task-type classified from phrasing.
        """
        if decision_point is None:
            decision_point = role == "user"
        turn = ConversationTurn(
            turn_id=self._next_turn_id(),
            role=role,  # type: ignore[arg-type]
            content=content,
            speaker=speaker,
            timestamp=timestamp,
            metadata=dict(metadata or {}),
        )
        cls = self.classifier.observe(content, decision_point=decision_point) if role != "assistant" else Classification(
            task_type=self.task_type, shift_detected=False, matched_rule="assistant_turn", topic_similarity=None
        )
        if cls.shift_detected:
            self._task_index += 1
        self.task_type = cls.task_type
        self.turn_count += 1
        self.tokens_used += count_tokens(turn.render())
        turn.metadata.setdefault("task_id", self.active_task_id)
        self.turns.append(turn)

        signal = TurnSignal(
            turn_id=turn.turn_id,
            conversation_id=self.conversation_id,
            turn_count=self.turn_count,
            task_type=self.task_type,
            token_usage=TokenUsage(used=self.tokens_used, budget=self.token_budget),
            conversation_state=TurnSignal.SHIFT_DETECTED if cls.shift_detected else self.active_task_id,
            timestamp=timestamp or utcnow(),
            recall_request=cls.recall_request,
        )
        if publish:
            self.bus.publish(signal)
        return ObservedTurn(turn=turn, signal=signal, classification=cls)

    def probe(self, content: str, **kw) -> ObservedTurn:
        """Classify and signal a user message *without* committing it to the conversation.

        Used for evaluation questions: the signal reflects the current state (token usage includes
        the probe itself), then turn count, token usage, task state and topic centroid are restored.
        The probe gets a distinct id (``t0042.p3``) so its decision record never collides.
        """
        snap = (
            self.turn_count,
            self.tokens_used,
            self._task_index,
            self.task_type,
            list(self.classifier._recent),
            self.classifier._seen,
            self.classifier._last_type,
            len(self.turns),
        )
        self._probe_seq = getattr(self, "_probe_seq", 0) + 1
        obs = self.observe("user", content, decision_point=True, publish=False, **kw)
        pid = f"{obs.turn.turn_id}.p{self._probe_seq}"
        obs.turn.turn_id = pid
        signal = obs.signal.model_copy(update={"turn_id": pid})
        (
            self.turn_count,
            self.tokens_used,
            self._task_index,
            self.task_type,
            self.classifier._recent,
            self.classifier._seen,
            self.classifier._last_type,
            n,
        ) = snap
        del self.turns[n:]
        return ObservedTurn(turn=obs.turn, signal=signal, classification=obs.classification)
