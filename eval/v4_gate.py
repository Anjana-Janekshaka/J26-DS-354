"""System gates for v4 (docs/v4_preregistration.md section 6), run locally, frozen vs v4 under identical conditions.

    python -m eval.v4_gate [--out runs/v4_gates]

Jobs, in order (each skipped if its output already exists, so an interrupted run resumes):
  G1  coding scenarios with v4; frozen reference = results/final/demo_scenarios/summary.json
  G2  synthetic controller val (evidence hit), frozen and v4
  G3  LoCoMo-Plus dev (cue hit, 10 warm-up turns), frozen and v4
  G4  LoCoMo dev (evidence hit, NLI off as in the frozen LoCoMo runs), frozen and v4
A dev gate fails when the paired 95% CI of v4 - frozen lies entirely below 0. G1 needs the original
scenario at 2/2 and held-out catches not below the frozen system's. Stops at the first failed gate.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from eval.v2_gate import _rows, paired

ROOT = Path(__file__).resolve().parents[1]


def job(module: list[str], out: Path, system: str, marker: str) -> None:
    if (out / marker).exists():
        print(f"  have {out}", flush=True)
        return
    out.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "CEAI_SYSTEM": system}
    env.pop("CEAI_SW_WEIGHTS", None)
    print(f"  running {' '.join(module)} [{system}] -> {out}", flush=True)
    with open(out.with_suffix(".log"), "w", encoding="utf-8") as log:
        subprocess.run([sys.executable, "-m", *module, "--out", str(out)], env=env, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                       check=True)


def report(name: str, g: dict) -> bool:
    if "diff" in g:
        print(f"{'PASS' if g['pass'] else 'FAIL'}  {name}: frozen {g['frozen']:.4f} -> v4 {g['v2']:.4f}, "
              f"diff {g['diff']:+.4f} [{g['ci_low']:+.4f}, {g['ci_high']:+.4f}]", flush=True)
    else:
        print(f"{'PASS' if g['pass'] else 'FAIL'}  {name}: {g}", flush=True)
    return g["pass"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "runs/v4_gates"))
    a = ap.parse_args()
    out = Path(a.out)
    gates: dict[str, dict] = {}

    def finish(ok: bool) -> None:
        (out / "gates.json").write_text(json.dumps({"gates": gates, "all_pass": ok}, indent=2), encoding="utf-8")
        print("ALL GATES PASSED" if ok else "A GATE FAILED - v4 stays dev-only; the frozen system is unchanged")
        sys.exit(0 if ok else 1)

    # G1
    job(["demo.coding_session.run_scenarios"], out / "v4_scenarios", "v4", "summary.json")
    f = json.loads((ROOT / "results/final/demo_scenarios/summary.json").read_text(encoding="utf-8"))
    v = json.loads((out / "v4_scenarios/summary.json").read_text(encoding="utf-8"))
    g1 = {"original": v["original"]["adaptive"], "held_out_frozen": f["held_out"]["adaptive"]["caught"],
          "held_out_v4": v["held_out"]["adaptive"]["caught"], "of": v["held_out"]["adaptive"]["of"]}
    g1["pass"] = g1["original"]["caught"] == g1["original"]["of"] and g1["held_out_v4"] >= g1["held_out_frozen"]
    gates["G1 coding demo + held-out scenarios"] = g1
    if not report("G1 coding demo + held-out scenarios", g1):
        finish(False)

    # G2
    for system in ("frozen", "v4"):
        job(["eval.synthetic.controller.run", "--split", "val"], out / f"{system}_val", system, "probes.jsonl")
    g = paired(_rows(out / "frozen_val/probes.jsonl"), _rows(out / "v4_val/probes.jsonl"), lambda r: r["adaptive_hit"], "conv")
    gates["G2 synthetic controller val (evidence hit)"] = g
    if not report("G2 synthetic controller val (evidence hit)", g):
        finish(False)

    # G3
    for system in ("frozen", "v4"):
        job(["eval.locomo_plus.run", "--split", "dev", "--warmup-turns", "10"], out / f"{system}_plus", system, "items.jsonl")
    g = paired(_rows(out / "frozen_plus/items.jsonl"), _rows(out / "v4_plus/items.jsonl"), lambda r: r["adaptive"]["cue_hit"], "item")
    gates["G3 LoCoMo-Plus dev (adaptive cue hit)"] = g
    if not report("G3 LoCoMo-Plus dev (adaptive cue hit)", g):
        finish(False)

    # G4
    for system in ("frozen", "v4"):
        job(["eval.locomo.run", "--split", "dev", "--no-nli"], out / f"{system}_locomo", system, "summary.json")
    rows = lambda s: [r for r in _rows(out / f"{s}_locomo/questions.jsonl") if r.get("n_evidence")]  # noqa: E731
    g = paired(rows("frozen"), rows("v4"), lambda r: r["adaptive"]["hit"], "conv")
    gates["G4 LoCoMo dev (adaptive evidence hit)"] = g
    finish(report("G4 LoCoMo dev (adaptive evidence hit)", g))


if __name__ == "__main__":
    main()
