"""Terminal chat: memory rows, commands, saved chats and reply streaming (no models, no real AI)."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from rich.console import Console

from console import sessions, tui
from console.chat import stream_ai
from integration.llm_client import OpenAICompatibleLLM
from tests.test_chat import make_session


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setenv("CEAI_HOME", str(tmp_path))
    out = Console(record=True, width=120, force_terminal=False)
    monkeypatch.setattr(tui, "console", out)
    a = tui.App(chat=make_session(monkeypatch))
    a.out = out
    a.confirm = lambda question, arg: True
    return a


def text(app) -> str:
    return app.out.export_text(clear=False)


def test_helpers():
    assert tui.ranges([1, 2, 5, 9, 12, 13, 14, 15]) == "1–2, 5, 9, 12–15"
    assert tui.ranges([]) == ""
    assert tui.split_think("<think>hmm</think>Answer") == ("hmm", "Answer")
    assert tui.split_think("<think>still thinking") == ("still thinking", "")
    assert tui.split_think("Plain") == ("", "Plain")


def test_message_memory_choice_and_commands(app):
    app.send("Write a helper to format due dates.")
    assert "memory  Recent messages" in text(app) and "AI is off" in text(app) and "message 1" in text(app)

    assert app.command("/memory search") and app.next_memory == "rag"
    app.send("what did we decide?")
    assert app.last()["memory"]["chosen_by"] == "you" and app.next_memory == "auto"  # lasts one message

    for c in ("/why", "/context", "/context all", "/track", "/history", "/status", "/usage", "/help", "/help memory",
              "/config", "/version", "/memory nope", "/nope", "/h", "/sessions", "/title", "/queue", "/copy 9"):
        assert app.command(c), c
    out = text(app)
    assert "Logged rationale" in out and "What the AI was shown" in out and "Unknown method" in out
    assert "Instructions to the AI" in out and "Did you mean" not in out
    assert app.toolbar()


def test_prefix_and_aliases(app):
    assert app.resolve("/h").name == "/help"
    assert app.resolve("/q").name == "/queue"  # the Hermes alias
    assert app.resolve("/exit").name == "/quit"
    assert app.resolve("/s") is None  # ambiguous
    assert not app.command("/quit")


def test_display_settings_persist(app, tmp_path):
    app.command("/verbose off")
    app.command("/skin ocean")
    app.command("/timestamps on")
    app.command("/personality concise")
    saved = json.loads((tmp_path / "config.json").read_text())
    assert saved["verbose"] == "off" and saved["skin"] == "ocean" and saved["timestamps"] is True
    assert app.chat.personality == "concise"
    app.send("hello")
    assert "memory  " not in text(app)  # verbose off hides the memory row
    app.command("/verbose")  # cycles to the next level
    assert app.settings["verbose"] == "new"


def test_save_undo_retry_branch_resume(app, tmp_path):
    for m in ("first message about the API", "second message", "third message"):
        app.send(m)
    sid = app.session["id"]
    stored = sessions.find(sid)
    assert len(stored["messages"]) == 3 and stored["title"].startswith("first message")

    app.command("/undo -y")
    assert len(app.chat.exchanges()) == 2 and app.prefill == "third message"
    app.command("/retry")  # replaces the last exchange with a fresh answer
    assert [e["user"] for e in app.chat.exchanges()] == ["first message about the API", "second message"]
    app.send("third message")

    app.command("/branch side idea")
    assert app.session["id"] != sid and app.session["title"] == "side idea"
    assert len(sessions.find("side idea")["messages"]) == 3

    app.command("/new -y")
    assert not app.chat.messages
    app.command(f"/resume {sid}")
    assert len(app.chat.exchanges()) == 3 and app.session["id"] == sid
    assert "Previous conversation" in text(app)

    app.command(f"/save {tmp_path / 'chat.md'}")
    assert "## 1. You" in (tmp_path / "chat.md").read_text(encoding="utf-8")


def test_side_question_is_not_remembered(app):
    app.send("we use postgres")
    before = len(app.chat.messages)
    app.command("/btw which database?")
    assert len(app.chat.messages) == before and "not remembered" in text(app)


def test_queue_and_paste_expansion(app):
    app.command("/queue first queued")
    app.command("/queue add second queued")
    assert app.queue == ["first queued", "second queued"]
    app.command("/queue rm 1")
    assert app.queue == ["second queued"]
    app.pastes["[pasted 9 lines #1]"] = "line\n" * 9
    app.send("look: [pasted 9 lines #1]")
    assert app.chat.exchanges()[-1]["user"].count("line") == 9


def _fake_ai(chunks, reasoning=()):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for r in reasoning:
                self.wfile.write(f"data: {json.dumps({'choices': [{'delta': {'reasoning': r}}]})}\n\n".encode())
            for c in chunks:
                self.wfile.write(f"data: {json.dumps({'choices': [{'delta': {'content': c}}]})}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")

    server = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def test_stream_reasoning_and_reply_is_remembered(app):
    server = _fake_ai(["Use the ", "existing `format_due_date`."], reasoning=["let me check memory"])
    try:
        llm = OpenAICompatibleLLM(f"http://127.0.0.1:{server.server_port}/v1", "fake")
        got, thought = [], []
        stream_ai(llm, "sys", "hi", got.append, on_reasoning=thought.append)
        assert "".join(got) == "Use the existing `format_due_date`." and thought == ["let me check memory"]

        app.chat.llm, app.chat.ai = llm, {"connected": True, "model": "fake", "where": "test"}
        app.send("Write a due date helper.")
        assert app.last()["text"] == "Use the existing `format_due_date`."
        assert "Thought for" in text(app) and "words" in text(app)
        assert app.usage.calls == 1 and app.usage.sent_tokens > 0
    finally:
        server.shutdown()


def test_keys_in_the_input_box(app):
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    with create_pipe_input() as inp:
        ask = app.make_prompt(inp, DummyOutput())
        inp.send_text("hello\r")
        assert ask() == "hello"
        inp.send_text("one\\\rtwo\r")  # a trailing backslash continues the line
        assert ask() == "one\ntwo"
        inp.send_text("draft\x13\x13\r")  # Ctrl+S puts the draft aside, again brings it back
        assert ask() == "draft"
        inp.send_text("\x1b[200~" + "l\n" * 6 + "\x1b[201~\r")  # a long paste folds into a placeholder
        line = ask()
        assert line.startswith("[pasted") and app.expand(line).count("l") == 6
        inp.send_text("junk\x03\x03\x03")  # Ctrl+C clears, then twice on empty quits
        with pytest.raises(EOFError):
            ask()
    assert app.prompt_session.bottom_toolbar is not None


def test_banner_wide_and_narrow(app, monkeypatch):
    app.banner()  # 120 columns: title, mark and the two-column panel
    out = text(app)
    assert "███████╗" in out and f"Syno v{tui.VERSION}" in out and "Memory methods" in out
    assert "Available Commands" in out and f"Session: {app.session['id']}" in out and "AI is off" in out
    narrow = Console(record=True, width=30, force_terminal=False)
    monkeypatch.setattr(tui, "console", narrow)
    app.banner()  # too narrow for the block title: falls back to one line, panel stacks
    assert "◈ SYNO" in narrow.export_text() and "███████╗" not in narrow.export_text(clear=False)
