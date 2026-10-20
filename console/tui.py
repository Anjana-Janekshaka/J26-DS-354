"""CEAI in the terminal: a chat where CEAI manages the memory, laid out like the Hermes agent CLI.

    python -m console.tui                     # new chat
    python -m console.tui -c                  # continue the most recent chat
    python -m console.tui -r <number|id|title>
    python -m console.tui -q "one question"   # answer once and exit (-q - reads stdin)
    python -m console.tui --model qwen2.5:7b --budget 1000

Enter sends. Alt+Enter, Ctrl+J or a trailing \\ adds a new line. Type / for commands (Tab
completes, Ctrl+P opens the list). Ctrl+C stops a reply or clears the input (twice on an empty
input quits). Ctrl+D quits. !<command> runs a shell command. Chats are saved in ~/.ceai.
"""

from __future__ import annotations

import os

# Keep model-loading progress bars and hub notices off the chat screen.
for _k, _v in {"HF_HUB_DISABLE_PROGRESS_BARS": "1", "HF_HUB_VERBOSITY": "error", "TRANSFORMERS_VERBOSITY": "error",
               "TRANSFORMERS_NO_ADVISORY_WARNINGS": "1", "TOKENIZERS_PARALLELISM": "false"}.items():
    os.environ.setdefault(_k, _v)

import argparse
import platform
import re
import subprocess
import sys
import threading
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from console import sessions
from console.chat import NAME, PERSONALITIES, STRATEGIES, ChatSession, stream_ai
from contracts import count_tokens

VERSION = "0.2"
COLOR = {"sliding_window": "cyan", "summarization": "magenta", "rag": "yellow", "hybrid": "green"}
HEX = {"sliding_window": "#56b6c2", "summarization": "#c678dd", "rag": "#e5c07b", "hybrid": "#98c379"}
SHORT = {"recent": "sliding_window", "summary": "summarization", "search": "rag", "both": "hybrid"}
SHORT_HELP = {"auto": "let CEAI choose (default)", "recent": "Recent messages", "summary": "Summary",
              "search": "Search earlier messages", "both": "Recent + search"}
SKINS = {
    "ceai": {"accent": "green", "hex": "#98c379", "bar": "#202020"},
    "ocean": {"accent": "bright_blue", "hex": "#61afef", "bar": "#1b2230"},
    "amber": {"accent": "dark_orange", "hex": "#d19a66", "bar": "#2a2018"},
    "mono": {"accent": "white", "hex": "#dddddd", "bar": "#262626"},
}
INDICATORS = {
    "kaomoji": (["(｡•́︿•̀｡)", "( ˘▽˘)っ", "(◕‿◕✿)", "ヽ(°〇°)ﾉ", "( •̀ω•́ )✧", "(・_・ヾ"], 1.6),
    "emoji": (["🧠", "💭", "📚", "✨"], 3.0),
    "unicode": (list("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"), 12.0),
    "ascii": (list("|/-\\"), 8.0),
}
VERBOSE = ["off", "new", "all", "verbose"]
VERBOSE_HELP = {"off": "replies only", "new": "memory row only when the method changes", "all": "memory row, reason and notes",
                "verbose": "also the three prepared methods and the logged rationale"}
YES = {"-y", "--yes", "now"}
THINK = re.compile(r"\s*<think>(.*?)(</think>|$)(.*)", re.S)
EXAMPLES = [
    "/sample, then: Write a helper that formats a task's due date for the email digest.",
    "/sample, then: Call get_user_tasks for the current user in the new endpoint.",
    "Or just start chatting. CEAI remembers as the conversation grows.",
]

console = Console(highlight=False)


# ------------------------------------------------------------------------------------- helpers
def ranges(nums: list[int]) -> str:
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}–{nums[j]}")
        i = j + 1
    return ", ".join(out)


def split_think(raw: str) -> tuple[str, str]:
    """(thinking, answer) from a reply that may start with a <think> block."""
    m = THINK.match(raw)
    if not m:
        return "", raw
    return m.group(1), m.group(3) if m.group(2) else ""


def ago(t: float) -> str:
    s = max(0, time.time() - t)
    for unit, n in (("d", 86400), ("h", 3600), ("m", 60)):
        if s >= n:
            return f"{int(s // n)}{unit} ago"
    return "just now"


def duration(s: float) -> str:
    s = int(s)
    return f"{s // 3600}h {s % 3600 // 60}m" if s >= 3600 else f"{s // 60}m {s % 60}s" if s >= 60 else f"{s}s"


def gutter(mark: Text, body) -> Table:
    """A row with a one-character mark on the left, like the Hermes 'modern' layout."""
    grid = Table.grid(padding=(0, 1))
    grid.add_column(width=1, no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_row(mark, body)
    return grid


def copy_to_clipboard(text: str) -> bool:
    try:
        if sys.platform == "win32":
            subprocess.run(["clip"], input=text.encode("utf-16"), check=True)
        elif sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
        else:
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


class Busy:
    """A busy indicator that animates on every refresh (style set by /indicator)."""

    def __init__(self, app: "App", label: Callable[[], str]):
        self.app, self.label, self.t0 = app, label, time.time()

    def __rich__(self):
        frames, fps = INDICATORS.get(self.app.settings["indicator"], INDICATORS["unicode"])
        frame = frames[int((time.time() - self.t0) * fps) % len(frames)]
        return Text.assemble((frame + " ", self.app.accent), (self.label(), "dim"))


@dataclass
class Command:
    name: str
    group: str
    help: str
    run: Callable[[str], object]
    args: str = ""
    aliases: tuple[str, ...] = ()
    choices: Callable[[], list[tuple[str, str]]] | None = None


@dataclass
class Usage:
    calls: int = 0
    seconds: float = 0.0
    words: int = 0
    sent_tokens: int = 0
    memory_ms: list[float] = field(default_factory=list)


# ------------------------------------------------------------------------------------- the app
class App:
    def __init__(self, budget: int = 700, model: str | None = None, chat: ChatSession | None = None):
        if model:
            os.environ["CEAI_CHAT_MODEL"] = model
        self.settings = sessions.load_settings()
        self.started = time.time()
        self.next_memory = "auto"
        self.queue: list[str] = []
        self.stash: list[str] = []
        self.pastes: dict[str, str] = {}
        self.prefill = ""
        self.usage = Usage()
        self.last_ctrl_c = 0.0
        self.prompt_session = None
        self.quit_delete = False
        if chat is None:
            with Live(Busy(self, lambda: "Loading the memory models (about 20 s)…"), console=console, transient=True):
                chat = ChatSession(budget)
        self.chat = chat
        self.chat.personality = self.settings.get("personality")
        self.session = self.fresh_session()
        self.commands = self.build_commands()

    # ---------------------------------------------------------------- settings and sessions
    @property
    def accent(self) -> str:
        return SKINS.get(self.settings["skin"], SKINS["ceai"])["accent"]

    def set(self, key: str, value) -> None:
        self.settings[key] = value
        sessions.save_settings(self.settings)

    def fresh_session(self, title: str | None = None) -> dict:
        return {"id": sessions.new_id(), "title": title, "created": time.time(), "budget": self.chat.budget}

    def save_session(self) -> None:
        ex = self.chat.exchanges()
        if not ex and not self.session.get("title"):
            return
        if not self.session.get("title") and ex:
            words = ex[0]["user"].split()
            self.session["title"] = " ".join(words[:6]) + ("…" if len(words) > 6 else "")
        self.session.update(messages=ex, model=self.chat.ai.get("model"), budget=self.chat.budget)
        sessions.save(self.session)

    def open_session(self, s: dict) -> None:
        ex = s.get("messages", [])
        with Live(Busy(self, lambda: f"Rebuilding memory from {len(ex)} messages (no AI calls)…"), console=console,
                  transient=True):
            self.chat.load(ex)
        self.session = s
        self.next_memory = "auto"
        console.print(Text.assemble(("Resumed ", "dim"), (s.get("title") or s["id"], f"bold {self.accent}"),
                                    (f"  {len(ex)} messages, last used {ago(s.get('updated', time.time()))}", "dim")))
        recent = ex[-3:]
        if recent:
            body = Group(*[Group(Text.assemble(("❯ ", self.accent), (e["user"].splitlines()[0][:110], ""))
                                 , Text("  " + (e["reply"] or "(no reply)").replace("\n", " ")[:110], style="dim"))
                           for e in recent])
            console.print(Panel(body, title="Previous conversation", title_align="left", border_style="grey37"))
        self.track()
        console.print()

    # ---------------------------------------------------------------- screen parts
    def banner(self) -> None:
        ai = self.chat.ai
        logo = Text.assemble(("◈ CEAI", f"bold {self.accent}"), ("  memory that changes method, message by message", "dim"))
        rows = Table.grid(padding=(0, 2))
        rows.add_column(style="dim", no_wrap=True)
        rows.add_column()
        rows.add_row("AI", f"{ai['model']}  [dim]{ai['where']}[/]" if ai["connected"] else
                     "[yellow]off[/]  [dim]memory-only: start Ollama or set CEAI_LLM_*, then /connect[/]")
        rows.add_row("Memory", f"{self.chat.state()['system']} system  [dim]│[/]  {self.chat.budget}-token budget  [dim]│[/]  "
                     + "  ".join(f"[{COLOR[s]}]●[/] {NAME[s]}" for s in STRATEGIES))
        if self.chat.personality:
            rows.add_row("Style", self.chat.personality)
        rows.add_row("Folder", str(Path.cwd()))
        rows.add_row("Keys", "[dim]Enter sends · Alt+Enter new line · / commands · Ctrl+P list · Ctrl+C stop · Ctrl+D quit[/]")
        console.print(Panel(Group(logo, Text(), rows), border_style=self.accent, padding=(0, 1)))
        if not self.chat.messages:
            console.print("[dim]Try:[/]")
            for e in EXAMPLES:
                console.print(f"  [dim]›[/] {e}")
        console.print()

    def last(self) -> dict | None:
        return next((m for m in reversed(self.chat.messages) if m["role"] == "assistant"), None)

    def toolbar(self):
        try:
            from prompt_toolkit.application import get_app

            width = get_app().output.get_size().columns
        except Exception:
            width = console.width
        ai, last = self.chat.ai, self.last()
        sep = ("class:tb.sep", " │ ")
        model = (ai["model"] or "")[:26] if ai["connected"] else "AI off"
        mins = duration(time.time() - self.started)
        if time.time() - self.last_ctrl_c < 2:
            return [("class:tb.warn", " Press Ctrl+C again to quit ")]
        fill = (last["memory"]["tokens"] / last["memory"]["budget"]) if last else 0.0
        bar_color = "#98c379" if fill < 0.5 else "#e5c07b" if fill < 0.8 else "#d19a66" if fill < 0.95 else "#e06c75"
        nxt = "Automatic" if self.next_memory == "auto" else f"{NAME[self.next_memory]} (once)"
        nxt_style = "class:tb.warn" if self.next_memory != "auto" else "class:tb"
        left = [("class:tb.logo", " ◈ "), ("class:tb", model)]
        if width < 52:
            parts = left + [sep, ("class:tb.dim", mins)]
        elif width < 76:
            parts = left + [sep, (f"fg:{bar_color}", f"{round(fill * 100)}%"), sep, (nxt_style, nxt), sep, ("class:tb.dim", mins)]
        else:
            cells = round(min(fill, 1.0) * 10)
            n = len(self.chat.exchanges())
            parts = left + [sep, ("class:tb.dim", "memory "), ("class:tb", f"{last['memory']['tokens'] if last else 0}/{self.chat.budget} "),
                            (f"fg:{bar_color}", "█" * cells), ("class:tb.dim", "░" * (10 - cells)), ("class:tb", f" {round(fill * 100)}%")]
            if last:
                s = last["memory"]["strategy"]
                parts += [sep, ("class:tb.dim", "last "), (f"fg:{HEX[s]}", NAME[s])]
            parts += [sep, ("class:tb.dim", "next "), (nxt_style, nxt)]
            if self.queue:
                parts += [sep, ("class:tb.warn", f"▶ {len(self.queue)} queued")]
            if self.settings["focus"]:
                parts += [sep, ("class:tb.warn", "focus")]
            parts += [sep, ("class:tb", f"{n} messages"), sep, ("class:tb.dim", mins)]
            title = self.session.get("title")
            if title:
                badge = f" {title[:30]} "
                used = sum(len(t) for _, t in parts)
                if used + len(badge) + 2 < width:
                    parts += [("class:tb", " " * (width - used - len(badge) - 1)), ("class:tb.title", badge)]
        return parts

    def memory_row(self, mem: dict, full: bool = False, at: float | None = None) -> Group | None:
        level = "verbose" if full else ("off" if self.settings["focus"] else self.settings["verbose"])
        if level == "off":
            return None
        s = mem["strategy"]
        line = Text()
        if self.settings["timestamps"] and at:
            line.append(time.strftime("%H:%M  ", time.localtime(at)), "dim")
        line.append("memory  ", "dim")
        line.append(mem["name"], f"bold {COLOR[s]}")
        if mem["chosen_by"] == "you":
            line.append("  (your choice)", "yellow")
        line.append("  │  ", "dim")
        line.append(f"drew on messages {ranges(mem['drew_on'])}" if mem["drew_on"] else "no earlier messages yet")
        line.append("  │  ", "dim")
        line.append(f"{mem['tokens']}/{mem['budget']} tokens", "dim")
        rows = [gutter(Text("◆", style=COLOR[s]), line)]
        if level == "verbose":
            for c in mem.get("candidates", []):
                picked = c["strategy"] == s or (s == "hybrid" and c["strategy"] in ("sliding_window", "rag"))
                rows.append(gutter(Text(" "), Text.assemble(("┊ ", "dim"), (f"{c['name']:<16}", COLOR[c["strategy"]]),
                                                             (f"{c['tokens']:>4} tokens  {c['detail']}", "" if picked else "dim"),
                                                             (f"  {c['ms']} ms" if c["ms"] else "", "dim"))))
        if mem["reason"]:
            rows.append(gutter(Text(" "), Text(mem["reason"], style="dim")))
        for note in mem["notes"]:
            rows.append(gutter(Text(" "), Text.assemble(("▲ ", "yellow"), (note, "yellow"))))
        if level == "verbose":
            rows.append(gutter(Text(" "), Text(f"Decided in {mem['ms']:.2f} ms, no AI call. Logged rationale:", style="dim")))
            for part in mem["rationale"].split(" | "):
                rows.append(gutter(Text(" "), Text(f"  {part}", style="dim")))
        return Group(*rows)

    def reply_view(self, text: str, mark: str = "◈") -> Table:
        return gutter(Text(mark, style=f"bold {self.accent}"), Markdown(text or " ", code_theme="monokai"))

    # ---------------------------------------------------------------- one message
    def expand(self, text: str) -> str:
        for key, body in self.pastes.items():
            text = text.replace(key, body)
        return text

    def send(self, text: str, memory: str | None = None, side: bool = False) -> dict | None:
        text = self.expand(text).strip()
        if not text:
            return None
        if memory is None:
            memory, self.next_memory = self.next_memory, "auto"
        t0 = time.time()
        label = "Choosing memory for a side question…" if side else "Choosing memory…"
        with Live(Busy(self, lambda: label), console=console, transient=True, refresh_per_second=10):
            turn = self.chat.side(text) if side else self.chat.prepare(text, memory)
        mem = turn["memory"]
        self.usage.memory_ms.append(mem["ms"])
        prev = [m for m in self.chat.messages if m["role"] == "assistant"]
        changed = not prev or prev[-1]["memory"]["strategy"] != mem["strategy"]
        if self.settings["verbose"] != "new" or changed or side:
            row = self.memory_row(mem, at=time.time())
            if row is not None:
                console.print(row)

        reply, ai_error, stopped = None, None, False
        if self.chat.llm is None:
            console.print(gutter(Text("◈", style="dim"), Text("AI is off, so there is no reply. /context all shows what it "
                                                             "would have been shown. Start Ollama, then /connect.", style="dim")))
        else:
            reply, ai_error, stopped = self.stream(turn, mark="↳" if side else "◈")
            self.usage.calls += 1
            self.usage.sent_tokens += count_tokens(turn["ask"][0]) + count_tokens(turn["ask"][1])
            self.usage.words += len((reply or "").split())
        msg = None
        if not side:
            msg = self.chat.finish(turn, reply or None, ai_error)
            self.save_session()

        took = time.time() - t0
        self.usage.seconds += took if self.chat.llm is not None else 0
        if reply and not console.is_terminal:
            console.print()  # a live view only ends its last line in a real terminal
        if ai_error:
            console.print(gutter(Text("✗", style="red"), Text(ai_error, style="red")))
        if self.settings["footer"] and not self.settings["focus"]:
            bits = ["side question, not remembered"] if side else [f"message {msg['n']}"]
            bits += [NAME[mem["strategy"]], f"{took:.1f}s"]
            if reply:
                bits.append(f"{len(reply.split())} words")
            if stopped:
                bits.append("stopped by you")
            summary = " " + " │ ".join(bits) + " "
            console.print(Text("───" + summary + "─" * max(0, console.width - len(summary) - 4), style="dim"))
        if self.settings["bell"]:
            console.bell()
        console.print()
        return msg

    def stream(self, turn: dict, mark: str = "◈") -> tuple[str, str | None, bool]:
        pieces: list[str] = []
        thoughts: list[str] = []
        stop, done, errors = threading.Event(), threading.Event(), []
        model, llm = self.chat.ai["model"], self.chat.llm
        clock = {"t0": time.time(), "answer_at": None}

        def work():
            try:
                if hasattr(llm, "url"):
                    stream_ai(llm, *turn["ask"], on_text=pieces.append, stop=stop, on_reasoning=thoughts.append)
                else:  # a backend without streaming
                    pieces.append(llm(*turn["ask"]))
            except Exception as e:  # network, model not loaded, timeout
                errors.append(e)
            finally:
                done.set()

        def parts() -> tuple[str, str]:
            think, answer = split_think("".join(pieces))
            return ("".join(thoughts) + think).strip(), answer.lstrip()

        app = self
        status = {"what": ""}
        busy = Busy(app, lambda: status["what"])

        class View:
            def __rich__(self):
                secs = int(time.time() - clock["t0"])
                think, answer = parts()
                if answer and clock["answer_at"] is None:
                    clock["answer_at"] = time.time()
                rows = []
                if think and not answer:
                    rows.append(gutter(Text("∴", style="dim"), Text("thinking…", style="dim italic")))
                    if app.settings["reasoning"] == "show":
                        rows.append(gutter(Text(" "), Text("\n".join(think.splitlines()[-4:]), style="dim italic")))
                if answer:
                    rows.append(app.reply_view(answer, mark))
                hint = "  (on a laptop CPU the first words can take a minute)" if secs > 8 and not answer else ""
                status["what"] = (f"writing… {secs}s" if answer else
                                  f"{model} is reading {turn['memory']['tokens']} tokens of memory… {secs}s{hint}")
                rows.append(busy)
                return Group(*rows)

        threading.Thread(target=work, daemon=True).start()
        stopped = False
        with Live(View(), console=console, refresh_per_second=10, vertical_overflow="visible") as live:
            try:
                while not done.wait(0.1):
                    pass
            except KeyboardInterrupt:
                stop.set()
                stopped = True
            think, answer = parts()
            final = []
            if think:
                took = (clock["answer_at"] or time.time()) - clock["t0"]
                final.append(gutter(Text("∴", style="dim"), Text(f"Thought for {took:.0f}s", style="dim")))
                if self.settings["reasoning"] == "show":
                    final.append(gutter(Text(" "), Text(think, style="dim italic")))
            if answer.strip():
                final.append(self.reply_view(answer.strip(), mark))
            live.update(Group(*final) if final else Text(""))
        error = None
        if errors and not answer.strip():
            error = f"The AI did not answer ({type(errors[0]).__name__}). Your message and memory are saved."
        return answer.strip(), error, stopped

    # ---------------------------------------------------------------- commands
    def build_commands(self) -> list[Command]:
        on_off = lambda: [("on", ""), ("off", "")]  # noqa: E731
        C = Command
        return [
            # session
            C("/new", "Session", "start a new chat (the current one stays saved)", self.c_new, "[title] [-y]", ("/reset",)),
            C("/clear", "Session", "clear the screen and start a new chat", self.c_clear, "[-y]"),
            C("/history", "Session", "list the messages in this chat", self.c_history),
            C("/save", "Session", "save this chat as a Markdown file", self.c_save, "[file.md]"),
            C("/retry", "Session", "send your last message again", self.c_retry),
            C("/undo", "Session", "remove the last message and its reply", self.c_undo, "[-y]"),
            C("/title", "Session", "name this chat", self.c_title, "[name]"),
            C("/sessions", "Session", "list saved chats", self.c_sessions),
            C("/resume", "Session", "open a saved chat", self.c_resume, "<number|id|title>",
              choices=lambda: [(str(i), s.get("title") or s["id"]) for i, s in enumerate(sessions.all_sessions()[:20], 1)]),
            C("/branch", "Session", "copy this chat into a new one and continue there", self.c_branch, "[name]", ("/fork",)),
            C("/btw", "Session", "ask a side question; it uses memory but is not remembered", self.c_btw, "<question>"),
            C("/queue", "Session", "queue messages to send one after another", self.c_queue, "<message>|list|rm N|clear", ("/q",)),
            C("/copy", "Session", "copy the last reply (or the Nth from last)", self.c_copy, "[N]"),
            # memory
            C("/memory", "Memory", "choose the memory method for your next message", self.c_memory, "<method>",
              choices=lambda: list(SHORT_HELP.items())),
            C("/why", "Memory", "explain the last memory choice in full", self.c_why),
            C("/context", "Memory", "what the AI was shown, by part (all: the full text)", self.c_context, "[all]", ("/ctx",),
              choices=lambda: [("all", "show the full text")]),
            C("/track", "Memory", "show how memory switched during this chat", lambda a: self.track()),
            C("/sample", "Memory", "load a 15-message coding session to try", self.c_sample),
            C("/status", "Memory", "a recap of this chat (no AI call)", self.c_status),
            C("/usage", "Memory", "AI calls, time, tokens sent, memory decision time", self.c_usage),
            # AI and display
            C("/model", "AI and display", "show or switch the AI model", self.c_model, "[name]",
              choices=lambda: [(m, "") for m in self.chat.models()]),
            C("/connect", "AI and display", "look for the AI again (Ollama or CEAI_LLM_*)", self.c_connect),
            C("/personality", "AI and display", "set the reply style", self.c_personality, "[name|none]",
              choices=lambda: [(k, v) for k, v in PERSONALITIES.items()] + [("none", "no style")]),
            C("/verbose", "AI and display", "cycle how much memory detail is shown", self.c_verbose, "[off|new|all|verbose]",
              choices=lambda: list(VERBOSE_HELP.items())),
            C("/focus", "AI and display", "show only your messages and the replies", lambda a: self.toggle("focus", a), "[on|off]",
              choices=on_off),
            C("/reasoning", "AI and display", "show or hide the thinking of reasoning models", self.c_reasoning, "[show|hide]",
              choices=lambda: [("show", ""), ("hide", "")]),
            C("/skin", "AI and display", "change the colours", self.c_skin, "[name]", choices=lambda: [(k, "") for k in SKINS]),
            C("/indicator", "AI and display", "busy indicator style", self.c_indicator, "[kaomoji|emoji|unicode|ascii]",
              choices=lambda: [(k, "") for k in INDICATORS]),
            C("/statusbar", "AI and display", "show or hide the status bar", lambda a: self.toggle("statusbar", a), "[on|off]",
              ("/sb",), choices=on_off),
            C("/timestamps", "AI and display", "show times on messages", lambda a: self.toggle("timestamps", a), "[on|off]",
              choices=on_off),
            C("/footer", "AI and display", "the summary line after each reply", lambda a: self.toggle("footer", a), "[on|off]",
              choices=on_off),
            C("/bell", "AI and display", "ring the terminal bell when a reply is done", lambda a: self.toggle("bell", a), "[on|off]",
              choices=on_off),
            C("/config", "AI and display", "show all settings", self.c_config),
            # info
            C("/help", "Info", "show the commands (or those matching a word)", self.c_help, "[word]"),
            C("/version", "Info", "version and environment", self.c_version),
            C("/redraw", "Info", "clear and redraw the screen", lambda a: (console.clear(), self.banner())),
            C("/quit", "Info", "leave (--delete also deletes this chat)", self.c_quit, "[--delete]", ("/exit",)),
        ]

    def resolve(self, word: str) -> Command | None:
        word = word.lower()
        for c in self.commands:
            if word == c.name or word in c.aliases:
                return c
        matches = [c for c in self.commands if c.name.startswith(word)]
        if len(matches) > 1 and any(c.name == "/help" for c in matches) and len(word) > 1:
            return next(c for c in matches if c.name == "/help")  # as in Hermes, /h means /help
        return matches[0] if len(matches) == 1 else None

    def command(self, line: str) -> bool:
        """Run a slash command. Returns False to quit."""
        word, _, arg = line.strip().partition(" ")
        cmd = self.resolve(word)
        if cmd is None:
            near = [c.name for c in self.commands if c.name.startswith(word.lower())]
            console.print(f"[red]Unknown command {word}.[/] " + (f"Did you mean {', '.join(near)}?" if near else "/help lists them."))
        elif cmd.run(arg.strip()) is False:
            return False
        console.print()
        return True

    def confirm(self, question: str, arg: str) -> bool:
        if YES & set(arg.split()):
            return True
        try:
            return console.input(f"{question} [dim]\\[y/N][/] ").strip().lower() in ("y", "yes")
        except (EOFError, KeyboardInterrupt):
            return False

    def toggle(self, key: str, arg: str) -> None:
        value = {"on": True, "off": False}.get(arg.lower(), not self.settings[key]) if arg != "status" else self.settings[key]
        self.set(key, value)
        if key == "statusbar" and self.prompt_session is not None:
            self.prompt_session.bottom_toolbar = self.toolbar if value else None
        console.print(f"[dim]{key}:[/] {'on' if value else 'off'}")

    # session commands ----------------------------------------------------------------------
    def c_new(self, arg: str) -> None:
        title = " ".join(w for w in arg.split() if w not in YES) or None
        if self.chat.messages and not self.confirm("Start a new chat? This one stays saved.", arg):
            return
        self.save_session()
        self.chat.reset()
        self.session, self.next_memory, self.queue = self.fresh_session(title), "auto", []
        console.print(f"[dim]New chat{': ' + title if title else ''}. The previous one is under /sessions.[/]")

    def c_clear(self, arg: str) -> None:
        if self.chat.messages and not self.confirm("Clear the screen and start a new chat?", arg):
            return
        self.save_session()
        self.chat.reset()
        self.session, self.next_memory, self.queue = self.fresh_session(), "auto", []
        console.clear()
        self.banner()

    def c_history(self, arg: str) -> None:
        if not self.chat.messages:
            console.print("[dim]No messages yet.[/]")
        for m in self.chat.messages:
            if m["role"] == "user":
                stamp = time.strftime("%H:%M ", time.localtime(m["at"])) if self.settings["timestamps"] and m.get("at") else ""
                console.print(Text.assemble((f"{stamp}{m['n']:>3} ❯ ", "dim"), (m["text"].splitlines()[0][:100], "")))
            else:
                s = m["memory"]["strategy"]
                reply = (m["text"] or "(no reply)").replace("\n", " ")[:90]
                console.print(Text.assemble(("      ◈ " if self.settings["timestamps"] else "    ◈ ", COLOR[s]), (reply, "dim")))

    def c_save(self, arg: str) -> None:
        path = Path(arg or f"ceai_chat_{self.session['id']}.md")
        lines = [f"# {self.session.get('title') or 'CEAI chat'}", "",
                 f"AI: {self.chat.ai.get('model') or 'off'}. Memory budget: {self.chat.budget} tokens.", ""]
        for m in self.chat.messages:
            if m["role"] == "user":
                lines += [f"## {m['n']}. You", "", m["text"], ""]
            else:
                mem = m["memory"]
                lines += [f"*Memory: {mem['name']}" + (" (your choice)" if mem["chosen_by"] == "you" else "")
                          + (f", drew on messages {ranges(mem['drew_on'])}" if mem["drew_on"] else "") + f". {mem['reason']}*", "",
                          m["text"] or "_(no reply)_", ""]
        path.write_text("\n".join(lines), encoding="utf-8")
        self.save_session()
        console.print(f"Saved to [bold]{path.resolve()}[/]")

    def c_retry(self, arg: str) -> None:
        with Live(Busy(self, lambda: "Removing the last reply…"), console=console, transient=True):
            ex = self.chat.undo()
        if ex is None:
            console.print("[dim]Nothing to retry.[/]")
            return
        console.print(Text.assemble(("❯ ", self.accent), (ex["user"], "")))
        self.send(ex["user"], memory=ex.get("memory", "auto"))

    def c_undo(self, arg: str) -> None:
        if not self.chat.messages:
            console.print("[dim]Nothing to undo.[/]")
            return
        if not self.confirm("Remove your last message and its reply?", arg):
            return
        with Live(Busy(self, lambda: "Rebuilding memory without it…"), console=console, transient=True):
            ex = self.chat.undo()
        self.save_session()
        self.prefill = ex["user"]
        console.print(f"[dim]Removed. Your message is back in the input to edit or send again.[/]")

    def c_title(self, arg: str) -> None:
        if not arg:
            console.print(f"Title: [bold]{self.session.get('title') or '(none yet)'}[/]  [dim]id {self.session['id']}[/]")
            return
        self.session["title"] = arg
        self.save_session()
        console.print(f"[dim]Title set:[/] {arg}")

    def c_sessions(self, arg: str) -> None:
        all_s = sessions.all_sessions()
        if not all_s:
            console.print("[dim]No saved chats yet.[/]")
            return
        t = Table(box=None, padding=(0, 2), header_style="dim")
        for col in ("#", "title", "messages", "last used", "id"):
            t.add_column(col)
        for i, s in enumerate(all_s[:20], 1):
            here = s["id"] == self.session["id"]
            t.add_row(str(i), Text((s.get("title") or "(untitled)")[:40], style=f"bold {self.accent}" if here else ""),
                      str(len(s.get("messages", []))), ago(s.get("updated", 0)), Text(s["id"], style="dim"))
        console.print(t)
        console.print("[dim]Open one with /resume <number>.[/]")

    def c_resume(self, arg: str) -> None:
        if not arg:
            self.c_sessions("")
            return
        s = sessions.find(arg)
        if s is None:
            console.print(f"[red]No saved chat matches {arg!r}.[/] /sessions lists them.")
            return
        self.save_session()
        self.open_session(s)

    def c_branch(self, arg: str) -> None:
        if not self.chat.messages:
            console.print("[dim]Nothing to branch yet.[/]")
            return
        self.save_session()
        old = self.session
        self.session = {**self.fresh_session(arg or f"{old.get('title') or 'chat'} (branch)")}
        self.save_session()
        console.print(f"Now in [bold]{self.session['title']}[/]. The original is kept: [dim]/resume {old['id']}[/]")

    def c_btw(self, arg: str) -> None:
        if not arg:
            console.print("[dim]Usage: /btw <question>. Answered with memory, but not remembered.[/]")
            return
        self.send(arg, side=True)

    def c_queue(self, arg: str) -> None:
        word, _, rest = arg.partition(" ")
        if not arg or word == "list":
            if not self.queue:
                console.print("[dim]The queue is empty. /queue <message> adds one; it is sent after the next reply.[/]")
            for i, q in enumerate(self.queue, 1):
                console.print(f"  {i}. {q[:100]}")
        elif word == "clear":
            self.queue.clear()
            console.print("[dim]Queue cleared.[/]")
        elif word == "rm" and rest.strip().isdigit() and 1 <= int(rest) <= len(self.queue):
            console.print(f"[dim]Removed:[/] {self.queue.pop(int(rest) - 1)[:100]}")
        else:
            self.queue.append(rest if word == "add" else arg)
            console.print(f"[dim]Queued ({len(self.queue)}). It is sent after the next reply; press Enter on an empty line to start.[/]")

    def c_copy(self, arg: str) -> None:
        replies = [m for m in self.chat.messages if m["role"] == "assistant" and m["text"]]
        k = int(arg) if arg.isdigit() else 1
        if not replies or k > len(replies):
            console.print("[dim]No reply to copy.[/]")
            return
        ok = copy_to_clipboard(replies[-k]["text"])
        console.print("[dim]Copied the reply.[/]" if ok else "[red]Could not reach the clipboard.[/]")

    # memory commands -----------------------------------------------------------------------
    def c_memory(self, arg: str) -> None:
        arg = arg.lower()
        if not arg:
            now = "Automatic" if self.next_memory == "auto" else NAME[self.next_memory]
            console.print(f"Next message uses: [bold]{now}[/]. Choose with /memory auto | recent | summary | search | both")
        elif arg == "auto":
            self.next_memory = "auto"
            console.print("[dim]Next message: CEAI chooses.[/]")
        elif arg in SHORT or arg in STRATEGIES:
            self.next_memory = SHORT.get(arg, arg)
            console.print(f"[dim]Next message only:[/] [{COLOR[self.next_memory]}]{NAME[self.next_memory]}[/]"
                          "[dim]. Afterwards CEAI chooses again.[/]")
        else:
            console.print(f"[red]Unknown method {arg!r}.[/] Use auto, recent, summary, search or both.")

    def c_why(self, arg: str) -> None:
        last = self.last()
        if not last:
            console.print("[dim]Nothing yet. Send a message first.[/]")
            return
        console.print(self.memory_row(last["memory"], full=True))

    def c_context(self, arg: str) -> None:
        last = self.last()
        if not last:
            console.print("[dim]Nothing yet. Send a message first.[/]")
            return
        mem = last["memory"]
        if arg.lower() == "all":
            console.print(Panel(Text(mem["context"] or "(empty)"), title=f"What the AI was shown for message {last['n']}",
                                subtitle=f"{mem['name']} │ {mem['tokens']} tokens", border_style=COLOR[mem["strategy"]],
                                title_align="left", subtitle_align="right"))
            return
        t = Table(box=None, padding=(0, 2), header_style="dim")
        t.add_column("part")
        t.add_column("tokens", justify="right")
        t.add_column("")
        total = mem["system_tokens"] + mem["tokens"] + mem["message_tokens"]
        t.add_row("Instructions to the AI", str(mem["system_tokens"]), "")
        for sec in mem.get("sections", []):
            t.add_row(Text(f"Memory: {sec['label']}", style=COLOR[mem["strategy"]]), str(sec["tokens"]), "")
        t.add_row("Your message", str(mem["message_tokens"]), "")
        t.add_row(Text("Total", style="bold"), Text(str(total), style="bold"), "")
        console.print(t)
        cells = round(min(mem["tokens"] / mem["budget"], 1.0) * 30)
        console.print(Text.assemble(("Memory budget  ", "dim"), ("█" * cells, COLOR[mem["strategy"]]), ("░" * (30 - cells), "dim"),
                                    (f"  {mem['tokens']} of {mem['budget']} tokens", "")))
        if mem["drew_on"]:
            console.print(f"[dim]Drew on messages {ranges(mem['drew_on'])}. /context all shows the full text.[/]")

    def c_sample(self, arg: str) -> None:
        if self.chat.messages and not self.confirm("Replace this chat with the sample? (this one stays saved)", arg):
            return
        self.save_session()
        with Live(Busy(self, lambda: "Loading the sample coding session (15 messages)…"), console=console, transient=True):
            self.chat.sample()
        self.session = self.fresh_session("Sample coding session")
        self.save_session()
        console.print(f"[{self.accent}]Loaded 15 messages[/] of a coding session (a task API, a bug, then a long detour).")
        self.track()
        console.print("[dim]Now try: Write a helper that formats a task's due date for the email digest.[/]")

    def c_status(self, arg: str) -> None:
        ex = self.chat.exchanges()
        used: dict[str, int] = {}
        for m in self.chat.messages:
            if m["role"] == "assistant":
                used[m["memory"]["strategy"]] = used.get(m["memory"]["strategy"], 0) + 1
        mine = sum(1 for e in ex if e["memory"] != "auto")
        rows = Table.grid(padding=(0, 2))
        rows.add_column(style="dim", no_wrap=True)
        rows.add_column()
        rows.add_row("Chat", f"{self.session.get('title') or '(untitled)'}  [dim]{self.session['id']}[/]")
        rows.add_row("AI", f"{self.chat.ai['model'] or 'off'}  [dim]{self.chat.ai['where'] or ''}[/]")
        rows.add_row("Memory", f"{self.chat.state()['system']} system, {self.chat.budget}-token budget")
        rows.add_row("Messages", f"{len(ex)} ({mine} with your memory choice)  [dim]open for {duration(time.time() - self.started)}[/]")
        rows.add_row("Methods", "  ".join(f"[{COLOR[s]}]{NAME[s]}[/] ×{c}" for s, c in used.items()) or "[dim]none yet[/]")
        if ex:
            rows.add_row("Last message", ex[-1]["user"].splitlines()[0][:90])
            rows.add_row("Last reply", (ex[-1]["reply"] or "(no reply)").replace("\n", " ")[:90])
        console.print(rows)

    def c_usage(self, arg: str) -> None:
        u = self.usage
        ms = u.memory_ms
        rows = Table.grid(padding=(0, 2))
        rows.add_column(style="dim", no_wrap=True)
        rows.add_column()
        rows.add_row("AI calls", f"{u.calls}" + (f"  [dim]{u.seconds:.0f}s in total, {u.seconds / u.calls:.1f}s each[/]" if u.calls else ""))
        rows.add_row("Sent to the AI", f"{u.sent_tokens} tokens  [dim](instructions + memory + your messages)[/]")
        rows.add_row("Reply words", str(u.words))
        rows.add_row("Memory decisions", f"{len(ms)}" + (f"  [dim]{sum(ms) / len(ms):.2f} ms each, no AI calls[/]" if ms else ""))
        local = self.chat.ai.get("where") == "Ollama on this computer"
        rows.add_row("Cost", "free (runs on this computer)" if local else "see your API provider")
        console.print(rows)
        console.print("[dim]Counts are for this run of the app.[/]")

    # AI and display commands ---------------------------------------------------------------
    def c_model(self, arg: str) -> None:
        if self.chat.llm is None:
            console.print("[yellow]No AI is connected.[/] Start Ollama, then /connect.")
            return
        models = self.chat.models()
        if not arg:
            for m in models:
                console.print(Text.assemble(("● " if m == self.chat.ai["model"] else "  ", self.accent), (m, "")))
            console.print("[dim]Switch with /model <name>.[/]")
            return
        pick = arg if arg in models else next((m for m in models if m.startswith(arg)), arg)
        self.chat.use_model(pick)
        console.print(f"[dim]AI model:[/] {pick}")

    def c_connect(self, arg: str) -> None:
        ai = self.chat.reconnect()
        console.print(f"[{self.accent}]Connected:[/] {ai['model']} [dim]({ai['where']})[/]" if ai["connected"] else
                      "[yellow]Still no AI.[/] Start Ollama (ollama serve) or set CEAI_LLM_BASE_URL / CEAI_LLM_MODEL.")

    def c_personality(self, arg: str) -> None:
        if not arg:
            for k, v in PERSONALITIES.items():
                console.print(Text.assemble(("● " if k == self.chat.personality else "  ", self.accent), (f"{k:<10}", "bold"), (v, "dim")))
            console.print("[dim]Set with /personality <name>; /personality none clears it.[/]")
            return
        value = None if arg.lower() in ("none", "default", "neutral") else arg.lower()
        if value and value not in PERSONALITIES:
            console.print(f"[red]Unknown style {arg!r}.[/] Choose from {', '.join(PERSONALITIES)}.")
            return
        self.chat.personality = value
        self.set("personality", value)
        console.print(f"[dim]Reply style:[/] {value or 'none'}")

    def c_verbose(self, arg: str) -> None:
        level = arg.lower() if arg.lower() in VERBOSE else VERBOSE[(VERBOSE.index(self.settings["verbose"]) + 1) % len(VERBOSE)]
        self.set("verbose", level)
        console.print(f"[dim]Memory detail:[/] {level} [dim]({VERBOSE_HELP[level]})[/]")

    def c_reasoning(self, arg: str) -> None:
        value = arg.lower() if arg.lower() in ("show", "hide") else ("hide" if self.settings["reasoning"] == "show" else "show")
        self.set("reasoning", value)
        console.print(f"[dim]Thinking of reasoning models:[/] {value}")

    def c_skin(self, arg: str) -> None:
        if arg.lower() not in SKINS:
            console.print("Skins: " + "  ".join(f"[{v['accent']}]{k}[/]" + (" (on)" if k == self.settings["skin"] else "")
                                                for k, v in SKINS.items()))
            return
        self.set("skin", arg.lower())
        if self.prompt_session is not None:
            self.prompt_session.style = self.style()
        console.print(f"[{self.accent}]Skin: {arg.lower()}[/]")

    def c_indicator(self, arg: str) -> None:
        if arg.lower() not in INDICATORS:
            console.print("Styles: " + "  ".join(f"{k} {v[0][0]}" for k, v in INDICATORS.items()))
            return
        self.set("indicator", arg.lower())
        console.print(f"[dim]Busy indicator:[/] {arg.lower()}")

    def c_config(self, arg: str) -> None:
        rows = Table.grid(padding=(0, 2))
        rows.add_column(style="dim", no_wrap=True)
        rows.add_column()
        for k, v in self.settings.items():
            rows.add_row(k, str(v))
        rows.add_row("budget", f"{self.chat.budget} tokens (set with --budget)")
        rows.add_row("saved in", str(sessions.home()))
        console.print(rows)

    # info ----------------------------------------------------------------------------------
    def c_help(self, arg: str) -> None:
        word = arg.lower()
        groups: dict[str, list[Command]] = {}
        for c in self.commands:
            if not word or word in c.name or word in c.help.lower():
                groups.setdefault(c.group, []).append(c)
        for g, cmds in groups.items():
            console.print(f"[bold]{g}[/]")
            t = Table.grid(padding=(0, 2))
            t.add_column(style=self.accent, no_wrap=True, min_width=30)
            t.add_column(style="dim")
            for c in cmds:
                t.add_row(Text(f"{c.name} {c.args}".strip() + (f"  ({', '.join(c.aliases)})" if c.aliases else "")), Text(c.help))
            console.print(t)
        if not word:
            console.print("[bold]Keys[/]")
            for k, d in [("Enter", "send"), ("Alt+Enter, Ctrl+J, or a line ending in \\", "new line"),
                         ("Tab", "complete a command, or accept the grey suggestion"), ("Up / Down", "earlier inputs"),
                         ("Ctrl+P", "list the commands"), ("Ctrl+G", "write the message in your editor"),
                         ("Ctrl+S", "put the input aside; again on an empty input brings it back"),
                         ("Ctrl+C", "stop a reply, clear the input, twice to quit"), ("Ctrl+D", "quit"),
                         ("!<command>", "run a shell command (not sent to the AI)")]:
                console.print(Text.assemble((f"  {k:<44}", self.accent), (d, "dim")))
            console.print("[dim]Commands can be shortened, e.g. /h for /help.[/]")

    def c_version(self, arg: str) -> None:
        try:
            from importlib.metadata import version

            core = version("ceai-memory-middleware")
        except Exception:
            core = "?"
        console.print(f"CEAI terminal {VERSION}  [dim]│[/]  memory middleware {core}  [dim]│[/]  {self.chat.state()['system']} system  "
                      f"[dim]│[/]  Python {platform.python_version()} on {platform.system()}")

    def c_quit(self, arg: str) -> bool:
        if "--delete" in arg.split():
            if not self.confirm("Delete this chat permanently?", arg):
                return True
            self.quit_delete = True
        return False

    # ---------------------------------------------------------------- the track
    def track(self) -> None:
        picks = [m["memory"]["strategy"] for m in self.chat.messages if m["role"] == "assistant"]
        if not picks:
            console.print("[dim]No messages yet.[/]")
            return
        width = max(len(NAME[s]) for s in STRATEGIES)
        for s in STRATEGIES:
            row = Text(f"  {NAME[s]:<{width}}  ", style="dim")
            for p in picks:
                row.append("● " if p == s else "· ", COLOR[s] if p == s else "grey30")
            console.print(row)
        axis = "".join(f"{i:<2}" if i % 5 == 0 or i == 1 else "  " for i in range(1, len(picks) + 1))
        console.print(Text(f"  {'message':<{width}}  {axis}", style="dim"))

    # ---------------------------------------------------------------- shell
    def shell(self, cmd: str) -> None:
        if not cmd:
            console.print("[dim]Usage: !<command>, e.g. !dir. Runs on this computer; nothing is sent to the AI.[/]")
            return
        try:
            code = subprocess.run(cmd, shell=True).returncode
        except KeyboardInterrupt:
            code = 130
        if code:
            console.print(f"[red]! exited {code}[/]")

    # ---------------------------------------------------------------- the loop
    def run(self, resume: dict | None = None) -> None:
        self.banner()
        if resume is not None:
            self.open_session(resume)
        ask = self.make_prompt()
        while True:
            if self.queue:
                nxt = self.queue.pop(0)
                console.print(Text.assemble(("▶ ", "yellow"), ("from the queue: ", "dim"), (nxt, "")))
                self.safe_send(nxt)
                continue
            try:
                line = ask()
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            if not line.strip():
                continue
            if line.strip().lower() in ("exit", "quit"):
                break
            if line.lstrip().startswith("!"):
                self.shell(line.lstrip()[1:].strip())
                continue
            if line.lstrip().startswith("/"):
                if not self.command(line):
                    break
                continue
            self.safe_send(line)
        self.goodbye()

    def safe_send(self, text: str) -> None:
        try:
            self.send(text)
        except KeyboardInterrupt:
            console.print("[dim]Stopped.[/]\n")

    def goodbye(self) -> None:
        n = len(self.chat.exchanges())
        if self.quit_delete:
            sessions.delete(self.session["id"])
            console.print("[dim]Chat deleted. Bye.[/]")
        elif n:
            self.save_session()
            console.print(Text.assemble(("Saved ", "dim"), (self.session.get("title") or "", "bold"),
                                        (f"  {n} messages, {duration(time.time() - self.started)}", "dim")))
            console.print(Text.assemble(("Resume with: ", "dim"), (f"python -m console.tui --resume {self.session['id']}", self.accent)))
        else:
            console.print("[dim]Bye.[/]")
        self.chat.pipe.close()

    # ---------------------------------------------------------------- input
    def style(self):
        from prompt_toolkit.styles import Style

        skin = SKINS.get(self.settings["skin"], SKINS["ceai"])
        return Style.from_dict({
            "prompt": f"{skin['hex']} bold", "bottom-toolbar": f"noreverse bg:{skin['bar']} #c8c8c8",
            "tb": "#c8c8c8", "tb.dim": "#7f7f7f", "tb.sep": "#4a4a4a", "tb.logo": f"{skin['hex']} bold",
            "tb.warn": "#e5c07b bold", "tb.title": f"bg:{skin['hex']} #111111 bold", "auto-suggestion": "#5c5c5c",
            "completion-menu.completion": "bg:#2a2a2a #c8c8c8", "completion-menu.completion.current": f"bg:{skin['hex']} #111111",
            "completion-menu.meta.completion": "bg:#2a2a2a #7f7f7f", "completion-menu.meta.completion.current": f"bg:{skin['hex']} #222222",
        })

    def make_prompt(self, pt_input=None, pt_output=None):
        if pt_input is None and not sys.stdin.isatty():  # piped input (scripts): plain lines, no status bar
            return lambda: input()
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.application import get_app
            from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
            from prompt_toolkit.completion import Completer, Completion
            from prompt_toolkit.filters import Condition
            from prompt_toolkit.history import FileHistory
            from prompt_toolkit.key_binding import KeyBindings
            from prompt_toolkit.keys import Keys
        except ImportError:
            console.print("[dim](Install prompt_toolkit for the status bar and Tab completion: pip install prompt_toolkit)[/]")
            return lambda: input("❯ ")
        if sys.platform == "win32" and not (os.environ.get("EDITOR") or os.environ.get("VISUAL")):
            os.environ["EDITOR"] = "notepad"
        app = self

        class Slash(Completer):
            def get_completions(self, document, complete_event):
                text = document.text_before_cursor
                if not text.startswith("/") or "\n" in text:
                    return
                head, space, rest = text.partition(" ")
                if not space:
                    for c in app.commands:
                        if c.name.startswith(head.lower()):
                            yield Completion(c.name, start_position=-len(head), display_meta=c.help)
                    return
                cmd = app.resolve(head)
                if cmd is not None and cmd.choices is not None and " " not in rest:
                    try:
                        options = cmd.choices()
                    except Exception:
                        options = []
                    for value, meta in options:
                        if value.lower().startswith(rest.lower()):
                            yield Completion(value, start_position=-len(rest), display_meta=meta)

        keys = KeyBindings()
        empty = Condition(lambda: not get_app().current_buffer.text)

        @keys.add("enter")
        def _(event):
            b = event.current_buffer
            if b.complete_state and b.complete_state.current_completion:
                b.apply_completion(b.complete_state.current_completion)
            elif b.document.text_before_cursor.endswith("\\") and b.document.is_cursor_at_the_end:
                b.delete_before_cursor(1)
                b.insert_text("\n")
            else:
                b.validate_and_handle()

        @keys.add("escape", "enter")
        @keys.add("c-j")
        def _(event):
            event.current_buffer.insert_text("\n")

        @keys.add("tab")
        def _(event):
            b = event.current_buffer
            if b.suggestion and b.document.is_cursor_at_the_end and not b.complete_state:
                b.insert_text(b.suggestion.text)
            elif b.complete_state:
                b.complete_next()
            else:
                b.start_completion(select_first=False)

        @keys.add("c-p")
        def _(event):
            b = event.current_buffer
            if not b.text.startswith("/"):
                b.text, b.cursor_position = "/", 1
            b.start_completion(select_first=False)

        @keys.add("c-s")
        def _(event):
            b = event.current_buffer
            if b.text:
                app.stash.append(b.text)
                b.reset()
            elif app.stash:
                b.text = app.stash.pop()
                b.cursor_position = len(b.text)

        @keys.add("c-g")
        def _(event):
            event.current_buffer.open_in_editor(validate_and_handle=True)

        @keys.add("c-c")
        def _(event):
            b = event.current_buffer
            if b.text:
                b.reset()
            elif time.time() - app.last_ctrl_c < 2:
                event.app.exit(exception=EOFError())
            else:
                app.last_ctrl_c = time.time()
                event.app.invalidate()

        @keys.add("c-d", filter=empty)
        def _(event):
            event.app.exit(exception=EOFError())

        @keys.add(Keys.BracketedPaste)
        def _(event):
            data = event.data.replace("\r\n", "\n").replace("\r", "\n")
            lines = data.count("\n") + 1
            if lines >= 5 or len(data) > 1200:
                key = f"[pasted {lines} lines #{len(app.pastes) + 1}]"
                app.pastes[key] = data
                event.current_buffer.insert_text(key)
            else:
                event.current_buffer.insert_text(data)

        self.prompt_session = PromptSession(
            history=FileHistory(str(sessions.home() / "input_history")), auto_suggest=AutoSuggestFromHistory(),
            completer=Slash(), complete_while_typing=True, key_bindings=keys, multiline=True, prompt_continuation="  ",
            bottom_toolbar=self.toolbar if self.settings["statusbar"] else None, style=self.style(), refresh_interval=1.0,
            input=pt_input, output=pt_output)

        def ask():
            stamp = [("class:tb.dim", time.strftime("%H:%M "))] if self.settings["timestamps"] else []
            default, self.prefill = self.prefill, ""
            return self.prompt_session.prompt(stamp + [("class:prompt", "❯ ")], default=default)

        return ask


def main() -> None:
    warnings.filterwarnings("ignore")
    try:
        from transformers.utils import logging as hf_logging

        hf_logging.disable_progress_bar()
        hf_logging.set_verbosity_error()
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-c", "--continue", dest="cont", action="store_true", help="continue the most recent chat")
    ap.add_argument("-r", "--resume", metavar="KEY", help="open a saved chat by number, id or title")
    ap.add_argument("-q", "--query", metavar="TEXT", help="answer one message and exit ('-' reads stdin)")
    ap.add_argument("--model", help="AI model to use (e.g. qwen2.5:7b)")
    ap.add_argument("--budget", type=int, default=700, help="memory budget in tokens")
    args = ap.parse_args()

    resume = None
    if args.cont or args.resume:
        resume = sessions.latest() if args.cont else sessions.find(args.resume)
        if resume is None:
            console.print(f"[red]No saved chat {'yet' if args.cont else 'matches ' + repr(args.resume)}.[/] Starting a new one.")
    app = App(args.budget, args.model)
    if args.query is not None:
        text = sys.stdin.read() if args.query == "-" else args.query
        if resume is not None:
            with Live(Busy(app, lambda: "Rebuilding memory…"), console=console, transient=True):
                app.chat.load(resume.get("messages", []))
            app.session = resume
        app.send(text)
        app.goodbye()
        return
    app.run(resume)


if __name__ == "__main__":
    main()
