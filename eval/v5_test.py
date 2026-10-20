"""v5_recall test runs, each exactly once, after all gates passed (docs/v5_recall_preregistration.md).

    python -m eval.v5_test [--system v5_recall] [--out runs/v5_recall_test]

The frozen per-question test outputs are not kept in the repository, so every split runs the frozen
system and the candidate back to back (each skipped if already written, so an interruption resumes).
Reports candidate - frozen with paired 95% CIs and, for BEAM, adaptive - RAG for both systems.
Writes <out>/comparison.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from eval.v2_gate import _rows, paired
from eval.v4_gate import job

ROOT = Path(__file__).resolve().parents[1]

# name: (module args, output marker, rows file, metric, group key, row filter)
SPLITS = {
    "beam": (["eval.beam.run"], "summary.json", "questions.jsonl",
             lambda r: r["adaptive"]["evidence_hit"], "conv", lambda r: r["adaptive"]["evidence_hit"] is not None),
    "beam_answer": (None, None, "questions.jsonl",
                    lambda r: r["adaptive"]["answer_in_context"], "conv", lambda r: r["adaptive"]["answer_in_context"] is not None),
    "controller": (["eval.synthetic.controller.run", "--split", "test"], "test/probes.jsonl", "test/probes.jsonl",
                   lambda r: r["adaptive_hit"], "conv", None),
    "locomo": (["eval.locomo.run", "--split", "test", "--no-nli"], "summary.json", "questions.jsonl",
               lambda r: r["adaptive"]["hit"], "conv", lambda r: r.get("n_evidence")),
    "locomo_plus": (["eval.locomo_plus.run", "--split", "test", "--warmup-turns", "10"], "items.jsonl", "items.jsonl",
                    lambda r: r["adaptive"]["cue_hit"], "item", None),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", default="v5_recall")
    ap.add_argument("--out", default=str(ROOT / "runs/v5_recall_test"))
    ap.add_argument("--only", nargs="*", help="run only these splits (default: all, in order)")
    a = ap.parse_args()
    out = Path(a.out)
    gates = json.loads((ROOT / f"runs/{a.system}_gates/gates.json").read_text(encoding="utf-8"))
    if not gates["all_pass"]:
        sys.exit(f"{a.system} did not pass every gate: no test runs (pre-registration)")
    cpath = out / "comparison.json"
    comparison = json.loads(cpath.read_text(encoding="utf-8")) if cpath.exists() else {}
    for name, (module, marker, rows_file, metric, group, keep) in SPLITS.items():
        base = name.split("_answer")[0]
        if a.only and base not in a.only:
            continue
        if module:
            for system in ("frozen", a.system):
                job(module, out / f"{system}_{name}", system, marker)
        froz, cand = _rows(out / f"frozen_{base}" / rows_file), _rows(out / f"{a.system}_{base}" / rows_file)
        if keep:
            froz, cand = [r for r in froz if keep(r)], [r for r in cand if keep(r)]
        g = paired(froz, cand, metric, group)
        comparison[name] = {"frozen": g["frozen"], a.system: g["v2"], "diff": g["diff"], "ci_low": g["ci_low"],
                            "ci_high": g["ci_high"], "n": len(cand)}
        print(f"{name:<12} frozen {g['frozen']:.4f} -> {a.system} {g['v2']:.4f}  diff {g['diff']:+.4f} "
              f"[{g['ci_low']:+.4f}, {g['ci_high']:+.4f}]", flush=True)
        if base == "beam":
            key = "evidence_hit" if name == "beam" else "answer_in_context"
            for system, rows in (("frozen", froz), (a.system, cand)):
                r = paired([{**x, "_m": x["rag"][key]} for x in rows], [{**x, "_m": x["adaptive"][key]} for x in rows],
                           lambda x: x["_m"], "conv")
                comparison[name][f"{system}_adaptive_minus_rag"] = {k: r[k] for k in ("diff", "ci_low", "ci_high")}
                print(f"  {system}: adaptive - RAG {r['diff']:+.4f} [{r['ci_low']:+.4f}, {r['ci_high']:+.4f}]", flush=True)
        cpath.write_text(json.dumps(comparison, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
