"""DSW vs recency baselines + weight ablation on topic-shift-labeled workloads.

    python -m eval.synthetic.sliding_window.run [--budget 220]

Metric: gold-turn recall - does the selected window contain the turn that planted the fact the
probe asks about. Reported overall and split into current-block vs earlier-block probes, plus the
win/tie/loss rate of DSW against the recency-only baseline, and a 35-point weight-simplex ablation
(steps of 0.25). Topic-shift labels from the dataset drive the state factor; the conversation
manager's own shift detector is scored against those labels too.
"""

from __future__ import annotations

import argparse
import itertools
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

from contracts import ConversationTurn, TokenUsage, TurnSignal
from contracts.text import CachingEmbedder
from conversation_manager import TaskTypeClassifier
from eval.metrics import prf
from retrieval import SentenceTransformerEmbedder
from sliding_window import DynamicSlidingWindow, FixedTokenWindow, RecencyOnlyWindow, SlidingWindowConfig, Weights

from .generate import generate

HERE = Path(__file__).parent
TS = datetime(2026, 10, 6, tzinfo=timezone.utc)


def _signal(tid: str, budget: int, shift: bool) -> TurnSignal:
    return TurnSignal(turn_id=tid, conversation_id="sw", turn_count=1, task_type="qa", token_usage=TokenUsage(used=budget * 2, budget=budget),
                      conversation_state="shift_detected" if shift else "task", timestamp=TS)


def evaluate(convs, factory, budget: int) -> list[dict]:
    rows = []
    for conv in convs:
        win = factory()
        shifts = set(conv["shift_indices"])
        probes_at: dict[int, list[dict]] = {}
        for p in conv["probes"]:
            probes_at.setdefault(p["after_index"], []).append(p)
        for i, m in enumerate(conv["messages"]):
            t = ConversationTurn(turn_id=f"t{i + 1:04d}", role=m["role"], content=m["content"])
            win.observe_signal(_signal(t.turn_id, budget, i in shifts))
            win.ingest(t)
            for p in probes_at.get(i, []):
                sig = _signal(f"t{i + 2:04d}", budget, False)
                win.observe_signal(sig)
                out = win.build_context(sig, p["question"])
                gold = f"t{p['turn_index'] + 1:04d}"
                rows.append({"conv": conv["id"], "kind": p["kind"], "hit": gold in out.quality.selected_turn_ids, "tokens": out.token_count})
    return rows


def summarize(rows) -> dict:
    def rate(rs):
        return sum(r["hit"] for r in rs) / len(rs) if rs else 0.0

    return {
        "recall": rate(rows),
        "recall_current_block": rate([r for r in rows if r["kind"] == "current_block"]),
        "recall_earlier_block": rate([r for r in rows if r["kind"] == "earlier_block"]),
        "mean_tokens": sum(r["tokens"] for r in rows) / len(rows),
        "n": len(rows),
    }


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=220)
    ap.add_argument("--out", default=str(HERE / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    convs = generate()
    emb = CachingEmbedder(SentenceTransformerEmbedder())
    B = args.budget

    systems = {
        "dsw_equal_weights": lambda: DynamicSlidingWindow(emb, SlidingWindowConfig()),
        "recency_only_k8": lambda: RecencyOnlyWindow(k=8),
        "fixed_token_window": lambda: FixedTokenWindow(),
    }
    raw = {name: evaluate(convs, f, B) for name, f in systems.items()}
    results = {name: summarize(rows) for name, rows in raw.items()}

    dsw, rec = raw["dsw_equal_weights"], raw["recency_only_k8"]
    win = sum(1 for a, b in zip(dsw, rec) if a["hit"] and not b["hit"])
    loss = sum(1 for a, b in zip(dsw, rec) if b["hit"] and not a["hit"])
    tie = len(dsw) - win - loss
    results["dsw_vs_recency_only"] = {"win": win, "tie": tie, "loss": loss, "win_rate": win / len(dsw), "loss_rate": loss / len(dsw)}

    grid = []
    steps = [0, 1, 2, 3, 4]
    for a, b, c in itertools.product(steps, steps, steps):
        d = 4 - a - b - c
        if d < 0:
            continue
        w = Weights(relevance=a / 4, freshness=b / 4, importance=c / 4, state=d / 4)
        if sum(w.as_tuple()) == 0:
            continue
        s = summarize(evaluate(convs, lambda w=w: DynamicSlidingWindow(emb, SlidingWindowConfig(weights=w)), B))
        grid.append({"weights": w.model_dump(), **s})
    grid.sort(key=lambda g: -g["recall"])
    equal = next(g for g in grid if all(abs(v - 0.25) < 1e-9 for v in g["weights"].values()))
    results["ablation"] = {"n_configs": len(grid), "best": grid[:5], "worst": grid[-3:], "equal_weights_rank": grid.index(equal) + 1}
    for factor in ("relevance", "freshness", "importance", "state"):
        drop = [g for g in grid if g["weights"][factor] == 0 and abs(sum(g["weights"].values()) - 1) < 1e-9]
        results["ablation"][f"best_without_{factor}"] = max((g["recall"] for g in drop), default=None)

    # conversation-manager shift detector vs the labels
    tp = fp = fn = 0
    for conv in convs:
        clf = TaskTypeClassifier(embedder=emb)
        labels = set(conv["shift_indices"][1:])
        for i, m in enumerate(conv["messages"]):
            if m["role"] != "user":
                continue
            pred = clf.observe(m["content"], decision_point=True).shift_detected
            gold = i in labels
            tp += pred and gold
            fp += pred and not gold
            fn += gold and not pred
    results["shift_detector_vs_labels"] = prf(tp, fp, fn)

    (out / "summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    (out / "ablation_grid.json").write_text(json.dumps(grid, indent=2), encoding="utf-8")
    print(f"{len(convs)} conversations, {results['dsw_equal_weights']['n']} probes, budget {B} tokens\n")
    print(f"{'system':<22}{'recall':>8}{'current':>9}{'earlier':>9}{'tokens':>8}")
    for name in systems:
        r = results[name]
        print(f"{name:<22}{r['recall']:>8.3f}{r['recall_current_block']:>9.3f}{r['recall_earlier_block']:>9.3f}{r['mean_tokens']:>8.0f}")
    v = results["dsw_vs_recency_only"]
    print(f"\nDSW vs recency-only: win {v['win']} / tie {v['tie']} / loss {v['loss']}  (win rate {v['win_rate']:.3f}, loss rate {v['loss_rate']:.3f})")
    ab = results["ablation"]
    print(f"\nablation ({ab['n_configs']} weight configs): equal weights rank #{ab['equal_weights_rank']}")
    for g in ab["best"]:
        print(f"   {g['weights']}  recall={g['recall']:.3f}")
    for factor in ("relevance", "freshness", "importance", "state"):
        print(f"   best recall with {factor}=0: {ab[f'best_without_{factor}']:.3f}")
    s = results["shift_detector_vs_labels"]
    print(f"\nshift detector vs labels: P={s['precision']:.3f} R={s['recall']:.3f} F1={s['f1']:.3f}")
    print(f"written: {out / 'summary.json'}")


if __name__ == "__main__":
    main()
