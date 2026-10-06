import pytest

from contracts import StrategyModuleOutput
from sliding_window import (
    DynamicSlidingWindow,
    FixedTokenWindow,
    RecencyOnlyWindow,
    SlidingWindowConfig,
    Weights,
    importance,
)

from conftest import CODE_SESSION, make_signal, turns_from


def load(window):
    for t in turns_from(CODE_SESSION):
        window.ingest(t)
    return window


def test_output_contract_and_chronological_order(embedder):
    w = load(DynamicSlidingWindow(embedder))
    out = w.build_context(make_signal(budget=80), "what is the signature of get_user_tasks")
    assert isinstance(out, StrategyModuleOutput) and out.module == "sliding_window"
    ids = out.quality.selected_turn_ids
    assert ids == sorted(ids)  # chronological restore
    assert out.token_count <= 80
    assert ids[-2:] == ["t0009", "t0010"]  # pinned recent turns


def test_relevance_pulls_in_old_definition(embedder):
    w = load(DynamicSlidingWindow(embedder, SlidingWindowConfig(weights=Weights(relevance=1, freshness=0, importance=0, state=0))))
    out = w.build_context(make_signal(budget=80), "get_user_tasks uid signature")
    assert "t0006" in out.quality.selected_turn_ids


def test_weights_are_runtime_config(embedder, monkeypatch):
    monkeypatch.setenv("CEAI_SW_WEIGHTS", "0.7,0.1,0.1,0.1")
    assert SlidingWindowConfig.from_env().weights.relevance == pytest.approx(0.7)
    w = DynamicSlidingWindow(embedder)
    w.set_weights("0,1,0,0")
    assert w.config.weights.normalized() == (0.0, 1.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        Weights.parse("1,2,3")
    with pytest.raises(ValueError):
        Weights(relevance=0, freshness=0, importance=0, state=0)


def test_importance_cues():
    assert importance("ok") == 0.0
    assert importance("```python\ndef f(x):\n    pass\n```") >= 0.4
    assert importance("We decided we must never use the v1 endpoint") > importance("nice weather today")


def test_state_factor_prefers_current_segment(embedder):
    w = DynamicSlidingWindow(embedder, SlidingWindowConfig(weights=Weights(relevance=0, freshness=0, importance=0, state=1), include_threshold=0.9, min_recent_turns=0))
    turns = turns_from(CODE_SESSION)
    for i, t in enumerate(turns):
        w.observe_signal(make_signal(turn_id=t.turn_id, state="shift_detected" if i == 6 else "task-1"))
        w.ingest(t)
    out = w.build_context(make_signal(turn_id="t0011", budget=1000), "anything")
    assert out.quality.selected_turn_ids == ["t0007", "t0008", "t0009", "t0010"]


def test_baselines(embedder):
    r = load(RecencyOnlyWindow(k=3))
    assert r.build_context(make_signal(budget=1000), "x").quality.selected_turn_ids == ["t0008", "t0009", "t0010"]
    f = load(FixedTokenWindow())
    out = f.build_context(make_signal(budget=30), "x")
    assert out.token_count <= 30 and out.quality.selected_turn_ids[-1] == "t0010"
