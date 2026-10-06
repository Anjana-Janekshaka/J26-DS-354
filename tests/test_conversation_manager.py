from contracts import TurnSignal, count_tokens
from conversation_manager import ConversationManager, SignalBus, TaskTypeClassifier


def test_turn_counter_tokens_and_bus(embedder):
    bus = SignalBus()
    seen = []
    bus.subscribe(seen.append)
    cm = ConversationManager("c1", token_budget=200, bus=bus, embedder=embedder)
    a = cm.observe("user", "How does the task API work?")
    b = cm.observe("assistant", "It is a Flask app with three routes.")
    assert [s.turn_id for s in seen] == ["t0001", "t0002"]
    assert b.signal.turn_count == 2
    assert b.signal.token_usage.used == count_tokens(a.turn.render()) + count_tokens(b.turn.render())
    assert b.signal.token_usage.budget == 200
    assert isinstance(a.signal, TurnSignal)


def test_task_type_patterns():
    c = TaskTypeClassifier()
    cases = {
        "I get a KeyError traceback when loading the page": "debugging",
        "Rename get_tasks to get_user_tasks everywhere": "code_refactor",
        "Write a helper that formats due dates": "code_generation",
        "What did we decide about the cache earlier?": "qa",
        "When did Caroline go to the support group?": "qa",
        "Explain how the scheduler works": "exploration",
    }
    for text, expected in cases.items():
        assert c.classify_phrasing(text)[0] == expected, text


def test_task_type_carries_over_and_shift_detected(embedder):
    cm = ConversationManager("c1", token_budget=500, embedder=embedder)
    cm.observe("user", "Write a function to parse invoices from csv files")
    cm.observe("assistant", "def parse_invoices(path): ...")
    third = cm.observe("user", "and handle empty invoices csv rows too")
    assert third.signal.task_type == "code_generation"  # carry-over
    cm.observe("assistant", "Done, empty invoice rows are skipped.")
    shifted = cm.observe("user", "Switching gears: what is a good recipe for banana bread?")
    assert shifted.signal.shift_detected
    after = cm.observe("assistant", "Mash bananas, mix flour.")
    assert after.signal.conversation_state == "task-2"


def test_probe_does_not_commit(embedder):
    bus = SignalBus()
    seen = []
    bus.subscribe(seen.append)
    cm = ConversationManager("c1", token_budget=500, bus=bus, embedder=embedder)
    cm.observe("user", "hello there friend")
    before = (cm.turn_count, cm.tokens_used, len(cm.turns))
    probe = cm.probe("When did we talk about the budget?")
    assert probe.signal.turn_id == "t0002.p1"
    assert probe.signal.task_type == "qa"
    assert (cm.turn_count, cm.tokens_used, len(cm.turns)) == before
    assert len(seen) == 1  # probes are not broadcast
    nxt = cm.observe("user", "next real message")
    assert nxt.signal.turn_id == "t0002"
