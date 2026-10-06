"""Contradiction-flag precision / recall / calibration on the synthetic contradiction pairs.

    python -m eval.synthetic.retrieval.run [--out eval/synthetic/retrieval/results]

For each pair the real two-stage checker runs (MiniLM prefilter -> DeBERTa NLI, or signature diff
for code). Raw scores are collected once; the NLI threshold is chosen on the dev split (max F1)
and reported on the held-out test split. Also reported: one- vs two-directional scoring,
prefilter recall, Brier score and expected calibration error of the raw NLI score.
"""

from __future__ import annotations

import argparse
import json
import warnings
from collections import defaultdict
from pathlib import Path

from contracts.text import code_signatures
from eval.metrics import brier, expected_calibration_error, prf
from retrieval import ContradictionChecker, ContradictionConfig, CrossEncoderNLI, SentenceTransformerEmbedder

from .generate import generate

HERE = Path(__file__).parent


def score_items(items, bidirectional: bool, embedder, nli) -> list[dict]:
    checker = ContradictionChecker(embedder, nli, ContradictionConfig(bidirectional=bidirectional))
    rows = []
    for it in items:
        old_vec, new_vec = embedder.encode([it["older"], it["newer"]])
        verdicts = checker.check(
            "new", it["newer"], new_vec, code_signatures(it["newer"]),
            [("old", it["older"], old_vec, code_signatures(it["older"]))], return_all=True,
        )
        v = max(verdicts, key=lambda x: x.confidence, default=None)
        rows.append({**it, "score": v.confidence if v else None, "verifier": v.verifier if v else "prefilter_rejected"})
    return rows


def evaluate(rows, threshold: float) -> dict:
    tp = sum(1 for r in rows if r["label"] == 1 and r["score"] is not None and r["score"] >= threshold)
    fp = sum(1 for r in rows if r["label"] == 0 and r["score"] is not None and r["score"] >= threshold)
    fn = sum(1 for r in rows if r["label"] == 1) - tp
    return prf(tp, fp, fn)


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    items = generate()
    embedder, nli = SentenceTransformerEmbedder(), CrossEncoderNLI()
    thresholds = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    report: dict = {"n_pairs": len(items), "n_positive": sum(i["label"] for i in items), "variants": {}}

    for name, bidir in (("one_directional", False), ("bidirectional", True)):
        rows = score_items(items, bidir, embedder, nli)
        dev = [r for r in rows if r["split"] == "dev"]
        test = [r for r in rows if r["split"] == "test"]
        sweep = {t: {"dev": evaluate(dev, t), "test": evaluate(test, t)} for t in thresholds}
        best_t = max(thresholds, key=lambda t: (sweep[t]["dev"]["f1"], t))
        nli_rows = [r for r in rows if r["verifier"] == "nli"]
        probs = [r["score"] for r in nli_rows]
        labels = [r["label"] for r in nli_rows]
        prefilter_recall = sum(1 for r in rows if r["label"] == 1 and r["score"] is not None) / max(1, sum(r["label"] for r in rows))
        by_cat = defaultdict(lambda: [0, 0])
        for r in test:
            by_cat[r["category"]][0] += int((r["score"] or 0) >= best_t)
            by_cat[r["category"]][1] += 1
        report["variants"][name] = {
            "threshold_selected_on_dev": best_t,
            "test_at_selected": sweep[best_t]["test"],
            "test_at_default_0.80": sweep[0.8]["test"],
            "sweep": {str(t): v for t, v in sweep.items()},
            "prefilter_recall_of_positives": prefilter_recall,
            "nli_calibration": {"n": len(nli_rows), "brier": brier(probs, labels), "ece_10bin": expected_calibration_error(probs, labels)},
            "test_flag_rate_by_category": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_cat.items())},
        }
        (out / f"scores_{name}.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    (out / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"pairs: {report['n_pairs']} ({report['n_positive']} positive)\n")
    for name, v in report["variants"].items():
        t = v["test_at_selected"]
        print(f"[{name}] threshold (dev-selected) = {v['threshold_selected_on_dev']}")
        print(f"   test P/R/F1 = {t['precision']:.3f} / {t['recall']:.3f} / {t['f1']:.3f}   (tp={t['tp']} fp={t['fp']} fn={t['fn']})")
        print(f"   prefilter recall of positives = {v['prefilter_recall_of_positives']:.3f}")
        c = v["nli_calibration"]
        print(f"   NLI calibration on {c['n']} verified pairs: Brier={c['brier']:.3f}  ECE={c['ece_10bin']:.3f}")
        print("   test flag rate by category: " + ", ".join(f"{k} {x}" for k, x in v["test_flag_rate_by_category"].items()))
    print(f"\nwritten: {out / 'summary.json'}")


if __name__ == "__main__":
    main()
