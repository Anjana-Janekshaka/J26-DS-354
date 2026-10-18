"""Does the adaptive advantage grow with conversation length? (docs/v4_preregistration.md section 5)

    python -m eval.synthetic.controller.length

A new set with family C wording (the held-out test family), seed 404: 15 conversations for each fixed
detour of 2, 10, 25 and 50 exchanges before the late probes. Frozen system, budget 400, nothing tuned.
Reports evidence hit per strategy and per detour group, and adaptive minus each fixed strategy with
conversation-level CIs. Also breaks the existing test traces down by conversation-length tercile.
"""

from __future__ import annotations

import json
import random
import warnings
from pathlib import Path

from controller import RuleBasedController
from eval.metrics import cluster_bootstrap_ci

from .generate import make_family
from .learned import load_traces
from .run import load_rule_config
from .trace import STRATEGIES, build_traces, replay

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / "results_v4"
DETOURS = (2, 10, 25, 50)
PER_GROUP = 15


def length_set() -> list[dict]:
    rng = random.Random(404)
    return [make_family(rng, f"len-{d:02d}-{i:02d}", "C", detour=d) for d in DETOURS for i in range(PER_GROUP)]


def breakdown(rows: list[dict], group_of) -> dict:
    out = {}
    for g in sorted({group_of(r) for r in rows}):
        rs = [r for r in rows if group_of(r) == g]
        res = {"n_probes": len(rs), "hit": {s: sum(r["hits"][s] for r in rs) / len(rs) for s in STRATEGIES}}
        res["hit"]["adaptive"] = sum(r["adaptive_hit"] for r in rs) / len(rs)
        for s in ("sliding_window", "rag", "hybrid"):
            paired = [{"conv": r["conv"], "d": float(r["adaptive_hit"]) - float(r["hits"][s])} for r in rs]
            res[f"adaptive_minus_{s}"] = cluster_bootstrap_ci(paired, lambda x: sum(r["d"] for r in x) / len(x))
        out[str(g)] = res
    return out


def main() -> None:
    warnings.filterwarnings("ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    cfg, default, _ = load_rule_config(False)
    rules = lambda: RuleBasedController(cfg, default)  # noqa: E731
    traces = build_traces(length_set(), 400, "minilm", True, OUT / "traces" / "length_b400_minilm_nli_rerank-noncode.jsonl.gz",
                          version="length-v1")
    rows = replay(traces, rules)
    by_detour = breakdown(rows, lambda r: int(r["conv"].split("-")[1]))

    test_rows = replay(load_traces(ROOT / "runs/colab3/controller_traces", "test"), rules)
    n_events = {}
    for tr in load_traces(ROOT / "runs/colab3/controller_traces", "test"):
        n_events[tr["conv"]] = sum(1 for e in tr["events"] if e["type"] == "turn")
    cuts = sorted(n_events.values())
    t1, t2 = cuts[len(cuts) // 3], cuts[2 * len(cuts) // 3]
    tercile = lambda r: "1 short" if n_events[r["conv"]] < t1 else ("2 medium" if n_events[r["conv"]] < t2 else "3 long")  # noqa: E731
    out = {"length_set_by_detour_exchanges": by_detour, "existing_test_by_length_tercile": breakdown(test_rows, tercile),
           "tercile_cuts_user_turns": [t1, t2]}
    (OUT / "length.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    for name, part in (("detour", by_detour), ("test tercile", out["existing_test_by_length_tercile"])):
        print(f"\n{name}:")
        for g, r in part.items():
            h = r["hit"]
            d = r["adaptive_minus_rag"], r["adaptive_minus_hybrid"], r["adaptive_minus_sliding_window"]
            print(f"  {g:<10} adaptive {h['adaptive']:.3f} rag {h['rag']:.3f} hybrid {h['hybrid']:.3f} window {h['sliding_window']:.3f} | "
                  + "  ".join(f"{n} {x['estimate']:+.3f} [{x['ci_low']:+.3f},{x['ci_high']:+.3f}]" for n, x in zip(("-rag", "-hyb", "-win"), d)))


if __name__ == "__main__":
    main()
