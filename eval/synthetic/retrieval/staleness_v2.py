"""Staleness v2: NLI + cheap cues in a logistic regression (docs/v4_preregistration.md section 2).

    python -m eval.synthetic.retrieval.staleness_v2            # dev: fit, out-of-fold threshold, gate
    python -m eval.synthetic.retrieval.staleness_v2 --test     # test, once, after the gate

Each pair runs through the real v1 checker (prefilter -> bidirectional NLI, signature diff for code).
The NLI calls are recorded so both directions are available as features. Code pairs flagged by the
signature diff stay flagged and prefilter-rejected pairs stay unflagged, exactly as in v1; only
NLI-verified pairs are scored by the regression.
"""

from __future__ import annotations

import argparse
import json
import re
import warnings
from pathlib import Path

import numpy as np

from contracts.text import code_signatures
from retrieval import ContradictionChecker, ContradictionConfig, CrossEncoderNLI, SentenceTransformerEmbedder

from .generate import generate

HERE = Path(__file__).parent
OUT = HERE / "results_v4"
CUE = re.compile(r"\b(moved|now|no longer|anymore|any more|switched|changed|left|quit|instead|these days|used to|"
                 r"not anymore|stopped|started|new)\b", re.I)
V1_THRESHOLD = 0.95


class RecordingNLI:
    def __init__(self, inner):
        self.inner, self.calls = inner, []

    def contradiction_prob(self, pairs):
        p = self.inner.contradiction_prob(pairs)
        self.calls.append(list(p))
        return p


def features(items, emb, nli) -> list[dict]:
    rec = RecordingNLI(nli)
    checker = ContradictionChecker(emb, rec, ContradictionConfig(bidirectional=True))
    rows = []
    for it in items:
        rec.calls = []
        old_vec, new_vec = emb.encode([it["older"], it["newer"]])
        verdicts = checker.check("new", it["newer"], new_vec, code_signatures(it["newer"]),
                                 [("old", it["older"], old_vec, code_signatures(it["older"]))], return_all=True)
        v = max(verdicts, key=lambda x: x.confidence, default=None)
        row = {**it, "verifier": v.verifier if v else "prefilter_rejected", "v1_score": v.confidence if v else None}
        if v is not None and v.verifier == "nli" and len(rec.calls) == 2:
            fwd, rev = rec.calls
            row["f_min"] = float(max(min(a, b) for a, b in zip(fwd, rev)))
            row["f_max"] = float(max(max(a, b) for a, b in zip(fwd, rev)))
            row["f_cos"] = float(old_vec @ new_vec)
            row["f_cue"] = float(bool(CUE.search(it["newer"])))
        rows.append(row)
    return rows


def X(rows):
    return np.array([[r["f_min"], r["f_max"], r["f_cos"], r["f_cue"]] for r in rows])


def flagged_v1(r) -> bool:
    return r["v1_score"] is not None and r["v1_score"] >= V1_THRESHOLD


def metrics(rows, flag) -> dict:
    tp = int(sum(bool(flag(r)) and r["label"] == 1 for r in rows))
    fp = int(sum(bool(flag(r)) and r["label"] == 0 for r in rows))
    fn = int(sum((not flag(r)) and r["label"] == 1 for r in rows))
    neg = sum(r["label"] == 0 for r in rows)
    p = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return {"precision": p, "recall": rc, "f1": 2 * p * rc / (p + rc) if p + rc else 0.0, "tp": tp, "fp": fp, "fn": fn,
            "stale_fact_leak_rate": 1 - rc, "false_supersession_rate": fp / neg if neg else 0.0}


def v2_flag(prob: dict, thr: float):
    def f(r):
        if r["verifier"] == "signature_diff":
            return True
        if r["verifier"] != "nli" or "f_min" not in r:
            return False
        return prob[r["id"]] >= thr
    return f


def main() -> None:
    warnings.filterwarnings("ignore")
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold

    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cache = OUT / "staleness_features.jsonl"
    if cache.exists():
        rows = [json.loads(x) for x in cache.read_text(encoding="utf-8").splitlines() if x.strip()]
    else:
        rows = features(generate(), SentenceTransformerEmbedder(), CrossEncoderNLI())
        cache.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    dev = [r for r in rows if r["split"] == "dev"]
    test = [r for r in rows if r["split"] == "test"]
    dev_nli = [r for r in dev if "f_min" in r]
    y = np.array([r["label"] for r in dev_nli])

    if not args.test:
        oof = np.zeros(len(dev_nli))
        for tr, va in StratifiedKFold(5, shuffle=True, random_state=0).split(X(dev_nli), y):
            m = LogisticRegression(C=1.0, max_iter=1000).fit(X(dev_nli)[tr], y[tr])
            oof[va] = m.predict_proba(X(dev_nli)[va])[:, 1]
        prob = {r["id"]: float(p) for r, p in zip(dev_nli, oof)}
        cands = sorted(set(np.round(oof, 4)))
        best_t = float(max(cands, key=lambda t: (metrics(dev, v2_flag(prob, t))["f1"], t)))
        v2 = metrics(dev, v2_flag(prob, best_t))
        v1 = metrics(dev, flagged_v1)
        gate = v2["f1"] > v1["f1"] and v2["false_supersession_rate"] <= v1["false_supersession_rate"]
        model = LogisticRegression(C=1.0, max_iter=1000).fit(X(dev_nli), y)
        out = {"split": "dev", "n_nli_pairs": len(dev_nli), "threshold_oof": best_t, "v1_dev": v1, "v2_dev_out_of_fold": v2,
               "gate_passed": gate, "coef": dict(zip(["nli_min", "nli_max", "cosine", "change_cue"], model.coef_[0].tolist())),
               "intercept": float(model.intercept_[0])}
        (OUT / "staleness_v2_dev.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(json.dumps({k: out[k] for k in ("threshold_oof", "v1_dev", "v2_dev_out_of_fold", "gate_passed", "coef")}, indent=2))
        return

    dev_out = json.loads((OUT / "staleness_v2_dev.json").read_text(encoding="utf-8"))
    assert dev_out["gate_passed"], "dev gate failed: no test run (pre-registration section 2)"
    model = LogisticRegression(C=1.0, max_iter=1000).fit(X(dev_nli), y)
    test_nli = [r for r in test if "f_min" in r]
    prob = {r["id"]: float(p) for r, p in zip(test_nli, model.predict_proba(X(test_nli))[:, 1])}
    out = {"split": "test", "threshold": dev_out["threshold_oof"], "v1_test": metrics(test, flagged_v1),
           "v2_test": metrics(test, v2_flag(prob, dev_out["threshold_oof"]))}
    (OUT / "staleness_v2_test.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
