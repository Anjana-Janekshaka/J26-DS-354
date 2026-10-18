"""Learned controller (LR / RF / GBDT) vs the frozen rules (docs/v4_preregistration.md section 4).

    python -m eval.synthetic.controller.learned [--traces runs/colab3/controller_traces]          # train + val, gate
    python -m eval.synthetic.controller.learned --test [--traces ...]                          # test, once

Training rows come from replaying the frozen rule controller over the TRAIN traces: at every probe,
the pre-decision features (``controller.model_based.featurize``) and the objective oracle label.
Each variant is then replayed over VAL as a full controller (it decides every turn, so its own
history feeds the prior-strategy feature). Selection: highest val evidence hit, ties to fewer tokens.
Gate: val hit >= frozen rules' val hit - 0.01.
"""

from __future__ import annotations

import argparse
import gzip
import json
import warnings
from pathlib import Path

from contracts import EscalationEvent, TurnSignal
from controller import ModelBasedController, RuleBasedController
from controller.model_based import featurize, make_model
from eval.metrics import cluster_bootstrap_ci, macro_f1

from .run import load_rule_config
from .trace import STRATEGIES, replay

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / "results_v4"
TAG = "b400_minilm_nli_rerank-noncode"
VARIANTS = ("logistic_regression", "random_forest", "gbdt")


def load_traces(folder: Path, split: str) -> list[dict]:
    with gzip.open(folder / f"{split}_{TAG}.jsonl.gz", "rt", encoding="utf-8") as f:
        f.readline()  # header
        return [json.loads(line) for line in f]


def training_rows(traces: list[dict], rules_factory) -> tuple[list[list[float]], list[str]]:
    X, y = [], []
    for tr in traces:
        ctl = rules_factory()
        for ev in tr["events"]:
            sig = TurnSignal.model_validate(ev["signal"])
            if ev["type"] == "turn":
                ctl.decide(sig, commit=True)
                for e in ev["escalations"]:
                    ctl.register_escalation(EscalationEvent.model_validate(e))
                continue
            if ev["oracle"] == "none":
                continue
            pending = [e for e in ctl._pending if e.source_turn_id != sig.turn_id]
            X.append(featurize(ctl.feature_vector(sig), sig.shift_detected, pending))
            y.append(ev["oracle"])
    return X, y


def score(rows: list[dict]) -> dict:
    labeled = [r for r in rows if r["oracle"] != "none"]
    f1, _ = macro_f1([r["oracle"] for r in labeled], [r["adaptive"] for r in labeled], STRATEGIES)
    return {"evidence_hit": sum(r["adaptive_hit"] for r in rows) / len(rows),
            "mean_tokens": sum(r["adaptive_tokens"] for r in rows) / len(rows), "macro_f1": f1, "n": len(rows)}


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", default=str(ROOT / "runs/colab3/controller_traces"))
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()
    folder = Path(args.traces)
    OUT.mkdir(parents=True, exist_ok=True)
    cfg, default, desc = load_rule_config(False)
    rules = lambda: RuleBasedController(cfg, default)  # noqa: E731
    X, y = training_rows(load_traces(folder, "train"), rules)
    models = {v: make_model(v).fit(X, y) for v in VARIANTS}

    if not args.test:
        val = load_traces(folder, "val")
        res = {"rules (frozen)": score(replay(val, rules))}
        for v, m in models.items():
            res[v] = score(replay(val, lambda m=m, v=v: ModelBasedController(v, m)))
        best = max(VARIANTS, key=lambda v: (res[v]["evidence_hit"], -res[v]["mean_tokens"]))
        gate = res[best]["evidence_hit"] >= res["rules (frozen)"]["evidence_hit"] - 0.01
        out = {"split": "val", "rules": desc, "n_train_rows": len(X), "train_label_counts": {s: y.count(s) for s in STRATEGIES},
               "results": res, "selected": best, "gate_passed": gate}
        (OUT / "learned_val.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"train rows {len(X)}  labels {out['train_label_counts']}")
        for k, r in res.items():
            print(f"  {k:<22} hit {r['evidence_hit']:.4f}  tokens {r['mean_tokens']:.0f}  macro-F1 {r['macro_f1']:.3f}")
        print(f"selected {best}; gate (>= rules - 0.01): {'PASSED' if gate else 'FAILED'}")
        return

    val_out = json.loads((OUT / "learned_val.json").read_text(encoding="utf-8"))
    assert val_out["gate_passed"], "val gate failed: no test run (pre-registration section 4)"
    best = val_out["selected"]
    test = load_traces(folder, "test")
    r_rows = replay(test, rules)
    m_rows = replay(test, lambda: ModelBasedController(best, models[best]))
    paired = [{"conv": a["conv"], "d": float(b["adaptive_hit"]) - float(a["adaptive_hit"])} for a, b in zip(r_rows, m_rows)]
    out = {"split": "test", "selected": best, "rules (frozen)": score(r_rows), best: score(m_rows),
           "learned_minus_rules_hit": cluster_bootstrap_ci(paired, lambda rs: sum(r["d"] for r in rs) / len(rs))}
    (OUT / "learned_test.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
