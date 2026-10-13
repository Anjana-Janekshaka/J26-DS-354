"""ASSE - Adaptive Strategy Selection Engine (rule-based variant).

Leakage-freedom is structural: ``decide`` receives only the ``TurnSignal`` (Tier 0) and builds the
``ControllerFeatureVector`` from it plus the controller's own decision history (Tier 1). Module
outputs never reach this class. Tier 2 signals arrive as ``EscalationEvent``s registered *after*
a turn rendered and are consumed by the next ``decide`` call only.
"""

from __future__ import annotations

import threading
import time

from contracts import (
    ControllerDecision,
    ControllerFeatureVector,
    EscalationEvent,
    OverrideInfo,
    OverrideRequest,
    SelectedStrategy,
    TurnSignal,
)

from .rules import RULES, RuleConfig, RuleHit, apply_escalations


class RuleBasedController:
    variant = "rule_based"

    def __init__(self, config: RuleConfig | None = None, default_strategy: SelectedStrategy = "sliding_window"):
        self.config = config or RuleConfig()
        self.default_strategy: SelectedStrategy = default_strategy
        self.prior_strategy: SelectedStrategy | None = None
        self.time_since_last_switch = 0
        self.history: list[ControllerDecision] = []
        self._pending: list[EscalationEvent] = []
        self._override: OverrideRequest | None = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ inputs other than the signal
    def register_escalation(self, event: EscalationEvent) -> None:
        """Queue a Tier 2 escalation; it influences the NEXT decision only."""
        with self._lock:
            self._pending.append(event)

    def request_override(self, request: OverrideRequest) -> None:
        with self._lock:
            self._override = request

    def clear_override(self) -> None:
        with self._lock:
            self._override = None

    # ------------------------------------------------------------------ feature vector
    def feature_vector(self, signal: TurnSignal) -> ControllerFeatureVector:
        used, budget = signal.token_usage.used, signal.token_usage.budget
        return ControllerFeatureVector(
            turn_count=signal.turn_count,
            token_budget_pressure=round(min(1.0, used / budget), 4),
            task_type=signal.task_type,
            prior_strategy=self.prior_strategy,
            time_since_last_switch=self.time_since_last_switch,
        )

    # ------------------------------------------------------------------ decision
    def _rule(self, fv: ControllerFeatureVector, shift: bool = False) -> RuleHit:
        for rule in RULES:
            hit = rule(fv, self.config, shift)
            if hit is not None:
                return hit
        if fv.prior_strategy is not None:
            return RuleHit("hold", fv.prior_strategy, f"no rule matched task_type={fv.task_type}; holding {fv.prior_strategy}", hard=False)
        return RuleHit("default", self.default_strategy, "no rule matched; default strategy", hard=False)

    def decide(self, signal: TurnSignal, commit: bool = True) -> tuple[ControllerFeatureVector, ControllerDecision]:
        """Decide from the signal alone. ``commit=False`` (evaluation probes) leaves history,
        pending escalations and one-shot overrides untouched."""
        t0 = time.perf_counter()
        with self._lock:
            events = [e for e in self._pending if e.source_turn_id != signal.turn_id]
            override = self._override
            if commit:
                self._pending = [e for e in self._pending if e.source_turn_id == signal.turn_id]
                if override is not None and override.scope == "next_turn":
                    self._override = None

        fv = self.feature_vector(signal)
        hit = self._rule(fv, signal.shift_detected)
        strategy = hit.strategy
        parts = [f"[{hit.rule}] {hit.reason}"]

        # Hysteresis: soft rules may not switch away before the minimum dwell time.
        if (
            not hit.hard
            and fv.prior_strategy is not None
            and strategy != fv.prior_strategy
            and fv.time_since_last_switch < self.config.min_dwell_turns
        ):
            parts.append(
                f"dwell: held {fv.prior_strategy} ({fv.time_since_last_switch} < {self.config.min_dwell_turns} turns since last switch)"
            )
            strategy = fv.prior_strategy

        strategy, notes = apply_escalations(RuleHit(hit.rule, strategy, hit.reason, hit.hard), events, self.config)
        parts += notes

        override_info = OverrideInfo(applied=False, by=None)
        if override is not None:
            parts.append(f"OVERRIDE by {override.by}: {strategy} -> {override.strategy}")
            strategy = override.strategy
            override_info = OverrideInfo(applied=True, by=override.by)

        parts.append(
            f"features: turn={fv.turn_count}, pressure={fv.token_budget_pressure:.2f}, task={fv.task_type}, "
            f"prior={fv.prior_strategy}, since_switch={fv.time_since_last_switch}"
        )
        decision = ControllerDecision(
            turn_id=signal.turn_id,
            selected_strategy=strategy,
            rationale=" | ".join(parts),
            controller_variant="rule_based",
            decision_latency_ms=round((time.perf_counter() - t0) * 1000, 4),
            override=override_info,
        )
        if not commit:
            return fv, decision
        if self.prior_strategy is None or strategy != self.prior_strategy:
            self.time_since_last_switch = 0
        else:
            self.time_since_last_switch += 1
        self.prior_strategy = strategy
        self.history.append(decision)
        return fv, decision
