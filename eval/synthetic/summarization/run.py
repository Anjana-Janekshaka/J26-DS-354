"""Structured + merge vs naive summarization on degradation-injected traces.

    python -m eval.synthetic.summarization.run

Per trace and budget, each summarizer emits its context at the end of the conversation; reported:
  * loss_score            - the module's own live anchor-recall loss (lower is better)
  * symbol_retention_rate - exact current signatures present (code sessions)
  * current_fact_recall   - ground-truth current facts present in context
  * stale_leak_rate       - superseded facts present WITHOUT a supersession marker on their line
Plus a loss-monitor sanity check: deleting a growing fraction of a summary's lines must raise the
loss score (Spearman rank correlation between deletion fraction and loss).
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

from contracts import ConversationTurn, TokenUsage, TurnSignal, utcnow
from contracts.text import normalize
from summarization import HierarchicalSummarizer, NaiveSummarizer, SummarizationConfig, anchor_loss

from .generate import generate

HERE = Path(__file__).parent
MARKERS = ("supersedes", "superseded", "retired", "[!] stale")


def run_one(trace: dict, summarizer, budget: int) -> dict:
    turns = [ConversationTurn(turn_id=f"t{i + 1:04d}", role=r, content=c) for i, (r, c) in enumerate(trace["messages"])]
    for t in turns:
        summarizer.ingest(t)
    sig = TurnSignal(
        turn_id=f"t{len(turns) + 1:04d}", conversation_id=trace["id"], turn_count=len(turns) + 1, task_type="code_refactor",
        token_usage=TokenUsage(used=budget * 3, budget=budget), conversation_state="task-1", timestamp=utcnow(),
    )
    out = summarizer.build_context(sig, "continue the work")
    ctx = out.context_text()
    nctx = normalize(ctx)
    current = trace["current_facts"]
    recall = sum(1 for f in current if normalize(f) in nctx) / len(current)
    leaks = 0
    for s in trace["stale_facts"]:
        for line in ctx.splitlines():
            if normalize(s) in normalize(line) and not any(m in line.lower() for m in MARKERS):
                leaks += 1
                break
    q = out.quality
    return {
        "loss_score": q.loss_score,
        "srr": q.symbol_retention_rate,
        "current_fact_recall": recall,
        "stale_leak_rate": leaks / len(trace["stale_facts"]),
        "tier": q.tier_emitted,
        "tokens": out.token_count,
        "summary_text": ctx,
        "turns": turns,
    }


def spearman(xs: list[float], ys: list[float]) -> float:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budgets", default="250,500,1000")
    ap.add_argument("--out", default=str(HERE / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    traces = generate()
    budgets = [int(b) for b in args.budgets.split(",")]
    systems = {
        "structured+merge": lambda: HierarchicalSummarizer(config=SummarizationConfig()),
        "structured_no_merge": lambda: HierarchicalSummarizer(config=SummarizationConfig(merge_contradictions=False)),
        "naive": lambda: NaiveSummarizer(tail_keep=4),
    }
    table: dict = {}
    monitor_x, monitor_y = [], []
    rng = random.Random(3)
    for b in budgets:
        for name, factory in systems.items():
            rows = [run_one(t, factory(), b) for t in traces]
            srrs = [r["srr"] for r in rows if r["srr"] is not None]
            table[f"{name}@{b}"] = {
                "loss_score": statistics.mean(r["loss_score"] for r in rows),
                "symbol_retention_rate": statistics.mean(srrs) if srrs else None,
                "current_fact_recall": statistics.mean(r["current_fact_recall"] for r in rows),
                "stale_leak_rate": statistics.mean(r["stale_leak_rate"] for r in rows),
                "tiers": {t: sum(1 for r in rows if r["tier"] == t) for t in ("L1", "L2", "L3")},
                "mean_tokens": statistics.mean(r["tokens"] for r in rows),
            }
            if name == "structured+merge" and b == max(budgets):
                for r in rows:
                    lines = [l for l in r["summary_text"].split("[Recent turns]")[0].splitlines() if l.strip()]
                    for frac in (0.0, 0.1, 0.25, 0.5, 0.75, 1.0):
                        keep = [l for l in lines if rng.random() >= frac]
                        source = [t for t in r["turns"]][:-4]
                        monitor_x.append(frac)
                        monitor_y.append(anchor_loss(source, "\n".join(keep))[0])
    rho = spearman(monitor_x, monitor_y)
    summary = {"n_traces": len(traces), "results": table, "loss_monitor_spearman_deletion_vs_loss": rho}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"{len(traces)} degradation-injected traces\n")
    print(f"{'system@budget':<28}{'loss':>7}{'SRR':>7}{'current':>9}{'stale':>8}{'tokens':>8}  tiers")
    for k, v in table.items():
        srr = f"{v['symbol_retention_rate']:.2f}" if v["symbol_retention_rate"] is not None else "  -"
        print(f"{k:<28}{v['loss_score']:>7.3f}{srr:>7}{v['current_fact_recall']:>9.2f}{v['stale_leak_rate']:>8.2f}{v['mean_tokens']:>8.0f}  {v['tiers']}")
    print(f"\nloss monitor sanity: Spearman(deleted fraction, loss) = {rho:.3f}  (1.0 = perfectly monotone)")
    print(f"written: {out / 'summary.json'}")


if __name__ == "__main__":
    main()
