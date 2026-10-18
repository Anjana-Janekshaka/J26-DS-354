"""Aggregate CAUGHT / MISSED over every coding scenario (roadmap 3.2).

    python -m demo.coding_session.run_scenarios [--budget 700] [--out runs/demo_scenarios]

Runs the frozen system once per scenario in `scenarios.py` with the same harness as `run_demo`
(same strategies, same trap check, same budget) and writes `summary.json` with per-scenario rows
and catch rates over the held-out scenarios, overall and per trap kind. The protocol, including
which number is primary, is fixed in docs/demo_scenarios_preregistration.md.
"""

from __future__ import annotations

import argparse
import json
import warnings
from collections import defaultdict
from pathlib import Path

from eval.frozen import system_name
from retrieval.rerank import DEFAULT_RERANKER

from .run_demo import run
from .scenarios import SCENARIOS

STRATEGIES = ["fixed_6_exchange_window", "sliding_window", "summarization", "rag", "hybrid", "adaptive"]


def slug(name: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=700)
    ap.add_argument("--out", default="runs/demo_scenarios")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    for sc in SCENARIOS:
        res = run(args.budget, out / slug(sc.name), reranker=DEFAULT_RERANKER, exchanges=sc.exchanges,
                  traps=sc.traps, conversation_id=slug(sc.name))
        for t in sc.traps:
            row = {"scenario": sc.name, "language": sc.language, "held_out": sc.held_out, "trap": t.name,
                   "kind": sc.kinds.get(t.name, "?"), "gap_exchanges": t.exchange - t.planted_at,
                   "adaptive_strategy": res["timeline"][t.exchange - 1]["strategy"]}
            for s in STRATEGIES:
                row[s] = res["results"][s][t.name]["caught"]
                row[s + "_detail"] = res["results"][s][t.name]["detail"]
            rows.append(row)
        caught = sum(res["results"]["adaptive"][t.name]["caught"] for t in sc.traps)
        base = sum(res["results"]["fixed_6_exchange_window"][t.name]["caught"] for t in sc.traps)
        print(f"{sc.name:<28} adaptive {caught}/{len(sc.traps)}   fixed window {base}/{len(sc.traps)}", flush=True)

    held = [r for r in rows if r["held_out"]]

    def rate(rs: list[dict]) -> dict:
        return {s: {"caught": sum(r[s] for r in rs), "of": len(rs)} for s in STRATEGIES}

    by_kind = defaultdict(list)
    for r in held:
        by_kind[r["kind"]].append(r)
    summary = {
        "system": system_name(),
        "budget_tokens": args.budget,
        "held_out": rate(held),
        "held_out_excluding_control": rate([r for r in held if "control" not in r["scenario"]]),
        "original": rate([r for r in rows if not r["held_out"]]),
        "by_kind": {k: rate(v) for k, v in sorted(by_kind.items())},
        "rows": rows,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nHeld-out scenarios: {len(held)} traps")
    print(f"{'strategy':<26}{'held out':>10}" + "".join(f"{k:>12}" for k in summary["by_kind"]))
    for s in STRATEGIES:
        h = summary["held_out"][s]
        cells = "".join(f"{str(v[s]['caught']) + '/' + str(v[s]['of']):>12}" for v in summary["by_kind"].values())
        print(f"{s:<26}{str(h['caught']) + '/' + str(h['of']):>10}{cells}")
    print("\nMissed by adaptive:")
    for r in held:
        if not r["adaptive"]:
            print(f"  {r['scenario']} / {r['trap']} ({r['kind']}): chose {r['adaptive_strategy']}; {r['adaptive_detail']}")


if __name__ == "__main__":
    main()
