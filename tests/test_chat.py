"""Everyday chat app: messages, explanations and the per-message memory choice (no models, no AI)."""

from contracts.text import HashingEmbedder
from console import chat as chat_mod
from eval.frozen import frozen_controller
from integration import MemoryPipeline
from retrieval import RetrievalConfig


def make_session(monkeypatch) -> chat_mod.ChatSession:
    s = chat_mod.ChatSession.__new__(chat_mod.ChatSession)
    s.budget, s.llm, s.ai = 700, None, {"connected": False, "model": None, "where": None}
    import threading

    s.lock = threading.Lock()
    monkeypatch.setattr(chat_mod.ChatSession, "reset", lambda self: _reset(self))
    s.reset()
    return s


def _reset(self):
    self.pipe = MemoryPipeline("t", token_budget=self.budget, embedder=HashingEmbedder(), controller=frozen_controller(),
                               retrieval_config=RetrievalConfig(check_contradictions=False))
    self.messages, self.number_of = [], {}


def test_memory_only_reply_explains_itself(monkeypatch):
    s = make_session(monkeypatch)
    msg = s.send("Write a helper to format due dates.")
    assert msg["memory_only"] and msg["text"] is None
    mem = msg["memory"]
    assert mem["strategy"] == "sliding_window" and mem["chosen_by"] == "automatic"
    assert mem["reason"] and mem["budget"] == 700


def test_user_can_choose_memory_for_one_message(monkeypatch):
    s = make_session(monkeypatch)
    s.send("hello", reply="hi")
    chosen = s.send("now remind me", memory="rag", reply="ok")["memory"]
    assert chosen["strategy"] == "rag" and chosen["chosen_by"] == "you"
    after = s.send("and again", reply="ok")["memory"]
    assert after["chosen_by"] == "automatic"  # the choice lasts one message


def test_reason_matches_the_method_used(monkeypatch):
    from demo.coding_session.script import EXCHANGES

    s = make_session(monkeypatch)
    for user, reply in EXCHANGES[:15]:
        mem = s.send(user, reply=reply)["memory"]
        if "normally use" not in mem["reason"]:
            continue
        assert mem["notes"], "a changed choice must say why it changed"
