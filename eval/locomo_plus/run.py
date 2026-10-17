"""LoCoMo-Plus harness (supplementary, build guide sec. 8) - deterministic, no LLM judge.

    python -m eval.locomo_plus.run [--budget 1024] [--limit 401]

For each item the stitched conversation (LoCoMo + inserted cue dialogue) is ingested through the
real pipeline and the trigger is asked as a non-committing probe. Because the cue *is* the gold
evidence and its position is known, we score whether it reached each strategy's context:

  * cue hit     - every cue line has >= 60% of its content words in the context
  * cue any     - at least one cue line does

reported per strategy (+ the naive summarizer baseline), per relation type and per cue-to-trigger
distance. Oracle labels for the controller come from our own objective protocol
(``eval.metrics.oracle_label``), never from LoCoMo-Plus itself. Judging whether a model's *reply*
honours the constraint needs an LLM judge and is not part of this script.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import warnings
from collections import Counter
from pathlib import Path

from contracts import ControllerDecision, OverrideInfo, TokenUsage, TurnSignal, utcnow
from contracts.text import CachingEmbedder
from eval.frozen import frozen_controller, llm_policy, system_name, system_retrieval
from eval.metrics import evidence_coverage, macro_f1, oracle_label
from integration import MemoryPipeline, assemble_prompt
from retrieval import RetrievalConfig, SentenceTransformerEmbedder
from retrieval.rerank import DEFAULT_RERANKER
from summarization import NaiveSummarizer

from .loader import load, split

HERE = Path(__file__).parent
STRATEGIES = ["sliding_window", "summarization", "rag", "hybrid"]


def forced(tid: str, s: str) -> ControllerDecision:
    return ControllerDecision(turn_id=tid, selected_strategy=s, rationale=f"forced {s}", controller_variant="rule_based",
                              decision_latency_ms=0.0, override=OverrideInfo(applied=False, by=None))


def score(cues: list[str], context: str) -> dict:
    covs = [evidence_coverage(c, context) for c in cues]
    return {"cue_hit": all(c >= 0.6 for c in covs), "cue_any": any(c >= 0.6 for c in covs), "coverage": sum(covs) / len(covs)}


def bucket(distance: int) -> str:
    return "<50 turns" if distance < 50 else "50-200 turns" if distance <= 200 else ">200 turns"


def run_item(item, budget: int, emb, warmup: int = 0, overrides: dict | None = None, reranker: str | None = DEFAULT_RERANKER,
             llm=None) -> dict:
    t0 = time.time()
    pipe = MemoryPipeline(f"plus-{item.item_id}", token_budget=budget, embedder=emb, nli=None, llm=llm,
                          llm_policy="assisted" if llm is not None else "strict",
                          retrieval_config=RetrievalConfig(**system_retrieval(check_contradictions=False, reranker=reranker)),
                          controller=frozen_controller(**(overrides or {})))
    naive = NaiveSummarizer(tail_keep=4)
    cue_index = None
    n = len(item.turns)
    for i, t in enumerate(item.turns):
        meta = {"date": t.date}
        if i >= n - warmup:
            # In deployment every user message is a decision turn; replaying the last ``warmup``
            # turns that way gives the controller its normal decision history and escalations.
            turn = pipe.user_turn(t.text, respond=False, speaker=t.speaker, metadata=meta).turn
        else:
            turn = pipe.add_turn("user", t.text, speaker=t.speaker, metadata=meta)
        naive.ingest(turn)
        if t.kind == "cue":
            cue_index = i
    trig = item.trigger
    r = pipe.user_turn(trig.text, remember=False, respond=False, speaker=trig.speaker, metadata={"date": trig.date})
    b = r.signal.token_usage.budget
    ctx = {s: assemble_prompt(forced(r.signal.turn_id, s), r.outputs, trig.text, b) for s in STRATEGIES}
    row = {
        "item": item.item_id,
        "relation_type": item.relation_type,
        "distance": bucket(len(item.turns) - 1 - cue_index),
        "task_type": r.feature_vector.task_type,
        "shift": r.signal.shift_detected,
        "adaptive_choice": r.decision.selected_strategy,
    }
    for s, p in ctx.items():
        row[s] = {**score(item.cue_texts, p.context), "tokens": p.token_count}
    row["adaptive"] = {**score(item.cue_texts, r.prompt.context), "tokens": r.prompt.token_count}
    sig = TurnSignal(turn_id=r.signal.turn_id, conversation_id="naive", turn_count=r.signal.turn_count, task_type="chat",
                     token_usage=TokenUsage(used=r.signal.token_usage.used, budget=b), conversation_state="x", timestamp=utcnow())
    nout = naive.build_context(sig, trig.text)
    row["naive_summary"] = {**score(item.cue_texts, nout.context_text()), "tokens": nout.token_count}
    row["oracle"] = oracle_label({s: row[s]["cue_hit"] for s in STRATEGIES}, {s: row[s]["tokens"] for s in STRATEGIES}, b)
    gen = pipe.modules["summarization"].generator
    row["llm_calls"], row["llm_fallbacks"] = getattr(gen, "llm_calls", 0), getattr(gen, "failures", 0)
    row["seconds"] = time.time() - t0
    pipe.close()
    return row


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=1024)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--split", choices=["dev", "test", "all"], default="all", help="even item ids = dev, odd = test")
    ap.add_argument("--warmup-turns", type=int, default=0, help="replay the last N history turns as decision turns")
    ap.add_argument("--reranker", default=DEFAULT_RERANKER)
    ap.add_argument("--no-reranker", dest="reranker", action="store_const", const=None)
    ap.add_argument("--long-chat", choices=["summarization", "hybrid", "rag"], default=None, help="override RuleConfig.long_chat_strategy")
    ap.add_argument("--loss-target", choices=["rag", "hybrid"], default=None, help="override RuleConfig.loss_escalation_target")
    ap.add_argument("--qa-strategy", choices=["rag", "hybrid", "hybrid_unless_shift"], default=None, help="override RuleConfig.qa_strategy")
    ap.add_argument("--sample", type=int, default=None, help="seeded random subset of the split (llm_policy runs)")
    ap.add_argument("--sample-seed", type=int, default=2310)
    ap.add_argument("--out", default=str(HERE / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    items = split(load(args.limit), args.split)
    if args.sample and args.sample < len(items):
        import random

        keep = set(random.Random(args.sample_seed).sample(range(len(items)), args.sample))
        items = [it for i, it in enumerate(items) if i in keep]
    llm = None
    if llm_policy() == "assisted":
        from integration.llm_client import get_llm

        llm = get_llm(out / "llm_cache.jsonl", role="summary")
        if llm is None:
            raise SystemExit("CEAI_LLM_POLICY=assisted needs an LLM (CEAI_LLM_BASE_URL + CEAI_LLM_MODEL)")
    overrides = {k: v for k, v in (("long_chat_strategy", args.long_chat), ("loss_escalation_target", args.loss_target), ("qa_strategy", args.qa_strategy)) if v}
    emb = CachingEmbedder(SentenceTransformerEmbedder())
    rows = []
    t0 = time.time()
    with open(out / "items.jsonl", "w", encoding="utf-8") as f:
        for n, item in enumerate(items, 1):
            row = run_item(item, args.budget, emb, args.warmup_turns, overrides, args.reranker, llm)
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            if n % 25 == 0:
                print(f"{n}/{len(items)} items, {time.time() - t0:.0f}s", flush=True)

    names = STRATEGIES + ["adaptive", "naive_summary"]

    def rate(rs, s, key="cue_hit"):
        return sum(r[s][key] for r in rs) / len(rs) if rs else None

    summary: dict = {
        "n_items": len(rows),
        "system": system_name(),
        "llm_policy": llm_policy(),
        "sample": args.sample, "sample_seed": args.sample_seed if args.sample else None,
        "llm_calls_per_item": statistics.mean(r["llm_calls"] for r in rows),
        "llm_fallbacks": sum(r["llm_fallbacks"] for r in rows),
        "seconds_per_item": statistics.mean(r["seconds"] for r in rows),
        "split": args.split,
        "warmup_turns": args.warmup_turns,
        "reranker": args.reranker,
        "rule_overrides": overrides,
        "budget_tokens": args.budget,
        "strategies": {s: {"cue_hit_rate": rate(rows, s), "cue_any_rate": rate(rows, s, "cue_any"),
                           "mean_coverage": statistics.mean(r[s]["coverage"] for r in rows),
                           "mean_tokens": statistics.mean(r[s]["tokens"] for r in rows)} for s in names},
        "by_relation_type": {k: {s: rate([r for r in rows if r["relation_type"] == k], s) for s in names} | {"n": sum(r["relation_type"] == k for r in rows)}
                             for k in sorted({r["relation_type"] for r in rows})},
        "by_cue_distance": {k: {s: rate([r for r in rows if r["distance"] == k], s) for s in names} | {"n": sum(r["distance"] == k for r in rows)}
                            for k in ("<50 turns", "50-200 turns", ">200 turns")},
        "controller": {
            "choice_distribution": dict(Counter(r["adaptive_choice"] for r in rows)),
            "task_type_distribution": dict(Counter(r["task_type"] for r in rows)),
            "oracle_distribution": dict(Counter(r["oracle"] for r in rows)),
        },
        "llm_judge": "not run (deterministic cue-in-context scoring only)",
    }
    labeled = [r for r in rows if r["oracle"] != "none"]
    if labeled:
        f1, _ = macro_f1([r["oracle"] for r in labeled], [r["adaptive_choice"] for r in labeled], STRATEGIES)
        summary["controller"]["macro_f1_vs_objective_oracle"] = f1
    singles = ("sliding_window", "summarization", "rag")
    best = max(singles, key=lambda s: summary["strategies"][s]["cue_hit_rate"])
    summary["best_fixed_baseline"] = best
    summary["adaptive_minus_best_fixed"] = summary["strategies"]["adaptive"]["cue_hit_rate"] - summary["strategies"][best]["cue_hit_rate"]
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nLoCoMo-Plus: {len(rows)} items, budget {args.budget} tokens (deterministic cue-in-context, no LLM)\n")
    print(f"{'strategy':<16}{'cue_hit':>9}{'cue_any':>9}{'coverage':>10}{'tokens':>8}")
    for s in names:
        v = summary["strategies"][s]
        print(f"{s:<16}{v['cue_hit_rate']:>9.3f}{v['cue_any_rate']:>9.3f}{v['mean_coverage']:>10.3f}{v['mean_tokens']:>8.0f}")
    print(f"\nadaptive - best single fixed ({best}): {summary['adaptive_minus_best_fixed']:+.3f}")
    c = summary["controller"]
    print(f"controller choices {c['choice_distribution']}  task types {c['task_type_distribution']}")
    print(f"oracle {c['oracle_distribution']}  macro-F1 {c.get('macro_f1_vs_objective_oracle', float('nan')):.3f}")
    for title, key in (("relation type", "by_relation_type"), ("cue distance", "by_cue_distance")):
        print(f"\nby {title} (cue hit rate):")
        for k, v in summary[key].items():
            print(f"   {k:<14} n={v['n']:<4} " + "  ".join(f"{s}={v[s]:.2f}" for s in names if v[s] is not None))
    print(f"\nwritten: {out / 'summary.json'}")


if __name__ == "__main__":
    main()
