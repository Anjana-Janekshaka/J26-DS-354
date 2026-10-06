"""Structured summary records, one schema per tier (build guide 6.3).

L1: {facts, entities, constraints, turn_range}            - verbatim extraction, no interpretation
L2: {intent, decisions, open_goals, source_l1_ids}        - intent/decisions described from L1 facts
L3: {persona, main_objective, final_state, source_l2_ids} - the only tier allowed to generalize
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FactKind = Literal["code_signature", "rename", "attribute", "decision", "constraint", "request", "statement"]


class Fact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_id: str
    key: str  # merge key, e.g. "func:get_user_tasks", "user.location", "stmt:t0012:1"
    value: str  # verbatim text / exact signature
    kind: FactKind
    source_turn_id: str
    superseded_by: str | None = None  # fact_id of the replacing fact
    superseded_at: datetime | None = None


class L1Record(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    tier: Literal["L1"] = "L1"
    facts: list[Fact]
    entities: list[str]
    constraints: list[str]
    turn_range: tuple[str, str]
    generator: str = "rule_based"


class L2Record(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    tier: Literal["L2"] = "L2"
    intent: str
    decisions: list[str] = Field(default_factory=list)
    open_goals: list[str] = Field(default_factory=list)
    source_l1_ids: list[str]
    generator: str = "rule_based"


class L3Record(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    tier: Literal["L3"] = "L3"
    persona: str
    main_objective: str
    final_state: str
    source_l2_ids: list[str]
    generator: str = "rule_based"
