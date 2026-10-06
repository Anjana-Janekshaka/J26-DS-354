import numpy as np
import pytest

from contracts import ConversationTurn
from retrieval import BoundaryConfig, ContradictionConfig, RetrievalConfig, RetrievalEngine, VectorIndex, decide_boundary

from conftest import CODE_SESSION, make_signal, turns_from


def engine(embedder, nli, mode="adaptive"):
    r = RetrievalEngine(embedder, nli, RetrievalConfig(mode=mode, min_score=0.0))
    for t in turns_from(CODE_SESSION):
        r.ingest(t)
    return r


def test_faiss_index_add_search_remove():
    idx = VectorIndex(4)
    v = np.eye(4, dtype=np.float32)
    idx.add([10, 11, 12], v[:3])
    assert idx.search(v[1], 1)[0][0] == 11
    idx.remove([11])
    assert all(i != 11 for i, _ in idx.search(v[1], 3))


def test_signature_diff_flags_stale_code_and_pulls_superseder(embedder, nli):
    r = engine(embedder, nli)
    old = r.chunks[r.resolve("turn:t0002")]
    assert old.superseded_by is not None and old.verifier == "signature_diff"
    out = r.build_context(make_signal(budget=400), "get_user_tasks user_id")
    q = out.quality
    assert out.module == "rag"
    flagged = {f.chunk_id for f in q.contradiction_flags}
    assert r.resolve("turn:t0002") in flagged
    assert r.resolve(old.superseded_by) in q.retrieved_chunk_ids  # superseder pulled in
    assert "[!] stale" in out.candidate_context


def test_nli_stage_flags_prose_contradiction(embedder, nli):
    # The lexical test embedder sees no overlap between "London" and "Paris" sentences, so open the
    # prefilter fully here; this test is about the NLI stage, not the prefilter.
    cfg = RetrievalConfig(min_score=0.0, contradiction=ContradictionConfig(topic_threshold=-1.0, sentence_threshold=-1.0))
    r = RetrievalEngine(embedder, nli, cfg)
    for t in turns_from(CODE_SESSION):
        r.ingest(t)
    london = next(c for c in r.chunks.values() if "London" in c.text and c.active)
    assert london.superseded_by is not None and london.verifier == "nli"
    assert nli.calls > 0


def test_prefilter_skips_unrelated_pairs(embedder, nli):
    r = RetrievalEngine(embedder, nli, RetrievalConfig())
    for t in turns_from([("user", "I live in London these days."), ("user", "The quarterly revenue report is due Friday afternoon.")]):
        r.ingest(t)
    assert r.checker.pairs_verified == 0


def test_granularity_modes(embedder, nli):
    turn_mode = engine(embedder, nli, "turn")
    assert all(c.granularity == "turn" for c in turn_mode.chunks.values() if c.active)
    seg_mode = engine(embedder, nli, "segment")
    assert any(c.granularity == "segment" for c in seg_mode.chunks.values() if c.active)
    adaptive = engine(embedder, nli, "adaptive")
    decisions = [d.reason for _, d in adaptive.boundary_log]
    assert "code_definition_isolated" in decisions


def test_boundary_score_monotone_in_semantic_drop():
    cfg = BoundaryConfig()
    a = np.array([1, 0], dtype=np.float32)
    same = decide_boundary("adaptive", cfg, [a], 10, a, 10, False, False, False)
    diff = decide_boundary("adaptive", cfg, [a], 10, np.array([0, 1], dtype=np.float32), 10, False, False, False)
    assert diff.probability > same.probability and diff.boundary and not same.boundary


def test_budget_respected(embedder, nli):
    r = engine(embedder, nli)
    out = r.build_context(make_signal(budget=40), "tasks")
    assert out.token_count <= 40


@pytest.mark.models
def test_real_models_flag_relocation():
    r = RetrievalEngine()
    for i, text in enumerate(["I live in London and work at Acme.", "Lovely, London is great.", "Actually I moved to Paris last month."]):
        r.ingest(ConversationTurn(turn_id=f"t{i + 1:04d}", role="user", content=text))
    out = r.build_context(make_signal(budget=300), "where does the user live")
    assert out.quality.contradiction_flags
