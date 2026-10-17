"""llm_policy: strict makes no LLM calls; assisted writes only L2/L3 and never changes the controller's choices."""

import json

import pytest

from integration import MemoryPipeline
from retrieval import RetrievalConfig


def fake_llm(system: str, user: str) -> str:
    if "persona" in system.lower() or "persona" in user.lower():
        return json.dumps({"persona": "a developer", "main_objective": "ship the feature", "final_state": "in progress"})
    return json.dumps({"intent": "build and debug a service", "decisions": ["use uid"], "open_goals": ["deploy"]})


def run(embedder, policy: str, llm=None):
    calls = []

    def counting(system, user):
        calls.append(system)
        return fake_llm(system, user)

    p = MemoryPipeline("pol", 200, embedder=embedder, nli=None, llm=counting if llm else None, llm_policy=policy,
                       retrieval_config=RetrievalConfig(min_score=0.0))
    choices = []
    for i in range(40):
        choices.append(p.user_turn(f"Message {i}: we discussed the invoice export, step {i}, and the due dates.").decision.selected_strategy)
        p.assistant_turn(f"Noted step {i}; the export uses the reporting service.")
    summ = p.modules["summarization"]
    p.close()
    return choices, summ, calls


def test_strict_is_default_and_makes_no_calls(embedder):
    choices, summ, calls = run(embedder, "strict", llm=True)
    assert calls == [] and summ.generator.name == "rule_based"


def test_assisted_only_l2_l3_and_controller_unchanged(embedder):
    strict_choices, _, _ = run(embedder, "strict")
    choices, summ, calls = run(embedder, "assisted", llm=True)
    assert choices == strict_choices  # the policy never reaches the controller
    assert summ.l1 and all(r.generator == "rule_based" for r in summ.l1)
    assert summ.l2 and all(r.generator == "llm" for r in summ.l2)
    assert summ.generator.llm_calls == len(calls) > 0


def test_assisted_needs_an_llm(embedder):
    with pytest.raises(ValueError, match="needs an llm"):
        MemoryPipeline("pol", 200, embedder=embedder, nli=None, llm_policy="assisted")
