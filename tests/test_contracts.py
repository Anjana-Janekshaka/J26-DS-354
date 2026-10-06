"""Schema-validation tests for packages/contracts (build order step 1)."""

import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from contracts import (
    LOSS_THRESHOLD,
    ControllerDecision,
    ControllerFeatureVector,
    ConversationTurn,
    DecisionLogRecord,
    StrategyModuleOutput,
    SummarizationQuality,
    TurnSignal,
)

NOW = datetime(2026, 10, 6, tzinfo=timezone.utc)


def signal(**kw):
    base = dict(
        turn_id="t0001",
        conversation_id="c1",
        turn_count=1,
        task_type="chat",
        token_usage={"used": 10, "budget": 100},
        conversation_state="task-1",
        timestamp=NOW,
    )
    base.update(kw)
    return TurnSignal.model_validate(base)


def sw_output():
    return StrategyModuleOutput.model_validate(
        {
            "module": "sliding_window",
            "candidate_context": [{"turn_id": "t0001", "role": "user", "content": "hi"}],
            "readiness": {"available": True, "estimated_latency_ms": 1.0},
            "quality": {
                "selected_turn_ids": ["t0001"],
                "scores": {"relevance": 0.1, "freshness": 1.0, "importance": 0.0, "state": 1.0, "composite": 0.5},
            },
            "token_count": 3,
        }
    )


def sum_output(loss=0.05):
    return StrategyModuleOutput.model_validate(
        {
            "module": "summarization",
            "candidate_context": "facts...",
            "readiness": {"available": True, "estimated_latency_ms": 2.0},
            "quality": {
                "tier_emitted": "L1",
                "loss_score": loss,
                "loss_threshold_exceeded": loss > LOSS_THRESHOLD,
                "symbol_retention_rate": None,
            },
            "token_count": 5,
        }
    )


def rag_output():
    return StrategyModuleOutput.model_validate(
        {
            "module": "rag",
            "candidate_context": "chunk text",
            "readiness": {"available": True, "estimated_latency_ms": 3.0},
            "quality": {
                "granularity_tag": "turn",
                "retrieved_chunk_ids": ["turn:t0001"],
                "contradiction_flags": [{"chunk_id": "turn:t0001", "nli_confidence": 0.9, "superseded_by": "turn:t0009"}],
            },
            "token_count": 2,
        }
    )


def decision(**kw):
    base = dict(
        turn_id="t0001",
        selected_strategy="rag",
        rationale="task_type=qa -> rag",
        controller_variant="rule_based",
        decision_latency_ms=0.2,
        override={"applied": False, "by": None},
    )
    base.update(kw)
    return ControllerDecision.model_validate(base)


def test_turn_signal_roundtrip():
    s = signal(conversation_state="shift_detected")
    assert s.shift_detected
    again = TurnSignal.model_validate_json(s.model_dump_json())
    assert again == s


def test_extra_fields_rejected():
    with pytest.raises(ValidationError):
        signal(unexpected="x")


def test_feature_vector_pressure_bounds():
    ControllerFeatureVector(turn_count=3, token_budget_pressure=1.0, task_type="qa", prior_strategy=None, time_since_last_switch=0)
    with pytest.raises(ValidationError):
        ControllerFeatureVector(turn_count=3, token_budget_pressure=1.2, task_type="qa", prior_strategy=None, time_since_last_switch=0)


def test_module_quality_parsed_by_module():
    assert type(sw_output().quality).__name__ == "SlidingWindowQuality"
    assert type(sum_output().quality).__name__ == "SummarizationQuality"
    assert type(rag_output().quality).__name__ == "RagQuality"


def test_quality_must_match_module():
    data = json.loads(rag_output().model_dump_json())
    data["module"] = "summarization"
    with pytest.raises(ValidationError):
        StrategyModuleOutput.model_validate(data)


def test_loss_threshold_flag_must_match_score():
    SummarizationQuality(tier_emitted="L2", loss_score=0.2, loss_threshold_exceeded=True)
    with pytest.raises(ValidationError):
        SummarizationQuality(tier_emitted="L2", loss_score=0.2, loss_threshold_exceeded=False)
    with pytest.raises(ValidationError):
        SummarizationQuality(tier_emitted="L2", loss_score=LOSS_THRESHOLD, loss_threshold_exceeded=True)


def test_override_consistency():
    decision(override={"applied": True, "by": "operator"})
    with pytest.raises(ValidationError):
        decision(override={"applied": True, "by": None})
    with pytest.raises(ValidationError):
        decision(override={"applied": False, "by": "operator"})


def test_decision_strategy_enum():
    decision(selected_strategy="hybrid")
    with pytest.raises(ValidationError):
        decision(selected_strategy="always_on")


def test_decision_log_record_roundtrip_and_consistency():
    fv = ControllerFeatureVector(turn_count=1, token_budget_pressure=0.1, task_type="chat", prior_strategy=None, time_since_last_switch=0)
    rec = DecisionLogRecord(
        turn_id="t0001",
        feature_vector=fv,
        decision=decision(),
        module_outputs={"sliding_window": sw_output(), "summarization": sum_output(), "rag": rag_output()},
        logged_at=NOW,
    )
    line = rec.model_dump_json()
    back = DecisionLogRecord.model_validate_json(line)
    assert back == rec
    assert isinstance(back.module_outputs["sliding_window"].candidate_context[0], ConversationTurn)

    with pytest.raises(ValidationError):
        DecisionLogRecord(turn_id="t0002", feature_vector=fv, decision=decision(), module_outputs={}, logged_at=NOW)
    with pytest.raises(ValidationError):
        DecisionLogRecord(turn_id="t0001", feature_vector=fv, decision=decision(), module_outputs={"rag": sw_output()}, logged_at=NOW)


def test_turn_render_includes_date_and_speaker():
    t = ConversationTurn(turn_id="t1", role="user", content="hello", speaker="Ana", metadata={"date": "7 May 2023"})
    assert t.render() == "[7 May 2023] Ana: hello"
