"""CEAI chat: the everyday-user app. A normal AI chat where CEAI manages the memory.

    python -m console.chat                 # opens http://127.0.0.1:8800/
    python -m console.chat --port 8801 --no-browser

Every message goes through the real frozen system (``MemoryPipeline``). The page shows the reply,
which memory method was used and why, and lets the user choose the method for one message (the
controller's human override).

AI replies come from, in order:
  1. ``CEAI_LLM_BASE_URL`` / ``CEAI_LLM_MODEL`` / ``CEAI_LLM_API_KEY`` (any OpenAI-compatible API), or
  2. a local Ollama server on http://127.0.0.1:11434 (model from ``CEAI_CHAT_MODEL``, else the first
     qwen2.5 model, else the first installed model).
With neither, the app still works in memory-only mode and shows what it would send to the AI.

Single user, local only: it binds to 127.0.0.1 and keeps one conversation in memory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import threading
import time
import urllib.request
import warnings
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from contracts import OverrideRequest, count_tokens
from controller.rules import RULES, TurnCues
from eval.frozen import frozen_controller, system_name, system_retrieval
from integration import MemoryPipeline
from integration.llm_client import OpenAICompatibleLLM
from retrieval import RetrievalConfig

PAGE = Path(__file__).parent / "chat.html"
TURN_ID = re.compile(r"\bt\d{4,}\b")
STRATEGIES = ("sliding_window", "summarization", "rag", "hybrid")
NAME = {"sliding_window": "Recent messages", "summarization": "Summary", "rag": "Search", "hybrid": "Recent + search"}
BECAUSE = {
    "history_fits": "The whole conversation still fits, so it kept the recent messages. Nothing was left out.",
    "recall_question": "You asked about something from earlier, so it searched past messages for it.",
    "build_request": "You asked for new code, so it also searched for code that already exists, to avoid writing it twice.",
    "refactor_request": "You are changing existing code, so it used the summary, which keeps the current function signatures.",
    "debugging": "You are debugging, so the most recent messages matter most.",
    "recall_request": "You asked to recall something said earlier, so it searched past messages for it.",
    "long_open_conversation": "This is a long conversation that no longer fits, so the summary keeps the gist.",
    "hold": "Nothing new stood out, so it kept the same memory method as before.",
    "default": "It started with the recent messages.",
}
PERSONALITIES = {
    "helpful": "Be friendly and helpful.",
    "concise": "Answer as briefly as possible. No preamble.",
    "technical": "Be precise and technical. Prefer code and exact names.",
    "teacher": "Explain step by step, as to a student, and check understanding.",
    "creative": "Be imaginative and suggest unusual options.",
}
SECTION = re.compile(r"\n\n(?=\[[A-Z][^\]\n]*\]\n)")
# Replies are capped so a local CPU model answers in reasonable time; raise it for a hosted API.
REPLY_TOKENS = int(os.environ.get("CEAI_CHAT_MAX_TOKENS", "400"))


# ---------------------------------------------------------------------------------------- the AI
def _ollama_models(base: str = "http://127.0.0.1:11434") -> list[str]:
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=1.5) as r:
            return [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception:
        return []


def connect_ai() -> tuple[object | None, dict]:
    base = os.environ.get("CEAI_LLM_BASE_URL")
    if base:
        model = os.environ.get("CEAI_LLM_MODEL", "")
        if model:
            llm = OpenAICompatibleLLM(base, model, api_key=os.environ.get("CEAI_LLM_API_KEY"), max_tokens=REPLY_TOKENS,
                                      temperature=0.3, timeout_s=180, max_retries=1)
            return llm, {"connected": True, "model": model, "where": "API from CEAI_LLM_BASE_URL"}
    models = _ollama_models()
    if models:
        want = os.environ.get("CEAI_CHAT_MODEL")
        model = want if want in models else next((m for m in models if m.startswith("qwen2.5")), models[0])
        llm = OpenAICompatibleLLM("http://127.0.0.1:11434/v1", model, max_tokens=REPLY_TOKENS, temperature=0.3,
                                  timeout_s=300, max_retries=1)
        return llm, {"connected": True, "model": model, "where": "Ollama on this computer"}
    return None, {"connected": False, "model": None, "where": None}


def stream_ai(llm: OpenAICompatibleLLM, system: str, user: str, on_text, stop: threading.Event | None = None,
              on_reasoning=None) -> None:
    """Stream a reply from the same endpoint ``llm`` uses, calling ``on_text`` with each new piece.

    Reasoning models may send their thinking in a separate field; it goes to ``on_reasoning``.
    """
    body = json.dumps({"model": llm.model, "temperature": llm.temperature, "max_tokens": llm.max_tokens, "stream": True,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
    headers = {"Content-Type": "application/json"}
    if llm.api_key:
        headers["Authorization"] = f"Bearer {llm.api_key}"
    req = urllib.request.Request(llm.url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=llm.timeout_s) as resp:
        for raw in resp:
            if stop is not None and stop.is_set():
                return
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                return
            try:
                delta = json.loads(data)["choices"][0].get("delta") or {}
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
            thought = delta.get("reasoning_content") or delta.get("reasoning") or ""
            if thought and on_reasoning is not None:
                on_reasoning(thought)
            if delta.get("content"):
                on_text(delta["content"])


# ---------------------------------------------------------------------------------------- the chat
class ChatSession:
    def __init__(self, budget: int = 700):
        self.budget = budget
        self.personality: str | None = None
        self.lock = threading.Lock()
        print("Loading the memory models (about 20 s)...", flush=True)
        from integration.pipeline import default_embedder
        from retrieval.nli import CrossEncoderNLI
        from retrieval.rerank import DEFAULT_RERANKER

        self.embedder = default_embedder()
        self.nli = CrossEncoderNLI()
        self.retrieval = RetrievalConfig(**system_retrieval(reranker=DEFAULT_RERANKER))
        self.llm, self.ai = connect_ai()
        self.reset()

    def reset(self) -> None:
        old = getattr(self, "pipe", None)
        if old is not None:
            old.close()
        self.pipe = MemoryPipeline(f"chat-{int(time.time())}", token_budget=self.budget, embedder=self.embedder, nli=self.nli,
                                   controller=frozen_controller(), retrieval_config=self.retrieval)
        self.messages: list[dict] = []
        self.number_of: dict[str, int] = {}  # turn id -> message number shown to the user

    def reconnect(self) -> dict:
        self.llm, self.ai = connect_ai()
        return self.ai

    def use_model(self, model: str) -> dict:
        """Switch the AI model (same endpoint) for the following messages."""
        if self.llm is None:
            raise ValueError("no AI is connected")
        self.llm = OpenAICompatibleLLM(self.llm.url.rsplit("/chat/completions", 1)[0], model, api_key=self.llm.api_key,
                                       max_tokens=self.llm.max_tokens, temperature=self.llm.temperature,
                                       timeout_s=self.llm.timeout_s, max_retries=self.llm.max_retries)
        self.ai = {**self.ai, "model": model}
        return self.ai

    def models(self) -> list[str]:
        if self.ai.get("where") == "Ollama on this computer":
            return _ollama_models()
        return [self.ai["model"]] if self.ai.get("model") else []

    # replaying saved messages (resume, undo, retry) -------------------------------------------
    def exchanges(self) -> list[dict]:
        """The conversation as saved: what was typed, the reply and any per-message memory choice."""
        out, user = [], None
        for m in self.messages:
            if m["role"] == "user":
                user = m
            elif user is not None:
                choice = m["memory"]["strategy"] if m["memory"]["chosen_by"] == "you" else "auto"
                out.append({"user": user["text"], "reply": m["text"], "memory": choice, "at": user.get("at")})
                user = None
        return out

    def load(self, exchanges: list[dict]) -> None:
        """Rebuild memory from saved exchanges. No AI calls; the memory decisions come out the same."""
        self.reset()
        for ex in exchanges:
            turn = self.prepare(ex["user"], ex.get("memory", "auto"), at=ex.get("at"))
            self.finish(turn, ex.get("reply"))

    def undo(self) -> dict | None:
        """Remove the last exchange and return it."""
        ex = self.exchanges()
        if not ex:
            return None
        self.load(ex[:-1])
        return ex[-1]

    def side(self, text: str) -> dict:
        """A side question: answered with memory, but neither the question nor the answer is stored."""
        res = self.pipe.user_turn(text, remember=False, respond=False)
        return {"memory": self._explain(res, "auto"), "ask": self._ask(res, text)}

    def _ask(self, res, text: str) -> tuple[str, str]:
        system = res.prompt.system
        if self.personality in PERSONALITIES:
            system += " " + PERSONALITIES[self.personality]
        return system, f"[Memory context]\n{res.prompt.context}\n\n[Current message]\n{text}"

    # one user message ------------------------------------------------------------------------
    def send(self, text: str, memory: str = "auto", reply: str | None = None) -> dict:
        turn = self.prepare(text, memory)
        ai_error = None
        if reply is None and self.llm is not None:
            try:
                reply = self.llm(*turn["ask"]).strip()
            except Exception as e:  # network, model not loaded, timeout
                ai_error = f"The AI did not answer ({type(e).__name__}). Your message and memory are saved."
        return self.finish(turn, reply, ai_error)

    def prepare(self, text: str, memory: str = "auto", at: float | None = None) -> dict:
        """Step 1: the memory system picks a method and builds what the AI will be shown."""
        if memory in STRATEGIES:
            self.pipe.controller.request_override(OverrideRequest(strategy=memory, by="you", scope="next_turn"))
        res = self.pipe.user_turn(text, respond=False)
        n = len([m for m in self.messages if m["role"] == "user"]) + 1
        self.number_of[res.turn.turn_id] = n
        self.messages.append({"role": "user", "n": n, "text": text, "at": at or time.time()})
        return {"n": n, "memory": self._explain(res, memory), "ask": self._ask(res, text)}

    def finish(self, turn: dict, reply: str | None, ai_error: str | None = None) -> dict:
        """Step 3: store the reply (if any) so later messages can draw on it."""
        if reply:
            t = self.pipe.assistant_turn(reply)
            self.number_of[t.turn_id] = turn["n"]
        msg = {"role": "assistant", "n": turn["n"], "text": reply, "memory": turn["memory"], "ai_error": ai_error,
               "memory_only": reply is None and ai_error is None}
        self.messages.append(msg)
        return msg

    def _explain(self, res, chosen: str) -> dict:
        d, fv = res.decision, res.feature_vector
        parts = d.rationale.split(" | ")
        rule = parts[0][1:parts[0].index("]")] if parts[0].startswith("[") else ""
        notes = []
        for p in parts:
            if p.startswith("escalation") and "summary loss" in p and "->" in p:
                loss = p.split("summary loss ")[1].split(" ")[0]
                notes.append(f"The summary was losing {round(float(loss) * 100)}% of the details, so it switched to {NAME[d.selected_strategy]}.")
            elif p.startswith("escalation") and "stale chunk" in p:
                notes.append("Some earlier facts are out of date, so it also shows the newer ones.")
            elif p.startswith("dwell"):
                notes.append("It changed method very recently, so it kept the current one to stay steady.")
        ids = set(TURN_ID.findall(res.prompt.context)) | {t for v in res.prompt.sources.values() for t in v}
        drew_on = sorted({self.number_of[t] for t in ids if t in self.number_of})
        # What the matching rule alone would have picked; dwell or a warning can change it afterwards.
        cues = TurnCues(shift=res.signal.shift_detected, recall_request=res.signal.recall_request)
        hit = next((h for h in (r(fv, self.pipe.controller.config, cues) for r in RULES) if h is not None), None)
        by_rule = hit.strategy if hit else (fv.prior_strategy or self.pipe.controller.default_strategy)
        if d.override.applied:
            reason = f"You chose {NAME[d.selected_strategy]} for this message."
        elif by_rule != d.selected_strategy:
            reason = f"For a message like this it would normally use {NAME[by_rule]}. It used {NAME[d.selected_strategy]} instead:"
        else:
            reason = BECAUSE.get(rule, "")
        candidates = []
        for name, out in res.outputs.items():
            q = out.quality
            if name == "sliding_window":
                detail = f"{len(q.selected_turn_ids)} recent turns"
            elif name == "summarization":
                detail = f"tier {q.tier_emitted}, loss {q.loss_score:.2f}" + (" (over the limit)" if q.loss_threshold_exceeded else "")
            else:
                detail = f"{len(q.retrieved_chunk_ids)} matches" + (f", {len(q.contradiction_flags)} out of date"
                                                                    if q.contradiction_flags else "")
            candidates.append({"strategy": name, "name": NAME[name], "tokens": out.token_count,
                               "ms": round(out.readiness.estimated_latency_ms, 1), "detail": detail})
        sections = []
        for part in SECTION.split(res.prompt.context) if res.prompt.context else []:
            head = part.splitlines()[0]
            label = head.strip("[]") if head.startswith("[") and head.endswith("]") else NAME[d.selected_strategy]
            sections.append({"label": label, "tokens": count_tokens(part)})
        return {
            "candidates": candidates,
            "sections": sections,
            "system_tokens": count_tokens(res.prompt.system),
            "message_tokens": count_tokens(res.turn.content),
            "strategy": d.selected_strategy,
            "name": NAME[d.selected_strategy],
            "chosen_by": "you" if d.override.applied else "automatic",
            "reason": reason,
            "notes": [] if d.override.applied else notes,
            "drew_on": drew_on,
            "tokens": res.prompt.token_count,
            "budget": self.budget,
            "fill": round(min(1.0, fv.token_budget_pressure), 3),
            "context": res.prompt.context,
            "rationale": d.rationale,
            "ms": d.decision_latency_ms,
        }

    def sample(self, upto: int = 15) -> None:
        """Replay the first exchanges of the demo session, with its scripted replies."""
        from demo.coding_session.script import EXCHANGES

        self.reset()
        for user, reply in EXCHANGES[:upto]:
            self.send(user, reply=reply)

    def state(self) -> dict:
        return {"ai": self.ai, "system": system_name(), "budget": self.budget, "messages": self.messages}


# ---------------------------------------------------------------------------------------- the server
def make_handler(chat: ChatSession):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # keep the terminal quiet
            pass

        def _json(self, obj, status=200):
            body = json.dumps(obj).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            try:
                return json.loads(self.rfile.read(n) or b"{}")
            except json.JSONDecodeError:
                return {}

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                body = PAGE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif self.path == "/api/state":
                with chat.lock:
                    self._json(chat.state())
            else:
                self.send_error(404)

        def do_POST(self):
            data = self._body()
            with chat.lock:
                if self.path == "/api/send":
                    text = str(data.get("text", "")).strip()
                    if not text:
                        return self._json({"error": "Type a message first."}, 400)
                    memory = data.get("memory", "auto")
                    if memory != "auto" and memory not in STRATEGIES:
                        return self._json({"error": f"Unknown memory method {memory!r}."}, 400)
                    msg = chat.send(text[:8000], memory)
                    return self._json({"message": msg, "ai": chat.ai})
                if self.path == "/api/new":
                    chat.reset()
                    return self._json(chat.state())
                if self.path == "/api/sample":
                    chat.sample()
                    return self._json(chat.state())
                if self.path == "/api/connect":
                    chat.reconnect()
                    return self._json(chat.state())
            self.send_error(404)

    return Handler


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8800)
    ap.add_argument("--budget", type=int, default=700, help="memory budget in tokens")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    chat = ChatSession(args.budget)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(chat))
    url = f"http://127.0.0.1:{args.port}/"
    ai = chat.ai
    print(f"CEAI chat: {url}")
    print(f"AI replies: {ai['model']} ({ai['where']})" if ai["connected"] else
          "AI replies: off (memory-only). Start Ollama or set CEAI_LLM_BASE_URL, then press 'Check again' in the page.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        chat.pipe.close()


if __name__ == "__main__":
    main()
