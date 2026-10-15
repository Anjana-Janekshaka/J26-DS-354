"""Pre-registered gate check for the v2 hybrid system (docs/v2_hybrid_preregistration.md).

    python -m eval.v2_gate --frozen-val DIR --v2-val DIR --frozen-plus DIR --v2-plus DIR [--demo results.json]

A gate FAILS when v2 is significantly worse than the frozen system on that dev set: the 95%
bootstrap interval of the paired difference (v2 - frozen, same items) lies entirely below zero.
The demo gate requires every trap caught by adaptive. Exit code 0 = all gates pass, 1 = a gate failed.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from eval.metrics import cluster_bootstrap_ci


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def paired(frozen: list[dict], v2: list[dict], key, group: str) -> dict:
    if len(frozen) != len(v2):
        raise SystemExit(f"row counts differ ({len(frozen)} vs {len(v2)}): the two runs are not on the same items")
    pairs = [{group: a[group], "d": float(key(b)) - float(key(a))} for a, b in zip(frozen, v2)]
    c = cluster_bootstrap_ci(pairs, lambda rs: statistics.mean(r["d"] for r in rs), group, n_boot=2000)
    return {"frozen": statistics.mean(float(key(r)) for r in frozen), "v2": statistics.mean(float(key(r)) for r in v2),
            "diff": c["estimate"], "ci_low": c["ci_low"], "ci_high": c["ci_high"], "pass": c["ci_high"] >= 0.0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen-val", required=True)
    ap.add_argument("--v2-val", required=True)
    ap.add_argument("--frozen-plus", required=True)
    ap.add_argument("--v2-plus", required=True)
    ap.add_argument("--demo", default=None, help="v2 demo results.json (optional; the demo gate can be checked locally)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    gates = {
        "G2 synthetic controller val (evidence hit)": paired(
            _rows(Path(a.frozen_val) / "probes.jsonl"), _rows(Path(a.v2_val) / "probes.jsonl"), lambda r: r["adaptive_hit"], "conv"),
        "G3 LoCoMo-Plus dev (adaptive cue hit)": paired(
            _rows(Path(a.frozen_plus) / "items.jsonl"), _rows(Path(a.v2_plus) / "items.jsonl"), lambda r: r["adaptive"]["cue_hit"], "item"),
    }
    if a.demo:
        d = json.loads(Path(a.demo).read_text(encoding="utf-8"))
        caught = [v["caught"] for v in d["results"]["adaptive"].values()]
        gates["G1 coding demo (adaptive traps caught)"] = {"caught": sum(caught), "of": len(caught), "pass": all(caught)}
    ok = all(g["pass"] for g in gates.values())
    for name, g in gates.items():
        if "diff" in g:
            print(f"{'PASS' if g['pass'] else 'FAIL'}  {name}: frozen {g['frozen']:.4f} -> v2 {g['v2']:.4f}, "
                  f"diff {g['diff']:+.4f} [{g['ci_low']:+.4f}, {g['ci_high']:+.4f}]")
        else:
            print(f"{'PASS' if g['pass'] else 'FAIL'}  {name}: {g['caught']}/{g['of']}")
    print("ALL GATES PASSED" if ok else "A GATE FAILED - do not run the v2 test splits")
    if a.out:
        Path(a.out).write_text(json.dumps({"gates": gates, "all_pass": ok}, indent=2), encoding="utf-8")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
