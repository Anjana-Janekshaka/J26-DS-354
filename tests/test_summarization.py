from contracts import LOSS_THRESHOLD, ConversationTurn
from summarization import (
    HierarchicalSummarizer,
    LLMGenerator,
    NaiveSummarizer,
    SummarizationConfig,
    anchor_loss,
    symbol_retention_rate,
)
from summarization.extract import extract_facts

from conftest import CODE_SESSION, make_signal, turns_from


def build(**cfg):
    s = HierarchicalSummarizer(config=SummarizationConfig(l1_span=2, tail_keep=2, l2_fanin=2, **cfg))
    for t in turns_from(CODE_SESSION):
        s.ingest(t)
    return s


def test_l1_extracts_exact_signatures_verbatim():
    t = ConversationTurn(turn_id="t1", role="assistant", content="```python\ndef get_user_tasks(uid: int, *, limit=10) -> list:\n    pass\n```")
    facts, _ = extract_facts(t, [0])
    assert [(f.key, f.value) for f in facts] == [("func:get_user_tasks", "def get_user_tasks(uid: int, *, limit=10) -> list")]


def test_contradiction_merge_supersedes_with_timestamp():
    s = build()
    active = s.state.active
    assert active["func:get_user_tasks"].value == "def get_user_tasks(uid)"
    assert active["user.location"].value == "Paris"
    old_sig = s.state.superseded_for("func:get_user_tasks")[0]
    assert old_sig.value == "def get_user_tasks(user_id)" and old_sig.superseded_at is not None
    assert old_sig.superseded_by == active["func:get_user_tasks"].fact_id
    assert s.state.superseded_for("user.location")[0].value == "London"


def test_rename_retires_old_symbol():
    s = HierarchicalSummarizer(config=SummarizationConfig(l1_span=1, tail_keep=0))
    for t in turns_from(
        [
            ("assistant", "```python\ndef fetch_tasks(uid):\n    pass\n```"),
            ("user", "Rename fetch_tasks to get_user_tasks."),
        ]
    ):
        s.ingest(t)
    assert "func:fetch_tasks" not in s.state.active
    assert "Retired symbols" in s.render_l1()


def test_tiers_and_structured_records():
    s = build()
    assert s.l1 and s.l2 and s.l3 is not None
    assert set(s.l1[0].model_dump()) >= {"facts", "entities", "constraints", "turn_range"}
    assert set(s.l2[0].model_dump()) >= {"intent", "decisions", "open_goals", "source_l1_ids"}
    assert set(s.l3.model_dump()) >= {"persona", "main_objective", "final_state", "source_l2_ids"}


def test_tier_falls_back_with_budget_and_loss_rises():
    s = build()
    big = s.build_context(make_signal(budget=400), "q")
    small = s.build_context(make_signal(budget=90), "q")
    assert big.quality.tier_emitted == "L1"
    assert small.quality.tier_emitted in ("L2", "L3")
    assert small.quality.loss_score > big.quality.loss_score
    assert small.quality.loss_threshold_exceeded == (small.quality.loss_score > LOSS_THRESHOLD)
    assert big.quality.symbol_retention_rate == 1.0
    assert small.quality.symbol_retention_rate == 0.0


def test_loss_score_detects_injected_degradation():
    turns = turns_from(CODE_SESSION)
    full = "def get_user_tasks(user_id) def get_user_tasks(uid) London Paris get_user_tasks"
    assert anchor_loss(turns, full)[0] < anchor_loss(turns, "Paris")[0] < anchor_loss(turns, "")[0]


def test_symbol_retention_none_without_code():
    turns = turns_from([("user", "I like hiking"), ("assistant", "Nice")])
    assert symbol_retention_rate(turns, "anything") is None


def test_naive_baseline_contract():
    n = NaiveSummarizer(tail_keep=2)
    for t in turns_from(CODE_SESSION):
        n.ingest(t)
    out = n.build_context(make_signal(budget=200), "q")
    assert out.module == "summarization" and out.token_count <= 200


def test_llm_generator_validates_and_falls_back():
    calls = []

    def bad_llm(system, user):
        calls.append(system[:20])
        return "not json"

    gen = LLMGenerator(bad_llm)
    s = HierarchicalSummarizer(generator=gen, config=SummarizationConfig(l1_span=2, tail_keep=2, l2_fanin=2))
    for t in turns_from(CODE_SESSION):
        s.ingest(t)
    assert calls and gen.failures > 0
    assert all(r.generator == "rule_based_fallback" for r in s.l1)
    assert s.state.active["func:get_user_tasks"].value == "def get_user_tasks(uid)"

    def good_llm(system, user):
        if "L1" in system or "EXTRACT VERBATIM" in system:
            return '{"facts": [{"key": "user.location", "value": "Paris", "kind": "attribute", "source_turn_id": "t0007"}], "entities": ["Paris"], "constraints": []}'
        if "L2" in system:
            return '{"intent": "relocation", "decisions": [], "open_goals": []}'
        return '{"persona": "dev", "main_objective": "ship", "final_state": "ok"}'

    s2 = HierarchicalSummarizer(generator=LLMGenerator(good_llm), config=SummarizationConfig(l1_span=2, tail_keep=2, l2_fanin=2))
    for t in turns_from(CODE_SESSION):
        s2.ingest(t)
    assert s2.l1[0].generator == "llm"
    # parser-derived signatures always override the model's copy
    assert s2.state.active["func:get_user_tasks"].value == "def get_user_tasks(uid)"
