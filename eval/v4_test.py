"""v4b test runs, each exactly once, after all gates passed (docs/v4_preregistration.md, amendment v4b).

    python -m eval.v4_test [--system v4b] [--out runs/v4b_test]

Runs every test split with the candidate system (skipping any already written, so an interruption
resumes without re-running a finished split), then reports candidate - frozen with paired 95%
conversation-level CIs against the frozen system's recorded test outputs (runs/colab3/final, and the
frozen BEAM run). Writes <out>/comparison.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from eval.v2_gate import _rows, paired
from eval.v4_gate import job

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "runs/colab3/final"

# name: (module args, output marker, rows file, frozen rows file, metric, group key, row filter)
SPLITS = {
    "controller": (["eval.synthetic.controller.run", "--split", "test"], "test/probes.jsonl", "test/probes.jsonl",
                   FROZEN / "controller/test/probes.jsonl", lambda r: r["adaptive_hit"], "conv", None),
    "locomo": (["eval.locomo.run", "--split", "test", "--no-nli"], "summary.json", "questions.jsonl",
               FROZEN / "locomo/questions.jsonl", lambda r: r["adaptive"]["hit"], "conv", lambda r: r.get("n_evidence")),
    "locomo_stream": (["eval.locomo.stream", "--split", "test"], "summary.json", "questions.jsonl",
                      FROZEN / "locomo_stream/questions.jsonl", lambda r: r["adaptive"]["hit"], "conv", None),
    "locomo_plus": (["eval.locomo_plus.run", "--split", "test", "--warmup-turns", "10"], "items.jsonl", "items.jsonl",
                    FROZEN / "locomo_plus/items.jsonl", lambda r: r["adaptive"]["cue_hit"], "item", None),
    "beam": (["eval.beam.run"], "summary.json", "questions.jsonl", ROOT / "eval/beam/results/questions.jsonl",
             lambda r: r["adaptive"]["evidence_hit"], "conv", lambda r: r["adaptive"]["evidence_hit"] is not None),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", default="v4b")
    ap.add_argument("--out", default=str(ROOT / "runs/v4b_test"))
    a = ap.parse_args()
    out = Path(a.out)
    gates = json.loads((ROOT / f"runs/{a.system}_gates/gates.json").read_text(encoding="utf-8"))
    if not gates["all_pass"]:
        sys.exit(f"{a.system} did not pass every gate: no test runs (pre-registration)")
    comparison = {}
    for name, (module, marker, rows_file, frozen_file, metric, group, keep) in SPLITS.items():
        job(module, out / name, a.system, marker)
        cand = _rows(out / name / rows_file)
        froz = _rows(frozen_file)
        if keep:
            cand, froz = [r for r in cand if keep(r)], [r for r in froz if keep(r)]
        g = paired(froz, cand, metric, group)
        comparison[name] = {"frozen": g["frozen"], a.system: g["v2"], "diff": g["diff"], "ci_low": g["ci_low"], "ci_high": g["ci_high"],
                            "n": len(cand)}
        print(f"{name:<14} frozen {g['frozen']:.4f} -> {a.system} {g['v2']:.4f}  diff {g['diff']:+.4f} [{g['ci_low']:+.4f}, {g['ci_high']:+.4f}]",
              flush=True)
        (out / "comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
