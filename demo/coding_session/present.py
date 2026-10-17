"""Live presentation mode: the coding session on the live dashboard, one exchange at a time.

    python -m demo.coding_session.present                       # Enter advances one exchange
    python -m demo.coding_session.present --delay 4             # auto-advance every 4 s
    python -m demo.coding_session.present --scenario invoice-service
    python -m demo.coding_session.present --no-browser --port 8765

Starts the dashboard server on a fresh log folder, opens it in the browser, and plays the scripted
session through the frozen system. Each user turn prints the controller's choice and rule; at each
trap it prints CAUGHT / MISSED for adaptive and for the fixed 6-exchange window, from the same
history. Overrides queued in the dashboard form apply to the next decision, live.

After the script, type your own messages (empty line or "quit" ends). A static copy of the dashboard
is written to the log folder at the end, as an offline fallback.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import threading
import time
import warnings
import webbrowser
from pathlib import Path

from dashboard import render_static, serve
from decision_logger import DecisionLogger
from eval.frozen import frozen_controller, system_retrieval
from integration import MemoryPipeline
from retrieval import RetrievalConfig
from retrieval.rerank import DEFAULT_RERANKER
from sliding_window import RecencyOnlyWindow

from .run_demo import check_trap
from .run_scenarios import slug
from .scenarios import SCENARIOS

GREEN, RED, DIM, BOLD, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[1m", "\033[0m"


def pause(delay: float | None) -> None:
    if delay is None:
        input(f"{DIM}  [Enter] next exchange{RESET}")
    else:
        time.sleep(delay)


def show_decision(ex, res) -> None:
    d = res.decision
    rule = d.rationale.split(" | ")[0]
    extra = [p for p in d.rationale.split(" | ")[1:] if p.startswith(("escalation", "OVERRIDE", "dwell"))]
    print(f"{BOLD}{ex:>3} -> {d.selected_strategy:<15}{RESET} {res.feature_vector.task_type:<16} "
          f"pressure {res.feature_vector.token_budget_pressure:.2f}  {d.decision_latency_ms:.2f} ms")
    print(f"      {DIM}{rule}{RESET}")
    for e in extra:
        print(f"      {e}")
    for e in res.escalations:
        print(f"      escalation raised for the next turn: {e.kind}")


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=SCENARIOS[0].name, help="scenario name or slug (default: the original session)")
    ap.add_argument("--delay", type=float, default=None, help="auto-advance seconds (default: wait for Enter)")
    ap.add_argument("--budget", type=int, default=700)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--out", default="runs/present")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--no-chat", action="store_true", help="skip the free-typing part at the end")
    args = ap.parse_args()
    sc = next((s for s in SCENARIOS if args.scenario in (s.name, slug(s.name))), None)
    if sc is None:
        sys.exit(f"unknown scenario {args.scenario!r}; choose from: " + ", ".join(slug(s.name) for s in SCENARIOS))

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    print("Loading models (about 20 s)...", flush=True)
    pipe = MemoryPipeline(slug(sc.name), token_budget=args.budget, log_dir=out, controller=frozen_controller(),
                          retrieval_config=RetrievalConfig(**system_retrieval(reranker=DEFAULT_RERANKER)))
    server = serve(out, port=args.port)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Dashboard: {url}")
    if not args.no_browser:
        webbrowser.open(url)

    fixed6 = RecencyOnlyWindow(k=12)
    traps_at = {}
    for t in sc.traps:
        traps_at.setdefault(t.exchange, []).append(t)
    score = {"adaptive": 0, "fixed": 0}
    print(f"\n{BOLD}{sc.name}{RESET}: {len(sc.exchanges)} exchanges, {len(sc.traps)} trap(s), budget {args.budget} tokens\n")
    for ex, (user_msg, reply) in enumerate(sc.exchanges, start=1):
        pause(args.delay)
        print(f"\n{BOLD}user:{RESET} {user_msg[:150]}")
        res = pipe.user_turn(user_msg)
        show_decision(ex, res)
        for trap in traps_at.get(ex, []):
            a_ok, a_why = check_trap(res.prompt.context, trap)
            f_ok, f_why = check_trap(fixed6.build_context(res.signal, user_msg).context_text(), trap)
            score["adaptive"] += a_ok
            score["fixed"] += f_ok
            tag = lambda ok: f"{GREEN}CAUGHT{RESET}" if ok else f"{RED}MISSED{RESET}"  # noqa: E731
            print(f"\n   {BOLD}TRAP: {trap.name}{RESET} ({trap.description})")
            print(f"   adaptive ({res.decision.selected_strategy}): {tag(a_ok)}  {a_why}")
            print(f"   fixed 6-exchange window:  {tag(f_ok)}  {f_why}\n")
        fixed6.ingest(res.turn)
        if reply:
            print(f"{DIM}assistant: {reply.splitlines()[0][:120]}{RESET}")
            fixed6.ingest(pipe.assistant_turn(reply))

    print(f"\n{BOLD}Traps caught: adaptive {score['adaptive']}/{len(sc.traps)}, fixed window {score['fixed']}/{len(sc.traps)}{RESET}")
    if not args.no_chat:
        print("\nYour turn: type a message to see the controller decide (empty line or 'quit' ends).")
        n = len(sc.exchanges)
        while True:
            try:
                msg = input(f"{BOLD}you:{RESET} ").strip()
            except EOFError:
                break
            if not msg or msg.lower() in ("quit", "exit"):
                break
            n += 1
            res = pipe.user_turn(msg)
            show_decision(n, res)
            print(f"      {DIM}context sent to the model ({res.prompt.token_count} tokens):{RESET}")
            for line in res.prompt.context.splitlines()[:12]:
                print(f"      {DIM}| {line[:140]}{RESET}")

    logger = DecisionLogger(out)
    render_static(logger.records(), logger.escalation_events(), out / "dashboard.html")
    pipe.close()
    print(f"\nStatic dashboard (offline fallback): {out / 'dashboard.html'}")
    if args.delay is None and not args.no_chat:
        input("[Enter] stops the dashboard server")
    server.shutdown()


if __name__ == "__main__":
    main()
