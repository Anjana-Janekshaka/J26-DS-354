"""Sliding-window weights chosen on a dev split (docs/v4_preregistration.md section 1).

    python -m eval.synthetic.sliding_window.select_weights            # dev: grid, choice, gate
    python -m eval.synthetic.sliding_window.select_weights --test     # test half, run once after the gate

Dev = even-index conversations of ``generate()``, test = odd-index. The 35-point weight grid runs at
budget 100 on dev; the highest recall wins (ties: fewer tokens, then more relevance weight). The gate
is strictly higher dev recall than equal weights. The test report compares the chosen weights with
equal weights and recency-only at budgets 100 and 220.
"""

from __future__ import annotations

import argparse
import itertools
import json
import warnings
from pathlib import Path

from contracts.text import CachingEmbedder
from retrieval import SentenceTransformerEmbedder
from sliding_window import DynamicSlidingWindow, RecencyOnlyWindow, SlidingWindowConfig, Weights

from .generate import generate
from .run import evaluate, summarize

HERE = Path(__file__).parent
CHOICE = HERE / "results_v4" / "dev_choice.json"


def split(convs: list[dict], name: str) -> list[dict]:
    return [c for i, c in enumerate(convs) if (i % 2 == 0) == (name == "dev")]


def grid() -> list[Weights]:
    out = []
    for a, b, c in itertools.product(range(5), repeat=3):
        d = 4 - a - b - c
        if d >= 0:
            out.append(Weights(relevance=a / 4, freshness=b / 4, importance=c / 4, state=d / 4))
    return out


def dsw(emb, w: Weights):
    return lambda: DynamicSlidingWindow(emb, SlidingWindowConfig(weights=w))


def win_tie_loss(a: list[dict], b: list[dict]) -> dict:
    win = sum(x["hit"] and not y["hit"] for x, y in zip(a, b))
    loss = sum(y["hit"] and not x["hit"] for x, y in zip(a, b))
    return {"win": win, "tie": len(a) - win - loss, "loss": loss}


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()
    CHOICE.parent.mkdir(parents=True, exist_ok=True)
    convs = generate()
    emb = CachingEmbedder(SentenceTransformerEmbedder())
    equal = Weights()

    if not args.test:
        dev = split(convs, "dev")
        rows = []
        for w in grid():
            s = summarize(evaluate(dev, dsw(emb, w), 100))
            rows.append({"weights": w.model_dump(), **s})
        rows.sort(key=lambda r: (-r["recall"], r["mean_tokens"], -r["weights"]["relevance"]))
        eq = next(r for r in rows if all(abs(v - 0.25) < 1e-9 for v in r["weights"].values()))
        best = rows[0]
        gate = best["recall"] > eq["recall"]
        out = {"split": "dev", "n_conversations": len(dev), "budget": 100, "chosen": best, "equal_weights": eq,
               "equal_weights_rank": rows.index(eq) + 1, "gate_passed": gate, "top5": rows[:5]}
        CHOICE.write_text(json.dumps(out, indent=2), encoding="utf-8")
        (CHOICE.parent / "dev_grid.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"dev ({len(dev)} conversations, {best['n']} probes, budget 100)")
        print(f"  chosen {best['weights']}  recall {best['recall']:.3f}")
        print(f"  equal  weights rank #{out['equal_weights_rank']}  recall {eq['recall']:.3f}")
        print(f"  gate (chosen > equal on dev): {'PASSED' if gate else 'FAILED'}")
        return

    choice = json.loads(CHOICE.read_text(encoding="utf-8"))
    assert choice["gate_passed"], "dev gate failed: no test run (pre-registration section 1)"
    chosen = Weights(**choice["chosen"]["weights"])
    test = split(convs, "test")
    report = {"split": "test", "n_conversations": len(test), "chosen_weights": chosen.model_dump(), "budgets": {}}
    for budget in (100, 220):
        raw = {"chosen": evaluate(test, dsw(emb, chosen), budget), "equal": evaluate(test, dsw(emb, equal), budget),
               "recency_only_k8": evaluate(test, lambda: RecencyOnlyWindow(k=8), budget)}
        report["budgets"][budget] = {
            **{k: summarize(v) for k, v in raw.items()},
            "chosen_vs_recency": win_tie_loss(raw["chosen"], raw["recency_only_k8"]),
            "equal_vs_recency": win_tie_loss(raw["equal"], raw["recency_only_k8"]),
            "chosen_vs_equal": win_tie_loss(raw["chosen"], raw["equal"]),
        }
    (CHOICE.parent / "test_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    for budget, r in report["budgets"].items():
        print(f"test, budget {budget}: chosen {r['chosen']['recall']:.3f}  equal {r['equal']['recall']:.3f}  "
              f"recency {r['recency_only_k8']['recall']:.3f}  | chosen vs recency {r['chosen_vs_recency']}  "
              f"chosen vs equal {r['chosen_vs_equal']}")


if __name__ == "__main__":
    main()
