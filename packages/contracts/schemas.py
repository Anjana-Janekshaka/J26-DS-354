"""Canonical shared contracts (build guide section 4).

Every package imports these types from here; nothing else is allowed to redefine them.
Field names and shapes follow section 4 exactly. Two additive types exist because section 5
and section 7 require them but section 4 does not spell out their shape:

* ``EscalationEvent`` - a Tier 2 signal raised *after* a module ran for a turn (section 5).
  It is logged next to the decision log (joined on ``source_turn_id``) and consumed by the
  controller on the *next* turn only.
* ``OverrideRequest`` - a human override queued for the controller's next decision.

``ConversationTurn`` is the concrete shape of the ``turn`` referenced by
``StrategyModuleOutput.candidate_context: string | array<turn>``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, ClassVar, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

StrategyName = Literal["sliding_window", "summarization", "rag"]
SelectedStrategy = Literal["sliding_window", "summarization", "rag", "hybrid"]
ControllerVariant = Literal["rule_based", "logistic_regression", "random_forest", "gbdt"]
SummaryTier = Literal["L1", "L2", "L3"]
Granularity = Literal["turn", "segment"]
Role = Literal["user", "assistant", "system"]

STRATEGY_MODULES: tuple[StrategyName, ...] = ("sliding_window", "summarization", "rag")

# Task types published by the conversation manager. The list is open (section 4.1 says "e.g."),
# these are the values the rule-based classifier emits.
TASK_TYPES: tuple[str, ...] = (
    "chat",
    "qa",
    "exploration",
    "debugging",
    "code_generation",
    "code_refactor",
)

# Section 4.3: loss_threshold_exceeded is defined as loss_score > 0.15.
LOSS_THRESHOLD = 0.15


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------- conversation


class ConversationTurn(_Contract):
    """One message in the conversation. ``turn_id`` is monotonic within a conversation."""

    turn_id: str
    role: Role
    content: str
    speaker: str | None = None
    timestamp: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def render(self) -> str:
        """Canonical text form used for prompts and token counting by every package."""
        who = self.speaker or self.role
        date = f"[{self.metadata['date']}] " if self.metadata.get("date") else ""
        return f"{date}{who}: {self.content}"


# --------------------------------------------------------------------------- 4.1 TurnSignal


class TokenUsage(_Contract):
    used: int = Field(ge=0)
    budget: int = Field(gt=0)


class TurnSignal(_Contract):
    SHIFT_DETECTED: ClassVar[str] = "shift_detected"

    turn_id: str
    conversation_id: str
    turn_count: int = Field(ge=0)
    task_type: str
    token_usage: TokenUsage
    conversation_state: str
    timestamp: datetime

    @property
    def shift_detected(self) -> bool:
        return self.conversation_state == self.SHIFT_DETECTED


# --------------------------------------------------------------------------- 4.2 feature vector


class ControllerFeatureVector(_Contract):
    turn_count: int = Field(ge=0)
    token_budget_pressure: float = Field(ge=0.0, le=1.0)
    task_type: str
    prior_strategy: SelectedStrategy | None
    time_since_last_switch: int = Field(ge=0)


# --------------------------------------------------------------------------- 4.3 module output


class Readiness(_Contract):
    available: bool
    estimated_latency_ms: float = Field(ge=0.0)


class CompositeScores(_Contract):
    relevance: float = Field(ge=0.0, le=1.0)
    freshness: float = Field(ge=0.0, le=1.0)
    importance: float = Field(ge=0.0, le=1.0)
    state: float = Field(ge=0.0, le=1.0)
    composite: float = Field(ge=0.0, le=1.0)


class SlidingWindowQuality(_Contract):
    selected_turn_ids: list[str]
    scores: CompositeScores


class SummarizationQuality(_Contract):
    tier_emitted: SummaryTier
    loss_score: float = Field(ge=0.0, le=1.0)
    loss_threshold_exceeded: bool
    symbol_retention_rate: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _threshold_consistent(self) -> "SummarizationQuality":
        if self.loss_threshold_exceeded != (self.loss_score > LOSS_THRESHOLD):
            raise ValueError(
                f"loss_threshold_exceeded must equal loss_score > {LOSS_THRESHOLD} "
                f"(got score={self.loss_score}, exceeded={self.loss_threshold_exceeded})"
            )
        return self


class ContradictionFlag(_Contract):
    chunk_id: str
    nli_confidence: float = Field(ge=0.0, le=1.0)
    superseded_by: str


class RagQuality(_Contract):
    granularity_tag: Granularity
    retrieved_chunk_ids: list[str]
    contradiction_flags: list[ContradictionFlag]


ModuleQuality = Union[SlidingWindowQuality, SummarizationQuality, RagQuality]

_QUALITY_BY_MODULE: dict[str, type[BaseModel]] = {
    "sliding_window": SlidingWindowQuality,
    "summarization": SummarizationQuality,
    "rag": RagQuality,
}


class StrategyModuleOutput(_Contract):
    module: StrategyName
    candidate_context: Union[str, list[ConversationTurn]]
    readiness: Readiness
    quality: ModuleQuality
    token_count: int = Field(ge=0)

    @model_validator(mode="before")
    @classmethod
    def _parse_quality_for_module(cls, data: Any) -> Any:
        # The quality block's shape is determined by ``module`` (section 4.3); parse it explicitly
        # instead of letting the union guess.
        if isinstance(data, dict) and isinstance(data.get("quality"), dict):
            model = _QUALITY_BY_MODULE.get(data.get("module", ""))
            if model is not None:
                data = {**data, "quality": model.model_validate(data["quality"])}
        return data

    @model_validator(mode="after")
    def _quality_matches_module(self) -> "StrategyModuleOutput":
        expected = _QUALITY_BY_MODULE[self.module]
        if not isinstance(self.quality, expected):
            raise ValueError(f"module {self.module!r} requires quality of type {expected.__name__}")
        return self

    def context_text(self) -> str:
        if isinstance(self.candidate_context, str):
            return self.candidate_context
        return "\n".join(t.render() for t in self.candidate_context)


# --------------------------------------------------------------------------- 4.4 decision


class OverrideInfo(_Contract):
    applied: bool
    by: str | None

    @model_validator(mode="after")
    def _by_iff_applied(self) -> "OverrideInfo":
        if self.applied and not self.by:
            raise ValueError("override.by is required when override.applied is true")
        if not self.applied and self.by is not None:
            raise ValueError("override.by must be null when override.applied is false")
        return self


class ControllerDecision(_Contract):
    turn_id: str
    selected_strategy: SelectedStrategy
    rationale: str
    controller_variant: ControllerVariant
    decision_latency_ms: float = Field(ge=0.0)
    override: OverrideInfo

    @field_validator("rationale")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("rationale must be a non-empty human-readable string")
        return v


# --------------------------------------------------------------------------- 4.5 log record


class DecisionLogRecord(_Contract):
    turn_id: str
    feature_vector: ControllerFeatureVector
    decision: ControllerDecision
    module_outputs: dict[StrategyName, StrategyModuleOutput]
    logged_at: datetime

    @model_validator(mode="after")
    def _consistent(self) -> "DecisionLogRecord":
        if self.decision.turn_id != self.turn_id:
            raise ValueError("decision.turn_id must equal record turn_id")
        for key, out in self.module_outputs.items():
            if out.module != key:
                raise ValueError(f"module_outputs[{key!r}] holds output of module {out.module!r}")
        return self


# --------------------------------------------------------------------------- additive (sec. 5 / 7)


class EscalationEvent(_Contract):
    """A Tier 2 signal that fired after a module ran. Consumed on the next turn only (section 5)."""

    event_id: str
    conversation_id: str
    source_turn_id: str
    source_module: StrategyName
    kind: Literal["loss_threshold_exceeded", "contradiction_flagged"]
    detail: dict[str, Any] = Field(default_factory=dict)
    raised_at: datetime


class OverrideRequest(_Contract):
    """A human override for the controller. ``scope='next_turn'`` applies once."""

    strategy: SelectedStrategy
    by: str
    scope: Literal["next_turn", "until_cleared"] = "next_turn"
    requested_at: datetime = Field(default_factory=utcnow)
