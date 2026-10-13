"""Coding-session demo on the real pipeline: CAUGHT / MISSED table for the two traps.

    python -m demo.coding_session.run_demo [--budget 700] [--out runs/demo]

One pipeline run; at every user turn all three modules produce outputs, the adaptive controller
decides, and each fixed-strategy alternative is assembled from the *same* module outputs. A fixed
6-exchange (12-message) recency window is run alongside as the original scaffold's baseline.
Writes the decision log, a static dashboard (dashboard.html) and results.json under --out.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import warnings
from pathlib import Path

from contracts import ControllerDecision, OverrideInfo, count_tokens
from contracts.text import BLOCK_TURNS, CONTEXT_BLOCK_SEPARATOR
from dashboard import render_static
from decision_logger import DecisionLogger
from eval.frozen import frozen_controller
from integration import MemoryPipeline, assemble_prompt
from retrieval import RetrievalConfig
from retrieval.rerank import DEFAULT_RERANKER
from sliding_window import RecencyOnlyWindow

from .script import EXCHANGES, TRAPS, Trap

STALE_MARKERS = ("[!] stale", "supersedes", "superseded", "retired symbols")


def check_trap(context: str, trap: Trap) -> tuple[bool, str]:
    if trap.required not in context:
        return False, f"missing `{trap.required}`"
    if trap.stale:
        for block in context.split(CONTEXT_BLOCK_SEPARATOR):
            lines = block.splitlines()
            for i, line in enumerate(lines):
                if trap.stale in line:
                    marked = any(m in line.lower() for m in STALE_MARKERS) or "[!] stale" in block
                    section = next((l for l in reversed(lines[:i]) if l.endswith(":") and not l.startswith("-")), "")
                    if not marked and "retired" not in section.lower():
                        return False, f"unmarked stale `{trap.stale}` present"
    return True, f"found `{trap.required}`"


def _find_turn(context: str, needle: str, ex_of_turn: dict[str, int]) -> str:
    """Which exchange the evidence came from, read from the block's own ``turns:`` header."""
    for block in context.split(CONTEXT_BLOCK_SEPARATOR):
        if needle in block:
            m = BLOCK_TURNS.search(block)
            if m:
                tid = m.group(1).split()[0]
                return f"exchange {ex_of_turn.get(tid, '?')} ({tid})"
    return "summary/window"


def run(budget: int, out: Path, quiet: bool = False, reranker: str | None = DEFAULT_RERANKER) -> dict:
    if out.exists():
        shutil.rmtree(out)
    # The frozen system configuration: tuned controller rules + reranked RAG (CLAUDE.md section 12).
    pipe = MemoryPipeline("coding-session-demo", token_budget=budget, log_dir=out, controller=frozen_controller(),
                          retrieval_config=RetrievalConfig(reranker=reranker))
    fixed6 = RecencyOnlyWindow(k=12)
    ex_of_turn: dict[str, int] = {}
    traps_by_ex = {t.exchange: t for t in TRAPS}
    strategies = ["fixed_6_exchange_window", "sliding_window", "summarization", "rag", "hybrid", "adaptive"]
    results: dict[str, dict[str, dict]] = {s: {} for s in strategies}
    timeline: list[dict] = []

    for ex, (user_msg, reply) in enumerate(EXCHANGES, start=1):
        res = pipe.user_turn(user_msg)
        ex_of_turn[res.turn.turn_id] = ex
        d = res.decision
        timeline.append(
            {
                "exchange": ex,
                "turn_id": res.turn.turn_id,
                "task_type": res.feature_vector.task_type,
                "pressure": res.feature_vector.token_budget_pressure,
                "strategy": d.selected_strategy,
                "rationale": d.rationale,
                "escalations": [e.kind for e in res.escalations],
            }
        )
        if ex in traps_by_ex:
            trap = traps_by_ex[ex]
            sig = res.signal
            for s in strategies:
                if s == "adaptive":
                    ctx = res.prompt.context
                elif s == "fixed_6_exchange_window":
                    ctx = fixed6.build_context(sig, user_msg).context_text()
                else:
                    forced = ControllerDecision(
                        turn_id=sig.turn_id,
                        selected_strategy=s,
                        rationale=f"forced {s} baseline",
                        controller_variant="rule_based",
                        decision_latency_ms=0.0,
                        override=OverrideInfo(applied=False, by=None),
                    )
                    ctx = assemble_prompt(forced, res.outputs, user_msg, sig.token_usage.budget).context
                caught, why = check_trap(ctx, trap)
                results[s][trap.name] = {"caught": caught, "detail": why, "tokens": count_tokens(ctx)}
            where = _find_turn(res.prompt.context, trap.required, ex_of_turn)
            results["adaptive"][trap.name]["evidence"] = where
        fixed6.ingest(res.turn)
        if reply:
            t = pipe.assistant_turn(reply)
            ex_of_turn[t.turn_id] = ex
            fixed6.ingest(t)

    logger = DecisionLogger(out)
    render_static(logger.records(), logger.escalation_events(), out / "dashboard.html")
    pipe.close()
    summary = {
        "budget_tokens": budget,
        "final_history_tokens": pipe.manager.tokens_used,
        "results": results,
        "timeline": timeline,
    }
    (out / "results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def print_report(summary: dict) -> None:
    print(f"\nBudget: {summary['budget_tokens']} tokens of memory context; full history at end: {summary['final_history_tokens']} tokens\n")
    print(f"{'ex':>3} {'task':<16} {'press':>5}  {'strategy':<15} rationale (rule)")
    for row in summary["timeline"]:
        rule = row["rationale"].split(" | ")[0]
        esc = f"  [escalation raised: {', '.join(row['escalations'])}]" if row["escalations"] else ""
        print(f"{row['exchange']:>3} {row['task_type']:<16} {row['pressure']:>5.2f}  {row['strategy']:<15} {rule[:90]}{esc}")
    names = [t.name for t in TRAPS]
    print("\n" + f"{'strategy':<26}" + "".join(f"{n:<28}" for n in names) + "score")
    for s, r in summary["results"].items():
        cells = "".join(f"{('CAUGHT' if r[n]['caught'] else 'MISSED') + ' (' + str(r[n]['tokens']) + ' tok)':<28}" for n in names)
        print(f"{s:<26}{cells}{sum(r[n]['caught'] for n in names)}/{len(names)}")
    print()
    for t in TRAPS:
        r = summary["results"]["adaptive"][t.name]
        row = summary["timeline"][t.exchange - 1]
        print(f"- {t.name} @ exchange {t.exchange}: adaptive chose {row['strategy']}; {r['detail']} via {r.get('evidence', '?')}")
        print(f"    rationale: {row['rationale']}")


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=700)
    ap.add_argument("--out", default="runs/demo")
    ap.add_argument("--no-reranker", action="store_true", help="plain FAISS ranking for RAG (ablation)")
    args = ap.parse_args()
    summary = run(args.budget, Path(args.out), reranker=None if args.no_reranker else DEFAULT_RERANKER)
    print_report(summary)
    print(f"\nDecision log: {Path(args.out) / 'decisions.jsonl'}\nDashboard:    {Path(args.out) / 'dashboard.html'}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
