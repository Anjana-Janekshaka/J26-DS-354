from conversation_manager import TaskTypeClassifier
from eval.metrics import evidence_hit, macro_f1, ndcg_at_k, oracle_label, required_hit
from summarization import HierarchicalSummarizer, SummarizationConfig

from conftest import make_signal, turns_from


def test_question_about_known_entity_is_recall():
    c = TaskTypeClassifier()
    c.observe("Yesterday Caroline went to the support group with Melanie.", decision_point=False)
    assert c.classify_phrasing("What is Caroline's identity?")[0] == "qa"
    assert c.classify_phrasing("What is a closure in Python?")[0] == "exploration"


def test_required_hit_stale_marking():
    ctx = "- def f(uid) (t9; supersedes \"def f(user_id)\" from t2)"
    assert required_hit(ctx, ["def f(uid"], ["f(user_id"])
    assert not required_hit("def f(uid)\ndef f(user_id)", ["def f(uid"], ["f(user_id"])
    blocks = "[chunk a]\ndef f(user_id)\n[!] stale: superseded by b\n\n---\n\n[chunk b]\ndef f(uid)"
    assert required_hit(blocks, ["def f(uid"], ["f(user_id"])


def test_oracle_label_buckets_and_preference():
    hits = {"sliding_window": True, "summarization": False, "rag": True, "hybrid": True}
    assert oracle_label(hits, {"sliding_window": 990, "summarization": 0, "rag": 960, "hybrid": 850}, 1000) == "hybrid"
    assert oracle_label(hits, {"sliding_window": 990, "summarization": 0, "rag": 985, "hybrid": 995}, 1000) == "sliding_window"
    assert oracle_label({s: False for s in hits}, {s: 1 for s in hits}, 1000) == "none"


def test_metric_basics():
    assert evidence_hit(["Caroline went hiking in Oregon"], "caroline hiking oregon trip")[1]
    assert ndcg_at_k([1, 0, 0], 1, 10) == 1.0 and ndcg_at_k([0, 1], 1, 10) < 1.0
    f1, _ = macro_f1(["a", "b", "a"], ["a", "b", "b"])
    assert 0 < f1 < 1


def test_eager_merge_and_cross_tier_annotation():
    msgs = [("user", "I live in London these days."), ("assistant", "ok")]
    msgs += [("user", f"Filler sentence number {i} about Kubernetes clusters and Helm charts.") for i in range(14)]
    msgs += [("user", "I just moved to Paris last week.")]
    s = HierarchicalSummarizer(config=SummarizationConfig(l1_span=4, tail_keep=2, l2_fanin=2))
    for t in turns_from(msgs):
        s.ingest(t)
    assert s.state.active["user.location"].value == "Paris"  # merged while still in the raw tail
    text = s.render_l2()
    for line in text.splitlines():
        if "London" in line:
            assert "superseded" in line


def test_coarse_tier_fills_budget_with_keyed_facts_first():
    msgs = [("assistant", "```python\ndef get_rows(path, limit):\n    ...\n```")]
    msgs += [("user", f"Long note {i}: the Helm chart for service {i} pins image tags and resource limits carefully.") for i in range(30)]
    s = HierarchicalSummarizer(config=SummarizationConfig(l1_span=4, tail_keep=2, l2_fanin=2))
    for t in turns_from(msgs):
        s.ingest(t)
    out = s.build_context(make_signal(budget=260), "q")
    assert out.quality.tier_emitted in ("L2", "L3")
    assert "def get_rows(path, limit)" in out.candidate_context
    assert out.quality.symbol_retention_rate == 1.0
