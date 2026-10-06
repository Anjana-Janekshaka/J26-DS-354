"""Model-based controller variants (LR -> RF -> GBDT).

# TODO: v2 - deliberately not implemented for Progress Presentation 1. Training needs real decision
# logs (feature_vector -> oracle strategy) that only exist once the rule-based controller has run
# through the pipeline (build guide sections 7 and 10, step 8). This class exposes the interface
# and refuses to produce decisions rather than returning a fabricated one.
"""

from __future__ import annotations

from pathlib import Path

from contracts import ControllerDecision, ControllerFeatureVector, ControllerVariant, TurnSignal


class ModelBasedController:
    def __init__(self, variant: ControllerVariant = "logistic_regression"):
        if variant == "rule_based":
            raise ValueError("use RuleBasedController for the rule_based variant")
        self.variant = variant
        self.trained = False

    def train(self, decision_log_paths: list[Path]) -> None:
        raise NotImplementedError(
            f"TODO: v2 - {self.variant} training on decision logs + oracle labels is post-Progress-Presentation-1 scope"
        )

    def decide(self, signal: TurnSignal) -> tuple[ControllerFeatureVector, ControllerDecision]:
        raise NotImplementedError(f"TODO: v2 - {self.variant} controller is not trained; use RuleBasedController")
