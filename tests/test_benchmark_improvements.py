from contracts import ConversationTurn, EscalationEvent, utcnow
from contracts.text import BLOCK_TURNS
from controller import RuleBasedController, RuleConfig
from controller.rules import RuleHit, apply_escalations
from retrieval import RetrievalConfig, RetrievalEngine

from conftest import make_signal


def turns(texts):
    return [ConversationTurn(turn_id=f"t{i + 1:04d}", role="user", content=t) for i, t in enumerate(texts)]


HISTORY = [
    "We adopted a rescue greyhound called Biscuit last spring.",
    "That's lovely, how is she settling in?",
    "She sleeps on the sofa all day and hates the rain.",
    "The quarterly tax filing is due at the end of the month.",
    "Remember to export the invoices before filing.",
]


def engine(embedder, **cfg):
    r = RetrievalEngine(embedder, None, RetrievalConfig(mode="turn", check_contradictions=False, min_score=0.0, **cfg))
    for t in turns(HISTORY):
        r.ingest(t)
    return r


def test_compact_headers_keep_turn_ids_parseable(embedder):
    ctx = engine(embedder).build_context(make_signal(budget=400), "greyhound Biscuit").context_text()
    first = ctx.splitlines()[0]
    assert first.startswith("[turns: t") and "score" not in first
    assert BLOCK_TURNS.search(ctx)
    verbose = engine(embedder, compact_headers=False).build_context(make_signal(budget=400), "greyhound Biscuit").context_text()
    assert verbose.startswith("[chunk ") and len(verbose.splitlines()[0]) > len(first)


def test_neighbors_add_adjacent_turns_once(embedder):
    out = engine(embedder, neighbors=1).build_context(make_signal(budget=600), "greyhound Biscuit")
    ctx = out.context_text()
    assert "That's lovely" in ctx  # the reply after the matching turn rides along
    assert ctx.count("That's lovely") == 1  # and is not repeated as its own block


class FakeReranker:
    def __init__(self, favourite):
        self.favourite = favourite

    def score(self, query, passages):
        return [1.0 if self.favourite in p else 0.1 for p in passages]


def test_reranker_reorders_candidates(embedder):
    r = engine(embedder)
    r._reranker = FakeReranker("invoices")
    out = r.build_context(make_signal(budget=400), "greyhound Biscuit")
    assert "invoices" in out.context_text().split("\n\n---\n\n")[0]


def test_routing_options_change_choice_and_escalation():
    hit = RuleHit("long_open_conversation", "summarization", "x", hard=False)
    ev = EscalationEvent(event_id="e1", conversation_id="c", source_turn_id="t0001", source_module="summarization",
                         kind="loss_threshold_exceeded", detail={"loss_score": 0.4}, raised_at=utcnow())
    assert apply_escalations(hit, [ev])[0] == "rag"  # default unchanged
    assert apply_escalations(hit, [ev], RuleConfig(loss_escalation_target="hybrid"))[0] == "hybrid"

    ctl = RuleBasedController(RuleConfig(long_chat_strategy="hybrid"))
    _, d = ctl.decide(make_signal(task_type="chat", used=900, budget=1000))
    assert d.selected_strategy == "hybrid" and "hybrid keeps the recent window" in d.rationale


def test_stream_schedule_places_questions_after_evidence_session():
    from eval.locomo.loader import LocomoConversation, LocomoQA, LocomoTurn
    from eval.locomo.stream import schedule

    conv = LocomoConversation("c1", ("A", "B"))
    for s in (1, 2, 3):
        conv.turns.append(LocomoTurn(f"D{s}:1", "A", f"session {s}", s, "1 May 2023"))
    conv.qa = [LocomoQA(f"q{i}", "a", ["D1:1"], 4) for i in range(40)] + [LocomoQA("no evidence", "a", [], 5)]
    due = schedule(conv, seed=0)
    positions = [(s, p) for s, items in due.items() for p, _ in items]
    assert sum(len(v) for v in due.values()) == 40  # questions without evidence are skipped
    assert {p for _, p in positions} == {"fresh", "late"}
    assert all((s == 1) if p == "fresh" else (s == 3) for s, p in positions)


def test_reranker_skipped_for_code_tasks(embedder):
    r = engine(embedder)
    r._reranker = FakeReranker("invoices")
    prose = r.build_context(make_signal(budget=400, task_type="qa"), "greyhound Biscuit").context_text()
    code = r.build_context(make_signal(budget=400, task_type="code_generation"), "greyhound Biscuit").context_text()
    assert "invoices" in prose.split("\n\n---\n\n")[0]  # reranked
    assert "invoices" not in code.split("\n\n---\n\n")[0]  # bi-encoder order kept for code tasks


def test_bm25_splits_identifiers_and_ranks_exact_terms():
    from retrieval.lexical import BM25Index, lexical_terms, reciprocal_rank_fusion

    assert {"get", "user", "tasks"} <= set(lexical_terms("call get_user_tasks(uid) please"))
    idx = BM25Index()
    idx.add("a", "def get_user_tasks(uid): return db.query(uid)")
    idx.add("b", "We talked about the weekend hiking trip.")
    idx.add("c", "The dashboard shows an empty task list.")
    assert idx.search("get_user_tasks", 3)[0][0] == "a"
    idx.remove("a")
    assert all(d != "a" for d, _ in idx.search("get_user_tasks", 3))
    fused = reciprocal_rank_fusion([["x", "y"], ["y", "z"]])
    assert max(fused, key=fused.get) == "y"  # ranked by both lists


def test_hybrid_and_mmr_are_off_by_default_and_change_nothing(embedder):
    base = engine(embedder).build_context(make_signal(budget=400), "invoices filing").context_text()
    assert RetrievalConfig().hybrid is False and RetrievalConfig().mmr_lambda is None
    same = engine(embedder, hybrid=False, mmr_lambda=None).build_context(make_signal(budget=400), "invoices filing").context_text()
    assert base == same


def test_hybrid_surfaces_exact_identifier_match(embedder):
    r = RetrievalEngine(embedder, None, RetrievalConfig(mode="turn", check_contradictions=False, hybrid=True))
    for t in turns(HISTORY + ["Added format_due_date(dt, tz) to app/services/tasks.py."]):
        r.ingest(t)
    ctx = r.build_context(make_signal(budget=200, task_type="code_generation"), "format_due_date").context_text()
    assert "format_due_date" in ctx.split("\n\n---\n\n")[0]


def test_mmr_keeps_all_candidates_and_demotes_duplicates(embedder):
    dup = HISTORY + ["We adopted a rescue greyhound called Biscuit last spring."]
    r = RetrievalEngine(embedder, None, RetrievalConfig(mode="turn", check_contradictions=False, min_score=0.0, mmr_lambda=0.3))
    for t in turns(dup):
        r.ingest(t)
    results = r.search("greyhound Biscuit", 10)
    reordered = r._mmr(results, 0.3)
    assert {c.chunk_id for c, _ in reordered} == {c.chunk_id for c, _ in results}
    top2 = [c.text for c, _ in reordered[:2]]
    assert not (("greyhound" in top2[0]) and ("greyhound" in top2[1]))  # the near-duplicate is not second


def test_hybrid_only_for_listed_task_types(embedder):
    r = RetrievalEngine(embedder, None, RetrievalConfig(mode="turn", check_contradictions=False, hybrid_task_types=("qa",)))
    for t in turns(HISTORY + ["Added format_due_date(dt, tz) to app/services/tasks.py."]):
        r.ingest(t)
    calls = []
    real = r._candidates
    r._candidates = lambda q, k, use_lexical=True: (calls.append(use_lexical), real(q, k, use_lexical))[1]
    r.build_context(make_signal(budget=200, task_type="qa"), "format_due_date")
    r.build_context(make_signal(budget=200, task_type="chat"), "format_due_date")
    assert calls == [True]  # qa uses the fused path; chat keeps the plain dense search


def test_observations_link_to_source_turn_and_dedupe(embedder):
    from integration import MemoryPipeline

    p = MemoryPipeline("t", 300, embedder=embedder,
                       retrieval_config=RetrievalConfig(check_contradictions=False, observations=True, min_score=0.0))
    for t in HISTORY:
        p.add_turn("user", t, metadata={"date": "8 May 2023"})
    rag = p.modules["rag"]
    obs = [c for c in rag.chunks.values() if c.granularity == "observation"]
    assert obs and all(len(c.turns) == 1 and c.text.startswith("[8 May 2023] user:") for c in obs)
    ctx = rag.build_context(make_signal(budget=400, task_type="qa"), "greyhound Biscuit").context_text()
    blocks = ctx.split("\n\n---\n\n")
    ids = [b.splitlines()[0] for b in blocks]
    assert len(ids) == len(set(ids))  # a turn is never shown twice (as observation and as turn chunk)


def test_frozen_system_has_no_v3_options():
    from eval.frozen import SYSTEMS

    assert SYSTEMS["frozen"] == {} and SYSTEMS["v3_qa_hybrid_obs"] == {"hybrid_task_types": ("qa",), "observations": True}
