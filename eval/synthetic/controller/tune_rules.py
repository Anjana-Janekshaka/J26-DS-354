"""Tune the rule-based controller's thresholds on TRAIN + VAL only, then freeze them.

    python -m eval.synthetic.controller.tune_rules [--offline] [--no-nli] [--budget 400]

Grid: ``low_pressure`` x ``min_dwell_turns`` x ``default_strategy`` x ``long_chat_strategy`` x
``loss_escalation_target``. Each candidate is replayed on
the train traces (reported) and selected on the val traces by macro-F1, then acceptable-choice
accuracy, then fewer context tokens. The winner is written to ``frozen_rule_config.json`` with the
full grid, so the choice is auditable. ``run.py`` then uses it on the test split, which this script
never reads.

Note: ``RuleConfig.high_pressure`` is not used by any rule, so it is not tuned.
"""

from __future__ import annotations

import argparse
import itertools
import json
import warnings

from controller import RuleBasedController, RuleConfig

from .run import FROZEN_RULES, add_common_args, rate, resolve_models, selection_scores, traces_for
from .trace import replay

LOW_PRESSURE = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
MIN_DWELL = [0, 1, 2, 3]
DEFAULTS = ["sliding_window", "summarization", "rag"]
LONG_CHAT = ["summarization", "hybrid", "rag"]
LOSS_TARGET = ["rag", "hybrid"]
QA = ["rag", "hybrid", "hybrid_unless_shift"]


def score(rows: list[dict]) -> dict:
    f1, _, acc = selection_scores(rows)
    return {"macro_f1": f1, "acceptable": acc, "hit": rate(rows, lambda r: r["adaptive_hit"]),
            "tokens": rate(rows, lambda r: r["adaptive_tokens"])}


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    add_common_args(ap)
    args = ap.parse_args()
    resolve_models(args)
    train, val = traces_for("train", args), traces_for("val", args)

    grid = []
    for lp, dwell, default, chat, target, qa in itertools.product(LOW_PRESSURE, MIN_DWELL, DEFAULTS, LONG_CHAT, LOSS_TARGET, QA):
        cfg = RuleConfig(low_pressure=lp, min_dwell_turns=dwell, long_chat_strategy=chat, loss_escalation_target=target, qa_strategy=qa)
        make = lambda cfg=cfg, default=default: RuleBasedController(cfg, default_strategy=default)  # noqa: E731
        grid.append({"config": cfg.model_dump(), "default_strategy": default,
                     "train": score(replay(train, make)), "val": score(replay(val, make))})

    key = lambda g: (round(g["val"]["macro_f1"], 4), round(g["val"]["acceptable"], 4), -g["val"]["tokens"])  # noqa: E731
    grid.sort(key=key, reverse=True)
    best = grid[0]
    default_cfg = next(g for g in grid if g["config"] == RuleConfig().model_dump() and g["default_strategy"] == "sliding_window")

    FROZEN_RULES.write_text(json.dumps({
        "config": best["config"],
        "default_strategy": best["default_strategy"],
        "tuned_on": "train+val (selected on val macro-F1, then acceptable accuracy, then tokens)",
        "budget_tokens": args.budget,
        "embedder": args.embedder,
        "nli": args.nli,
        "offline_warning": "tuned in offline mode - re-run with real models before reporting" if args.offline else None,
        "selected": {"train": best["train"], "val": best["val"]},
        "original_defaults": {"train": default_cfg["train"], "val": default_cfg["val"]},
        "grid": grid,
    }, indent=2), encoding="utf-8")

    print(f"{len(grid)} configurations; top 5 on val:")
    for g in grid[:5]:
        c = g["config"]
        print(f"  low_pressure={c['low_pressure']:.1f} dwell={c['min_dwell_turns']} default={g['default_strategy']:<14} "
              f"chat={c['long_chat_strategy']:<13} loss->{c['loss_escalation_target']:<6} qa={c['qa_strategy']:<19} "
              f"val F1={g['val']['macro_f1']:.3f} acc={g['val']['acceptable']:.3f} tok={g['val']['tokens']:.0f} | "
              f"train F1={g['train']['macro_f1']:.3f}")
    d = default_cfg
    print(f"original defaults:  val F1={d['val']['macro_f1']:.3f} acc={d['val']['acceptable']:.3f} | train F1={d['train']['macro_f1']:.3f}")
    print(f"frozen -> {FROZEN_RULES}")


if __name__ == "__main__":
    main()
