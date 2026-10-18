"""Staleness metrics in the form MemStrata (arXiv 2606.26511) reports them, on our frozen scores.

    python -m eval.synthetic.retrieval.staleness [--scores runs/final/retrieval/scores_bidirectional.jsonl]

Uses the per-pair scores already written by ``eval.synthetic.retrieval.run`` (no re-scoring, no
tuning; the threshold is the one selected on dev). Reports on the test split:

  * stale-fact leak rate       - true contradictions NOT flagged (1 - recall): the stale value stays live
  * false-supersession rate    - compatible pairs wrongly flagged (a current fact would be retired)
  * leak rate by verifier      - structural (code signature diff) vs NLI
  * cosine AUROC               - can embedding similarity alone tell contradictions from compatible
                                 pairs? (MemStrata reports 0.59, near chance)
  * NLI AUROC                  - the same question for our verifier score
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def auroc(pos: list[float], neg: list[float]) -> float:
    if not pos or not neg:
        return float("nan")
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", default=str(ROOT / "runs/final/retrieval/scores_bidirectional.jsonl"))
    ap.add_argument("--summary", default=str(ROOT / "runs/final/retrieval/summary.json"))
    ap.add_argument("--out", default=str(ROOT / "runs/final/retrieval/staleness.json"))
    args = ap.parse_args()

    rows = [json.loads(line) for line in Path(args.scores).read_text(encoding="utf-8").splitlines() if line.strip()]
    thr = json.loads(Path(args.summary).read_text(encoding="utf-8"))["variants"]["bidirectional"]["threshold_selected_on_dev"]
    test = [r for r in rows if r["split"] == "test"]
    pos = [r for r in test if r["label"] == 1]
    neg = [r for r in test if r["label"] == 0]
    flagged = lambda r: (r.get("score") or 0.0) >= thr  # noqa: E731

    by_ver: dict[str, list[dict]] = defaultdict(list)
    for r in pos:
        by_ver["structural (signature diff)" if r.get("verifier") == "signature_diff" else "nli / prefilter"].append(r)

    from retrieval import SentenceTransformerEmbedder

    emb = SentenceTransformerEmbedder()
    vec = emb.encode([r["older"] for r in test] + [r["newer"] for r in test])
    n = len(test)
    cos = {r["id"]: float(vec[i] @ vec[n + i]) for i, r in enumerate(test)}

    out = {
        "split": "test",
        "threshold": thr,
        "n_contradictions": len(pos),
        "n_compatible": len(neg),
        "stale_fact_leak_rate": sum(not flagged(r) for r in pos) / len(pos),
        "false_supersession_rate": sum(flagged(r) for r in neg) / len(neg),
        "leak_rate_by_verifier": {k: {"n": len(v), "leak_rate": sum(not flagged(r) for r in v) / len(v)} for k, v in by_ver.items()},
        "cosine_auroc_contradiction_vs_compatible": auroc([cos[r["id"]] for r in pos], [cos[r["id"]] for r in neg]),
        "nli_auroc_contradiction_vs_compatible": auroc([r.get("score") or 0.0 for r in pos], [r.get("score") or 0.0 for r in neg]),
        "mean_cosine": {"contradiction": float(np.mean([cos[r["id"]] for r in pos])), "compatible": float(np.mean([cos[r["id"]] for r in neg]))},
    }
    # Fair flagger comparison: each signal gets its own threshold chosen on dev (max F1), reported on test.
    dev = [r for r in rows if r["split"] == "dev"]
    vd = emb.encode([r["older"] for r in dev] + [r["newer"] for r in dev])
    for i, r in enumerate(dev):
        r["cos"] = float(vd[i] @ vd[len(dev) + i])
    for r in test:
        r["cos"] = cos[r["id"]]
    for r in dev + test:
        r["nli"] = r.get("score") or 0.0

    def ev(rs, key, t):
        tp = sum(r[key] >= t and r["label"] == 1 for r in rs)
        fp = sum(r[key] >= t and r["label"] == 0 for r in rs)
        fn = sum(r[key] < t and r["label"] == 1 for r in rs)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        return {"precision": prec, "recall": rec, "f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0,
                "leak_rate": 1 - rec, "false_supersession_rate": fp / max(1, sum(r["label"] == 0 for r in rs))}

    out["flagger_comparison_test"] = {}
    for key, name in (("cos", "embedding similarity only"), ("nli", "NLI stage (ours)")):
        ts = sorted({round(r[key], 3) for r in dev})
        best = max(ts, key=lambda t: (ev(dev, key, t)["f1"], t))
        out["flagger_comparison_test"][name] = {"threshold_selected_on_dev": best, **ev(test, key, best)}
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
