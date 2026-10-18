"""Model-based controller variants (logistic regression, random forest, gradient boosting).

Same contract and the same leakage rule as the rule-based controller: ``decide`` sees only the
``TurnSignal`` plus the controller's own history and escalations registered on *earlier* turns
(section 5). The feature vector is the Tier 0/1 ``ControllerFeatureVector`` plus the signal's
topic-shift flag and two pending-escalation flags. History, escalations and manual overrides are
handled exactly as in ``RuleBasedController``; only the strategy choice comes from the model.

Training data are (features, oracle strategy) pairs, recorded by replaying a controller over traced
conversations (``eval/synthetic/controller/learned.py``). Every rationale names the model and its top
class probabilities, so decisions stay explainable. Evaluated in docs/v4_preregistration.md section 4;
not part of the frozen system.
"""

from __future__ import annotations

import time

from contracts import ControllerDecision, ControllerFeatureVector, ControllerVariant, EscalationEvent, OverrideInfo, TurnSignal

from .controller import RuleBasedController

STRATEGIES = ("sliding_window", "summarization", "rag", "hybrid")
TASK_TYPES = ("chat", "exploration", "qa", "debugging", "code_generation", "code_refactor")
FEATURE_NAMES = (
    ["turn_count", "token_budget_pressure", "time_since_last_switch", "shift", "loss_pending", "contradiction_pending"]
    + [f"task={t}" for t in TASK_TYPES]
    + [f"prior={s}" for s in (*STRATEGIES, None)]
)


def featurize(fv: ControllerFeatureVector, shift: bool, events: list[EscalationEvent]) -> list[float]:
    kinds = {e.kind for e in events}
    return (
        [float(fv.turn_count), fv.token_budget_pressure, float(fv.time_since_last_switch), float(shift),
         float("loss_threshold_exceeded" in kinds), float("contradiction_flagged" in kinds)]
        + [float(fv.task_type == t) for t in TASK_TYPES]
        + [float(fv.prior_strategy == s) for s in (*STRATEGIES, None)]
    )


def make_model(variant: ControllerVariant):
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if variant == "logistic_regression":
        return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    if variant == "random_forest":
        return RandomForestClassifier(n_estimators=300, random_state=0)
    if variant == "gbdt":
        return GradientBoostingClassifier(random_state=0)
    raise ValueError(f"unknown model variant {variant!r}")


class ModelBasedController(RuleBasedController):
    def __init__(self, variant: ControllerVariant = "logistic_regression", model=None):
        if variant == "rule_based":
            raise ValueError("use RuleBasedController for the rule_based variant")
        super().__init__()
        self.variant = variant
        self.model = model
        self.trained = model is not None

    def train(self, X: list[list[float]], y: list[str]) -> "ModelBasedController":
        self.model = make_model(self.variant).fit(X, y)
        self.trained = True
        return self

    def decide(self, signal: TurnSignal, commit: bool = True) -> tuple[ControllerFeatureVector, ControllerDecision]:
        if not self.trained:
            raise RuntimeError(f"{self.variant} controller is not trained")
        t0 = time.perf_counter()
        with self._lock:
            events = [e for e in self._pending if e.source_turn_id != signal.turn_id]
            override = self._override
            if commit:
                self._pending = [e for e in self._pending if e.source_turn_id == signal.turn_id]
                if override is not None and override.scope == "next_turn":
                    self._override = None

        fv = self.feature_vector(signal)
        probs = self.model.predict_proba([featurize(fv, signal.shift_detected, events)])[0]
        ranked = sorted(zip(self.model.classes_, probs), key=lambda x: -x[1])
        strategy = ranked[0][0]
        parts = [f"[{self.variant}] " + ", ".join(f"p({s})={p:.2f}" for s, p in ranked[:3])]
        if events:
            parts.append("pending escalations: " + ", ".join(sorted({e.kind for e in events})))
        override_info = OverrideInfo(applied=False, by=None)
        if override is not None:
            parts.append(f"OVERRIDE by {override.by}: {strategy} -> {override.strategy}")
            strategy = override.strategy
            override_info = OverrideInfo(applied=True, by=override.by)
        parts.append(
            f"features: turn={fv.turn_count}, pressure={fv.token_budget_pressure:.2f}, task={fv.task_type}, "
            f"prior={fv.prior_strategy}, since_switch={fv.time_since_last_switch}, shift={signal.shift_detected}"
        )
        decision = ControllerDecision(
            turn_id=signal.turn_id,
            selected_strategy=strategy,
            rationale=" | ".join(parts),
            controller_variant=self.variant,
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
