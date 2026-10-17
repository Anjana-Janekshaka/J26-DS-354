import inspect

import pytest

from contracts import EscalationEvent, OverrideRequest, utcnow
from controller import ModelBasedController, RuleBasedController

from conftest import make_signal


def esc(kind, turn="t0001", **detail):
    return EscalationEvent(
        event_id="e1",
        conversation_id="c",
        source_turn_id=turn,
        source_module="summarization" if kind == "loss_threshold_exceeded" else "rag",
        kind=kind,
        detail=detail,
        raised_at=utcnow(),
    )


def test_decide_signature_has_no_access_to_module_outputs():
    params = inspect.signature(RuleBasedController.decide).parameters
    assert list(params) == ["self", "signal", "commit"]


def test_rules():
    c = RuleBasedController()
    assert c.decide(make_signal("t1", used=10, budget=100))[1].selected_strategy == "sliding_window"
    assert c.decide(make_signal("t2", used=100, budget=100, task_type="qa"))[1].selected_strategy == "rag"
    assert c.decide(make_signal("t3", used=100, budget=100, task_type="code_generation"))[1].selected_strategy == "hybrid"
    assert c.decide(make_signal("t4", used=100, budget=100, task_type="code_refactor"))[1].selected_strategy == "summarization"


def test_feature_vector_tracks_own_history():
    c = RuleBasedController()
    fv1, _ = c.decide(make_signal("t1", used=10, budget=100))
    fv2, _ = c.decide(make_signal("t2", used=20, budget=100))
    fv3, _ = c.decide(make_signal("t3", used=200, budget=100, task_type="qa"))
    assert fv1.prior_strategy is None
    assert fv2.prior_strategy == "sliding_window" and fv2.time_since_last_switch == 0
    assert fv3.time_since_last_switch == 1 and fv3.token_budget_pressure == 1.0


def test_escalation_applies_to_next_turn_only():
    c = RuleBasedController()
    c.decide(make_signal("t1", used=100, budget=100, task_type="code_refactor"))
    c.register_escalation(esc("loss_threshold_exceeded", turn="t1", loss_score=0.4, tier_emitted="L3"))
    _, d2 = c.decide(make_signal("t2", used=100, budget=100, task_type="code_refactor"))
    assert d2.selected_strategy == "rag" and "escalation from t1" in d2.rationale
    _, d3 = c.decide(make_signal("t3", used=100, budget=100, task_type="code_refactor"))
    assert d3.selected_strategy == "summarization"  # consumed once


def test_escalation_from_same_turn_is_not_used():
    c = RuleBasedController()
    c.register_escalation(esc("loss_threshold_exceeded", turn="t5"))
    _, d = c.decide(make_signal("t5", used=100, budget=100, task_type="code_refactor"))
    assert d.selected_strategy == "summarization"


def test_override_and_scope():
    c = RuleBasedController()
    c.request_override(OverrideRequest(strategy="rag", by="operator"))
    _, d1 = c.decide(make_signal("t1", used=10, budget=100))
    assert d1.selected_strategy == "rag" and d1.override.applied and d1.override.by == "operator"
    _, d2 = c.decide(make_signal("t2", used=10, budget=100))
    assert not d2.override.applied
    c.request_override(OverrideRequest(strategy="summarization", by="op", scope="until_cleared"))
    assert c.decide(make_signal("t3", used=10, budget=100))[1].override.applied
    assert c.decide(make_signal("t4", used=10, budget=100))[1].override.applied
    c.clear_override()
    assert not c.decide(make_signal("t5", used=10, budget=100))[1].override.applied


def test_dwell_hysteresis_on_soft_rules():
    c = RuleBasedController()
    c.decide(make_signal("t1", used=100, budget=100, task_type="qa"))  # rag (hard)
    _, d = c.decide(make_signal("t2", used=100, budget=100, task_type="debugging"))  # soft -> held
    assert d.selected_strategy == "rag" and "dwell" in d.rationale


def test_probe_decision_does_not_commit():
    c = RuleBasedController()
    c.decide(make_signal("t1", used=10, budget=100))
    c.decide(make_signal("t2.p1", used=100, budget=100, task_type="qa"), commit=False)
    assert c.prior_strategy == "sliding_window" and len(c.history) == 1


def test_model_based_refuses_until_trained_then_decides_from_signal_only():
    m = ModelBasedController("logistic_regression")
    with pytest.raises(RuntimeError, match="not trained"):
        m.decide(make_signal())
    from controller.model_based import FEATURE_NAMES

    X = [[float(i % 3)] * len(FEATURE_NAMES) for i in range(12)]
    y = ["rag", "hybrid", "sliding_window"] * 4
    m.train(X, y)
    fv, d = m.decide(make_signal())
    assert d.controller_variant == "logistic_regression" and d.selected_strategy in {"rag", "hybrid", "sliding_window"}
    assert d.rationale.startswith("[logistic_regression] p(") and m.prior_strategy == d.selected_strategy
