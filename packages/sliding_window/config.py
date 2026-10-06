"""Runtime configuration for the Dynamic Sliding Window.

Weights are *not* hardcoded: they come from (in priority order) explicit arguments, a JSON file
named by ``CEAI_SW_CONFIG``, the ``CEAI_SW_WEIGHTS`` env var (``"relevance,freshness,importance,state"``),
or the defaults below, and can be changed at runtime via ``DynamicSlidingWindow.set_weights``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

FACTORS = ("relevance", "freshness", "importance", "state")


class Weights(BaseModel):
    relevance: float = Field(default=0.25, ge=0.0)
    freshness: float = Field(default=0.25, ge=0.0)
    importance: float = Field(default=0.25, ge=0.0)
    state: float = Field(default=0.25, ge=0.0)

    @model_validator(mode="after")
    def _not_all_zero(self) -> "Weights":
        if sum(self.as_tuple()) <= 0:
            raise ValueError("at least one weight must be positive")
        return self

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.relevance, self.freshness, self.importance, self.state)

    def normalized(self) -> tuple[float, float, float, float]:
        total = sum(self.as_tuple())
        return tuple(w / total for w in self.as_tuple())  # type: ignore[return-value]

    @classmethod
    def parse(cls, spec: str) -> "Weights":
        parts = [float(x) for x in spec.split(",")]
        if len(parts) != 4:
            raise ValueError("weights spec must have 4 comma-separated values: relevance,freshness,importance,state")
        return cls(**dict(zip(FACTORS, parts)))


class SlidingWindowConfig(BaseModel):
    weights: Weights = Field(default_factory=Weights)
    freshness_half_life_turns: float = Field(default=8.0, gt=0)
    min_recent_turns: int = Field(default=2, ge=0)
    include_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    state_decay: float = Field(default=0.5, gt=0.0, le=1.0)

    @classmethod
    def from_env(cls) -> "SlidingWindowConfig":
        path = os.environ.get("CEAI_SW_CONFIG")
        if path:
            return cls.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
        cfg = cls()
        spec = os.environ.get("CEAI_SW_WEIGHTS")
        if spec:
            cfg.weights = Weights.parse(spec)
        return cfg
