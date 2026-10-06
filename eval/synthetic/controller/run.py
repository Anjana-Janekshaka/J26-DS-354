"""Controller evaluation: strategy-selection macro-F1 against an objective oracle, and the
downstream evidence-hit delta of adaptive vs every fixed strategy.

    python -m eval.synthetic.controller.run [--budget 400] [--judge]

Oracle (source 1, objective): at each probe all four strategies' contexts are assembled from the
same module outputs; a strategy "hits" when its context satisfies the probe's evidence requirement
(required strings present, stale strings absent or marked). The oracle label is the cheapest
hitting strategy (``eval.metrics.oracle_label``: 10%-of-budget token buckets, then simplest first); probes no strategy can answer are excluded from F1 (counted in
hit rates). "Acceptable accuracy" counts a choice as correct when it is any hitting strategy.
Source 2 (LLM judge) runs only with --judge and configured Claude credentials; otherwise it is
reported as not run - labels are never fabricated.
"""

from __future__ import annotations

import argparse
import json
import warnings
from collections import Counter, defaultdict
from pathlib import Path

from contracts import ControllerDecision, OverrideInfo
from contracts.text import CachingEmbedder
from eval.metrics import macro_f1, oracle_label, required_hit
from integration import MemoryPipeline, assemble_prompt
from integration.llm_client import describe, get_llm
from retrieval import CrossEncoderNLI, SentenceTransformerEmbedder

from .generate import generate

HERE = Path(__file__).parent
STRATEGIES = ["sliding_window", "summarization", "rag", "hybrid"]
PREFERENCE = {s: i for i, s in enumerate(STRATEGIES)}

JUDGE_SYSTEM = (
    "You are grading memory contexts for an assistant. Given a user message and four candidate contexts "
    "labelled A-D, answer with the single letter of the context that best lets the assistant respond "
    "correctly with current (not stale) information, preferring the shorter context when equally good."
)


def forced(sig_turn: str, s: str) -> ControllerDecision:
    return ControllerDecision(turn_id=sig_turn, selected_strategy=s, rationale=f"forced {s}", controller_variant="rule_based",
                              decision_latency_ms=0.0, override=OverrideInfo(applied=False, by=None))


def run_conversation(conv, budget, emb, nli, judge) -> list[dict]:
    pipe = MemoryPipeline(conv["id"], token_budget=budget, embedder=emb, nli=nli)
    probes_at = defaultdict(list)
    for p in conv["probes"]:
        probes_at[p["after_index"]].append(p)
    rows = []
    for i, m in enumerate(conv["messages"]):
        if m["role"] == "user":
            pipe.user_turn(m["content"], respond=False)
        else:
            pipe.assistant_turn(m["content"])
        for p in probes_at.get(i, []):
            r = pipe.user_turn(p["question"], remember=False, respond=False)
            budget_now = r.signal.token_usage.budget
            ctxs = {s: assemble_prompt(forced(r.signal.turn_id, s), r.outputs, p["question"], budget_now) for s in STRATEGIES}
            hits = {s: required_hit(c.context, p["required"], p["stale"]) for s, c in ctxs.items()}
            ok = [s for s in STRATEGIES if hits[s]]
            oracle = oracle_label(hits, {s: ctxs[s].token_count for s in STRATEGIES}, budget_now)
            row = {
                "conv": conv["id"],
                "kind": p["kind"],
                "pressure": r.feature_vector.token_budget_pressure,
                "task_type": r.feature_vector.task_type,
                "adaptive": r.decision.selected_strategy,
                "adaptive_hit": required_hit(r.prompt.context, p["required"], p["stale"]),
                "hits": hits,
                "acceptable": ok,
                "oracle": oracle,
                "rationale": r.decision.rationale,
            }
            if judge is not None:
                letters = "ABCD"
                body = f"User message: {p['question']}\n\n" + "\n\n".join(
                    f"[{letters[k]}]\n{ctxs[s].context}" for k, s in enumerate(STRATEGIES))
                try:
                    ans = judge(JUDGE_SYSTEM, body).strip().upper()[:1]
                    row["judge"] = STRATEGIES[letters.index(ans)] if ans in letters else None
                except Exception as e:  # pragma: no cover - network
                    row["judge"] = None
                    row["judge_error"] = str(e)
            rows.append(row)
    pipe.close()
    return rows


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=400)
    ap.add_argument("--judge", action="store_true", help="also collect LLM-judge labels (needs Claude credentials)")
    ap.add_argument("--out", default=str(HERE / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    convs = generate()
    emb = CachingEmbedder(SentenceTransformerEmbedder())
    nli = CrossEncoderNLI()
    judge = get_llm(out / "judge_cache.jsonl", role="judge") if args.judge else None
    rows = [r for c in convs for r in run_conversation(c, args.budget, emb, nli, judge)]

    labeled = [r for r in rows if r["oracle"] != "none"]
    f1, per = macro_f1([r["oracle"] for r in labeled], [r["adaptive"] for r in labeled], STRATEGIES)
    acceptable = sum(r["adaptive"] in r["acceptable"] for r in labeled) / len(labeled)
    hit_rates = {s: sum(r["hits"][s] for r in rows) / len(rows) for s in STRATEGIES}
    adaptive_rate = sum(r["adaptive_hit"] for r in rows) / len(rows)
    singles = ("sliding_window", "summarization", "rag")  # the fixed baselines of build guide 6.1
    best_fixed = max(singles, key=hit_rates.get)
    by_kind = {}
    for kind in sorted({r["kind"] for r in rows}):
        rs = [r for r in rows if r["kind"] == kind]
        by_kind[kind] = {
            "n": len(rs),
            "adaptive_choice": dict(Counter(r["adaptive"] for r in rs)),
            "oracle": dict(Counter(r["oracle"] for r in rs)),
            "adaptive_hit": sum(r["adaptive_hit"] for r in rs) / len(rs),
            **{f"{s}_hit": sum(r["hits"][s] for r in rs) / len(rs) for s in STRATEGIES},
        }
    judge_report: dict = {"status": "not run (pass --judge with Claude credentials configured)"}
    if args.judge and judge is None:
        judge_report = {"status": "not run: no LLM configured (CEAI_LLM_BASE_URL + CEAI_LLM_MODEL, or Claude credentials)"}
    elif judge is not None:
        pairs = [(r["oracle"], r["judge"]) for r in labeled if r.get("judge")]
        judge_report = {"status": "run", "judge_model": describe(judge), "n": len(pairs), "agreement": sum(a == b for a, b in pairs) / max(1, len(pairs)),
                        "cohen_kappa": cohen_kappa([a for a, _ in pairs], [b for _, b in pairs])}

    summary = {
        "n_probes": len(rows),
        "n_with_oracle_label": len(labeled),
        "oracle_label_distribution": dict(Counter(r["oracle"] for r in rows)),
        "strategy_selection_macro_f1": f1,
        "per_class": per,
        "acceptable_choice_accuracy": acceptable,
        "evidence_hit_rate": {"adaptive": adaptive_rate, **hit_rates},
        "best_fixed_baseline": best_fixed,
        "adaptive_minus_best_fixed": adaptive_rate - hit_rates[best_fixed],
        "adaptive_minus_always_hybrid": adaptive_rate - hit_rates["hybrid"],
        "by_probe_kind": by_kind,
        "llm_judge_oracle": judge_report,
        "budget_tokens": args.budget,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "probes.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    print(f"{len(rows)} probes over {len(convs)} conversations (budget {args.budget}); oracle labels: {summary['oracle_label_distribution']}\n")
    print(f"strategy-selection macro-F1 vs objective oracle: {f1:.3f}   acceptable-choice accuracy: {acceptable:.3f}")
    print("evidence hit rate: " + "  ".join(f"{k}={v:.3f}" for k, v in summary["evidence_hit_rate"].items()))
    print(f"adaptive - best single fixed paradigm ({best_fixed}): {summary['adaptive_minus_best_fixed']:+.3f}; "
          f"adaptive - always-hybrid: {summary['adaptive_minus_always_hybrid']:+.3f}\n")
    for kind, v in by_kind.items():
        fixed = "  ".join(f"{s}={v[f'{s}_hit']:.2f}" for s in STRATEGIES)
        print(f"  {kind:<16} n={v['n']:<3} adaptive_hit={v['adaptive_hit']:.2f}  [{fixed}]  chose={v['adaptive_choice']}  oracle={v['oracle']}")
    print(f"\nLLM-judge oracle: {judge_report['status']}")
    print(f"written: {out / 'summary.json'}")


if __name__ == "__main__":
    main()
