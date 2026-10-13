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
