"""Phase 1 evaluation protocol: families, splits, trace replay, conversation-level bootstrap."""

from collections import defaultdict

from contracts.text import HashingEmbedder
from controller import RuleBasedController
from eval.metrics import cluster_bootstrap_ci, required_hit
from eval.synthetic.controller.families import FAMILIES, SLOTS
from eval.synthetic.controller.generate import generate, generate_families, load_split, make_splits
from eval.synthetic.controller.trace import replay, trace_conversation
from integration import MemoryPipeline
from retrieval import RetrievalConfig


def test_families_are_deterministic_and_complete():
    a, b = generate_families(), generate_families()
    assert [c["messages"] for c in a] == [c["messages"] for c in b]
    for fam in FAMILIES.values():
        assert set(fam) == set(SLOTS)
    # evidence fields are carried verbatim by every template that needs them
    for fam in FAMILIES.values():
        assert all("{job}" in t for t in fam["intro"])
        assert all("{fix}" in t for t in fam["fix_reply"])
        assert all("{second_fix}" in t for t in fam["off_reply"])
        assert all("{city}" in t for t in fam["intro"])


def test_splits_are_disjoint_and_test_is_held_out_family():
    convs = generate_families()
    s = make_splits(convs)
    assert not set(s["train"]) & set(s["val"])
    assert not set(s["train"]) & set(s["test"])
    assert not set(s["val"]) & set(s["test"])
    fam = {c["id"]: c["family"] for c in convs}
    assert {fam[i] for i in s["test"]} == {"C"}
    assert "C" not in {fam[i] for i in s["train"] + s["val"]}
    assert {c["id"] for c in load_split("test")} == set(s["test"])


def test_structure_varies_so_pressure_is_not_constant():
    lengths = {len(c["messages"]) for c in generate_families()}
    assert len(lengths) > 5


def test_replay_matches_live_pipeline():
    """Replaying a recorded trace must give the same decisions and hits as running the pipeline live."""
    conv = generate()[0]
    emb = HashingEmbedder()
    trace = trace_conversation(conv, 400, emb, None)
    replayed = replay([trace], RuleBasedController)

    pipe = MemoryPipeline(conv["id"], token_budget=400, embedder=emb, nli=None,
                          retrieval_config=RetrievalConfig(check_contradictions=False))
    probes_at = defaultdict(list)
    for p in conv["probes"]:
        probes_at[p["after_index"]].append(p)
    live = []
    for i, m in enumerate(conv["messages"]):
        if m["role"] == "user":
            pipe.user_turn(m["content"], respond=False)
        else:
            pipe.assistant_turn(m["content"])
        for p in probes_at.get(i, []):
            r = pipe.user_turn(p["question"], remember=False, respond=False)
            live.append((r.decision.selected_strategy, required_hit(r.prompt.context, p["required"], p["stale"]), r.prompt.token_count))
    pipe.close()
    assert [(r["adaptive"], r["adaptive_hit"], r["adaptive_tokens"]) for r in replayed] == live


def test_cluster_bootstrap_resamples_groups():
    rows = [{"conv": f"c{i}", "x": float(i % 2)} for i in range(20) for _ in range(5)]
    out = cluster_bootstrap_ci(rows, lambda rs: sum(r["x"] for r in rs) / len(rs), n_boot=500)
    assert out["n_groups"] == 20
    assert out["ci_low"] <= out["estimate"] <= out["ci_high"]
    assert out["ci_high"] - out["ci_low"] > 0.1  # 20 clusters -> a wide interval, not a 100-row one
