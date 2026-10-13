"""Controller evaluation on held-out phrasing, with baselines and conversation-level CIs.

    python -m eval.synthetic.controller.run                      # test split (family C), real models
    python -m eval.synthetic.controller.run --split val          # tuning split
    python -m eval.synthetic.controller.run --split legacy       # the original 30-conversation set
    python -m eval.synthetic.controller.run --offline            # no model downloads (hashing embedder,
                                                                 # no NLI) - for checking code only
    python -m eval.synthetic.controller.run --judge              # + LLM-judge half of the oracle

Protocol (Phase 1):
* Conversations come in phrasing families (see ``families.py``). The rules were written against
  family A; ``splits.json`` puts A + most of B in train, the rest of B in val, and family C in test.
  Rule thresholds are tuned on train/val only (``tune_rules.py`` -> ``frozen_rule_config.json``).
* The pipeline runs once per conversation and is cached as a trace (``trace.py``); controllers are
  evaluated by replaying the trace.
* Oracle (objective source): at each probe all four strategies' contexts are assembled from the
  same module outputs; a strategy "hits" when its context satisfies the evidence requirement. The
  oracle label is the cheapest hitting strategy (``eval.metrics.oracle_label``). Probes no strategy
  answers are excluded from F1 but counted in hit rates.
* Baselines: each fixed strategy, always-hybrid, random choice (expected value), majority class
  (most common oracle label in TRAIN), and the oracle itself (upper bound).
* 95% CIs resample whole conversations (``eval.metrics.cluster_bootstrap_ci``).
"""

from __future__ import annotations

import argparse
import json
import random
import warnings
from collections import Counter
from pathlib import Path

from controller import RuleBasedController, RuleConfig
from eval.metrics import cluster_bootstrap_ci, macro_f1

from .generate import GENERATOR_VERSION, load_split
from .trace import SINGLES, STRATEGIES, build_traces, replay

HERE = Path(__file__).parent
FROZEN_RULES = HERE / "frozen_rule_config.json"

JUDGE_SYSTEM = (
    "You are grading memory contexts for an assistant. Given a user message and four candidate contexts "
    "labelled A-D, answer with the single letter of the context that best lets the assistant respond "
    "correctly with current (not stale) information, preferring the shorter context when equally good."
)


# --------------------------------------------------------------------------- shared helpers
def traces_for(split: str, args) -> list[dict]:
    convs = load_split(split)
    tag = f"{split}_b{args.budget}_{args.embedder}_{'nli' if args.nli else 'nonli'}" + ("" if args.embedder == "hashing" else "_rerank-noncode")
    version = "legacy" if split == "legacy" else GENERATOR_VERSION
    return build_traces(convs, args.budget, args.embedder, args.nli, Path(args.cache_dir) / f"{tag}.jsonl.gz",
                        rebuild=args.rebuild_traces, version=version)


def load_rule_config(use_default: bool) -> tuple[RuleConfig, str, str]:
    """(config, default_strategy, description). Uses the frozen config unless told not to."""
    if not use_default and FROZEN_RULES.exists():
        data = json.loads(FROZEN_RULES.read_text(encoding="utf-8"))
        return (RuleConfig(**data["config"]), data.get("default_strategy", "sliding_window"),
                f"frozen ({FROZEN_RULES.name}, tuned on {data.get('tuned_on', '?')})")
    return RuleConfig(), "sliding_window", "default RuleConfig()"


def rate(rows: list[dict], fn) -> float:
    return sum(fn(r) for r in rows) / len(rows) if rows else 0.0


def selection_scores(rows: list[dict], pred_key: str = "adaptive") -> tuple[float, dict, float]:
    labeled = [r for r in rows if r["oracle"] != "none"]
    f1, per = macro_f1([r["oracle"] for r in labeled], [r[pred_key] for r in labeled], STRATEGIES)
    acc = rate(labeled, lambda r: r[pred_key] in r["acceptable"])
    return f1, per, acc


def summarize(rows: list[dict], majority: str, n_boot: int) -> dict:
    """All headline numbers for one split. Every comparison with the adaptive controller gets a CI."""
    ci = lambda stat: cluster_bootstrap_ci(rows, stat, n_boot=n_boot)  # noqa: E731
    labeled = [r for r in rows if r["oracle"] != "none"]
    f1, per, acc = selection_scores(rows)

    hit = {"adaptive": ci(lambda rs: rate(rs, lambda r: r["adaptive_hit"]))}
    for s in STRATEGIES:
        hit[s] = ci(lambda rs, s=s: rate(rs, lambda r: r["hits"][s]))
    hit["oracle_upper_bound"] = rate(rows, lambda r: any(r["hits"].values()))
    hit["random_expected"] = rate(rows, lambda r: sum(r["hits"].values()) / len(STRATEGIES))
    hit[f"majority ({majority})"] = rate(rows, lambda r: r["hits"][majority])

    tokens = {"adaptive": rate(rows, lambda r: r["adaptive_tokens"]), **{s: rate(rows, lambda r, s=s: r["tokens"][s]) for s in STRATEGIES}}
    tokens["oracle_choice"] = rate(labeled, lambda r: r["tokens"][r["oracle"]])

    best = max(SINGLES, key=lambda s: hit[s]["estimate"])
    deltas = {
        f"hit: adaptive - best single fixed ({best})": ci(lambda rs: rate(rs, lambda r: r["adaptive_hit"] - r["hits"][best])),
        "hit: adaptive - always_hybrid": ci(lambda rs: rate(rs, lambda r: r["adaptive_hit"] - r["hits"]["hybrid"])),
        "tokens: adaptive - always_hybrid": ci(lambda rs: rate(rs, lambda r: r["adaptive_tokens"] - r["tokens"]["hybrid"])),
        f"tokens: adaptive - best single fixed ({best})": ci(lambda rs: rate(rs, lambda r: r["adaptive_tokens"] - r["tokens"][best])),
    }

    maj_rows = [{**r, "majority": majority} for r in rows]
    maj_f1, _, maj_acc = selection_scores(maj_rows, "majority")
    rnd = []
    for seed in range(20):
        g = random.Random(seed)
        rr = [{**r, "random": g.choice(STRATEGIES)} for r in rows]
        rnd.append(selection_scores(rr, "random")[0])

    by_kind = {}
    for kind in sorted({r["kind"] for r in rows}):
        rs = [r for r in rows if r["kind"] == kind]
        by_kind[kind] = {
            "n": len(rs),
            "adaptive_choice": dict(Counter(r["adaptive"] for r in rs)),
            "task_type": dict(Counter(r["task_type"] for r in rs)),
            "oracle": dict(Counter(r["oracle"] for r in rs)),
            "adaptive_hit": rate(rs, lambda r: r["adaptive_hit"]),
            **{f"{s}_hit": rate(rs, lambda r, s=s: r["hits"][s]) for s in STRATEGIES},
            "adaptive_tokens": rate(rs, lambda r: r["adaptive_tokens"]),
        }

    return {
        "n_probes": len(rows),
        "n_conversations": len({r["conv"] for r in rows}),
        "n_with_oracle_label": len(labeled),
        "oracle_label_distribution": dict(Counter(r["oracle"] for r in rows)),
        "selection": {
            "adaptive_macro_f1": ci(lambda rs: selection_scores(rs)[0]),
            "adaptive_acceptable_choice_accuracy": ci(lambda rs: selection_scores(rs)[2]),
            "per_class": per,
            "majority_macro_f1": maj_f1,
            "majority_acceptable_choice_accuracy": maj_acc,
            "random_macro_f1_mean_of_20": sum(rnd) / len(rnd),
        },
        "evidence_hit_rate": hit,
        "mean_context_tokens": tokens,
        "best_single_fixed_baseline": best,
        "differences": deltas,
        "by_probe_kind": by_kind,
        "_check": {"macro_f1_point": f1, "acceptable_point": acc},
    }


def run_judge(rows: list[dict], traces: list[dict], judge) -> dict:
    from integration.llm_client import describe

    ctx = {(t["conv"], ev["query"]): ev.get("contexts") for t in traces for ev in t["events"] if ev["type"] == "probe"}
    letters = "ABCD"
    pairs = []
    for r in rows:
        if r["oracle"] == "none":
            continue
        c = ctx.get((r["conv"], r["query"]))
        if not c:
            continue
        body = f"User message: {r['query']}\n\n" + "\n\n".join(f"[{letters[k]}]\n{c[s]}" for k, s in enumerate(STRATEGIES))
        try:
            ans = judge(JUDGE_SYSTEM, body).strip().upper()[:1]
        except Exception as e:  # pragma: no cover - network
            r["judge_error"] = str(e)
            continue
        r["judge"] = STRATEGIES[letters.index(ans)] if ans in letters else None
        if r["judge"]:
            pairs.append((r["oracle"], r["judge"]))
    return {"status": "run", "judge_model": describe(judge), "n": len(pairs),
            "agreement": sum(a == b for a, b in pairs) / max(1, len(pairs)),
            "cohen_kappa": cohen_kappa([a for a, _ in pairs], [b for _, b in pairs])}


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def add_common_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--budget", type=int, default=400)
    ap.add_argument("--offline", action="store_true", help="hashing embedder + no NLI: no model downloads (code checks only)")
    ap.add_argument("--no-nli", action="store_true", help="real embedder but skip the NLI contradiction stage")
    ap.add_argument("--rebuild-traces", action="store_true")
    ap.add_argument("--cache-dir", default=str(HERE / "results" / "traces"))


def resolve_models(args) -> None:
    args.embedder = "hashing" if args.offline else "minilm"
    args.nli = not (args.offline or args.no_nli)


# --------------------------------------------------------------------------- main
def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["train", "val", "test", "legacy"], default="test")
    ap.add_argument("--default-rules", action="store_true", help="ignore frozen_rule_config.json")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--judge", action="store_true", help="also collect LLM-judge labels (needs an LLM configured)")
    ap.add_argument("--out", default=str(HERE / "results"))
    add_common_args(ap)
    args = ap.parse_args()
    resolve_models(args)
    out = Path(args.out) / args.split
    out.mkdir(parents=True, exist_ok=True)

    cfg, default_strategy, cfg_source = load_rule_config(args.default_rules)
    print(f"split={args.split}  budget={args.budget}  embedder={args.embedder}  nli={args.nli}  rules={cfg_source}")
    traces = traces_for(args.split, args)
    rows = replay(traces, lambda: RuleBasedController(cfg, default_strategy=default_strategy))

    # Majority class comes from TRAIN labels, never from the split being evaluated.
    train_traces = traces if args.split == "train" else (traces_for("train", args) if args.split != "legacy" else traces)
    train_labels = [ev["oracle"] for t in train_traces for ev in t["events"] if ev["type"] == "probe" and ev["oracle"] != "none"]
    majority = Counter(train_labels).most_common(1)[0][0]

    summary = summarize(rows, majority, args.n_boot)
    summary.update({
        "split": args.split,
        "budget_tokens": args.budget,
        "embedder": args.embedder,
        "nli": args.nli,
        "rule_config": {**cfg.model_dump(), "default_strategy": default_strategy},
        "rule_config_source": cfg_source,
        "majority_label_from_train": majority,
        "llm_judge_oracle": {"status": "not run (pass --judge with an LLM configured)"},
    })
    if args.offline:
        summary["WARNING"] = "offline mode (hashing embedder, no NLI): numbers check the code, they are NOT results"
    if args.judge:
        from integration.llm_client import get_llm

        judge = get_llm(out / "judge_cache.jsonl", role="judge")
        summary["llm_judge_oracle"] = (run_judge(rows, traces, judge) if judge is not None else
                                       {"status": "not run: no LLM configured (CEAI_LLM_BASE_URL + CEAI_LLM_MODEL, or Claude credentials)"})

    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "probes.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    print_report(summary)
    print(f"\nwritten: {out / 'summary.json'}")


def fmt(c: dict) -> str:
    return f"{c['estimate']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]"


def print_report(s: dict) -> None:
    if "WARNING" in s:
        print(f"\n!! {s['WARNING']}")
    print(f"\n{s['n_probes']} probes / {s['n_conversations']} conversations; oracle labels: {s['oracle_label_distribution']}")
    sel = s["selection"]
    print(f"strategy-selection macro-F1   adaptive {fmt(sel['adaptive_macro_f1'])}   "
          f"majority {sel['majority_macro_f1']:.3f}   random {sel['random_macro_f1_mean_of_20']:.3f}")
    print(f"acceptable-choice accuracy    adaptive {fmt(sel['adaptive_acceptable_choice_accuracy'])}   "
          f"majority {sel['majority_acceptable_choice_accuracy']:.3f}")
    print("\nevidence hit rate / mean context tokens:")
    hit, tok = s["evidence_hit_rate"], s["mean_context_tokens"]
    for k, v in hit.items():
        est = v["estimate"] if isinstance(v, dict) else v
        ci = f" [{v['ci_low']:.3f}, {v['ci_high']:.3f}]" if isinstance(v, dict) else ""
        t = tok.get(k, tok.get("oracle_choice") if k == "oracle_upper_bound" else None)
        print(f"  {k:<26} {est:.3f}{ci:<18} {'' if t is None else f'{t:6.0f} tok'}")
    print("\ndifferences (95% CI, resampling conversations):")
    for k, v in s["differences"].items():
        print(f"  {k:<48} {fmt(v)}")
    print("\nby probe kind:")
    for kind, v in s["by_probe_kind"].items():
        fixed = "  ".join(f"{x[:4]}={v[f'{x}_hit']:.2f}" for x in STRATEGIES)
        print(f"  {kind:<18} n={v['n']:<3} adaptive={v['adaptive_hit']:.2f} [{fixed}] chose={v['adaptive_choice']} task={v['task_type']}")


if __name__ == "__main__":
    main()
