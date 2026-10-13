"""LoCoMo harness (primary benchmark, build guide sec. 8).

    python -m eval.locomo.run [--budget 1024] [--conversations 10] [--no-nli] [--llm]

For every conversation the whole dialogue is ingested through the real pipeline, then every QA
question is asked as a non-committing probe. At each question the same module outputs yield the
context of every fixed strategy (sliding window, summarization, RAG, hybrid) and of the adaptive
controller. Reported per strategy and per LoCoMo category:

  * evidence hit rate  - every gold evidence turn has >= 60% of its content words in the context
  * evidence coverage  - mean content-word coverage of the gold evidence turns
  * answer-in-context  - all gold-answer tokens present in the context (categories 1-4)
  * tokens             - mean context size
  * QA token-F1        - only with --llm and a configured LLM (free OpenAI-compatible endpoint or Claude)
  * judge score        - only with --judge-answers: correct=1 / partial=0.5 / wrong=0 (eval/judge.py)

Granularity (RAG, Claim 1): NDCG@10 / recall@10 of turn-level vs segment-level vs adaptive chunking,
three separate indexes over the same embeddings (contradiction checking off for these three).
Controller (Claim headline): macro-F1 of the adaptive choice vs the objective oracle (cheapest
strategy whose context hits the evidence), plus the adaptive-minus-best-fixed delta.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path

from contracts import ControllerDecision, OverrideInfo
from contracts.text import CachingEmbedder
from eval.metrics import answer_in_context, evidence_hit, macro_f1, ndcg_at_k, oracle_label, token_f1
from integration import MemoryPipeline, assemble_prompt
from eval.frozen import frozen_controller
from eval.judge import GRADES, grade
from concurrent.futures import ThreadPoolExecutor

from integration.llm_client import concurrency, describe, get_llm, stats as llm_stats
from retrieval.rerank import DEFAULT_RERANKER
from retrieval import CrossEncoderNLI, RetrievalConfig, RetrievalEngine, SentenceTransformerEmbedder

from .loader import CATEGORY_NAMES, load

HERE = Path(__file__).parent
STRATEGIES = ["sliding_window", "summarization", "rag", "hybrid"]
PREFERENCE = {s: i for i, s in enumerate(STRATEGIES)}
QA_SYSTEM = (
    "Answer the question using only the memory context. Each memory line starts with the date of that "
    "conversation session in [brackets]; resolve relative times ('yesterday', 'last week', 'next month') "
    "against that date and answer with an absolute date. Reply with a short phrase, no explanation."
)


def forced(tid: str, s: str) -> ControllerDecision:
    return ControllerDecision(turn_id=tid, selected_strategy=s, rationale=f"forced {s}", controller_variant="rule_based",
                              decision_latency_ms=0.0, override=OverrideInfo(applied=False, by=None))


def run_conversation(conv, args, emb, nli, llm, judge=None) -> tuple[list[dict], dict]:
    t0 = time.time()
    pipe = MemoryPipeline(conv.sample_id, token_budget=args.budget, embedder=emb, nli=nli,
                          controller=None if args.default_rules else frozen_controller(),
                          llm=llm if args.llm_summaries else None, summarize_with_llm=args.llm_summaries,
                          retrieval_config=RetrievalConfig(check_contradictions=nli is not None,
                                                           compact_headers=not args.full_headers,
                                                           reranker=args.reranker, neighbors=args.neighbors))
    gran = {m: RetrievalEngine(emb, None, RetrievalConfig(mode=m, check_contradictions=False)) for m in ("turn", "segment", "adaptive")}
    dia_to_tid: dict[str, str] = {}
    text_of: dict[str, str] = {}
    for t in conv.turns:
        turn = pipe.add_turn("user", t.text, speaker=t.speaker, metadata={"date": t.date, "dia_id": t.dia_id})
        dia_to_tid[t.dia_id] = turn.turn_id
        text_of[t.dia_id] = t.text
        for eng in gran.values():
            eng.ingest(turn)
    ingest_s = time.time() - t0

    rows = []
    questions = conv.qa
    if args.max_questions and args.max_questions < len(questions):
        # Seeded random sample, kept in original order. LoCoMo lists questions grouped by category,
        # so taking the first N would over-sample some categories and skip others entirely.
        rng = random.Random(f"{args.sample_seed}:{conv.sample_id}")
        keep = set(rng.sample(range(len(questions)), args.max_questions))
        questions = [q for i, q in enumerate(questions) if i in keep]
    for q in questions:
        ev_texts = [text_of[e] for e in q.evidence if e in text_of]
        r = pipe.user_turn(q.question, remember=False, respond=False)
        budget = r.signal.token_usage.budget
        ctx = {s: assemble_prompt(forced(r.signal.turn_id, s), r.outputs, q.question, budget) for s in STRATEGIES}
        ctx["adaptive"] = r.prompt
        row = {"conv": conv.sample_id, "category": q.category, "adaptive_choice": r.decision.selected_strategy,
               "task_type": r.feature_vector.task_type, "n_evidence": len(ev_texts)}
        for s, p in ctx.items():
            cov, hit = evidence_hit(ev_texts, p.context)
            row[s] = {"coverage": cov, "hit": hit, "tokens": p.token_count,
                      "answer_in_context": answer_in_context(q.answer, p.context) if q.answer is not None and q.category != 5 else None}
        ok = [s for s in STRATEGIES if row[s]["hit"]] if ev_texts else []
        row["acceptable"] = ok
        row["oracle"] = oracle_label({s: s in ok for s in STRATEGIES}, {s: row[s]["tokens"] for s in STRATEGIES}, budget)

        ev_tids = {dia_to_tid[e] for e in q.evidence if e in dia_to_tid}
        for mode, eng in gran.items():
            ranked = eng.search(q.question, 10)
            rel = [1.0 if ev_tids & set(c.turn_ids) else 0.0 for c, _ in ranked]
            possible = sum(1 for c in eng.chunks.values() if c.active and ev_tids & set(c.turn_ids))
            covered = set().union(*[set(c.turn_ids) for c, _ in ranked]) if ranked else set()
            # Equal-cost comparison: walk the ranking until a fixed word budget is spent.
            wb_cov: set[str] = set()
            words = 0
            for c, _ in eng.search(q.question, 60):
                n = len(c.text.split())
                if words + n > args.word_budget:
                    continue
                wb_cov |= set(c.turn_ids)
                words += n
            row[f"gran_{mode}"] = {
                "ndcg@10": ndcg_at_k(rel, possible, 10) if ev_tids else None,
                "recall@10": len(ev_tids & covered) / len(ev_tids) if ev_tids else None,
                "tokens@10": sum(len(c.text.split()) for c, _ in ranked),
                "recall@word_budget": len(ev_tids & wb_cov) / len(ev_tids) if ev_tids else None,
            }
        if args.llm and llm is not None and q.answer is not None and q.category != 5:
            row["question"], row["gold_answer"] = q.question, str(q.answer)
            names = ("adaptive", "rag", "sliding_window", "summarization", "hybrid")
            # Identical contexts (adaptive always equals one fixed strategy) are answered once, and the
            # distinct calls go out in parallel (the server batches them).
            unique_ctx = list(dict.fromkeys(ctx[s].context for s in names))
            with ThreadPoolExecutor(concurrency()) as pool:
                answers = dict(zip(unique_ctx, pool.map(
                    lambda c: llm(QA_SYSTEM, f"[Memory context]\n{c}\n\nQuestion: {q.question}"), unique_ctx)))
                grades: dict[str, str | None] = {}
                if judge is not None:
                    preds = list(dict.fromkeys(answers.values()))
                    grades = dict(zip(preds, pool.map(lambda a: grade(judge, q.question, str(q.answer), a), preds)))
            for s in names:
                pred = answers[ctx[s].context]
                row[s]["answer"] = pred
                row[s]["qa_f1"] = token_f1(pred, str(q.answer))
                if judge is not None:
                    g = grades[pred]
                    row[s]["judge_grade"] = g
                    row[s]["judge_score"] = GRADES.get(g) if g else None
        rows.append(row)
    stats = {"conv": conv.sample_id, "turns": len(conv.turns), "questions": len(conv.qa), "ingest_s": ingest_s,
             "total_s": time.time() - t0, "nli_pairs": getattr(nli, "calls", 0),
             "llm": llm_stats(llm) if llm is not None else None, "judge": llm_stats(judge) if judge is not None else None,
             "chunk_granularity_adaptive": dict(Counter(c.granularity for c in gran["adaptive"].chunks.values() if c.active))}
    pipe.close()
    return rows, stats


def aggregate(rows: list[dict]) -> dict:
    def mean(xs):
        xs = [x for x in xs if x is not None]
        return statistics.mean(xs) if xs else None

    names = STRATEGIES + ["adaptive"]
    out: dict = {"n_questions": len(rows)}
    per = {}
    for s in names:
        per[s] = {
            "evidence_hit_rate": mean([float(r[s]["hit"]) for r in rows if r["n_evidence"]]),
            "evidence_coverage": mean([r[s]["coverage"] for r in rows if r["n_evidence"]]),
            "answer_in_context": mean([None if r[s]["answer_in_context"] is None else float(r[s]["answer_in_context"]) for r in rows]),
            "mean_tokens": mean([r[s]["tokens"] for r in rows]),
            "qa_f1": mean([r[s].get("qa_f1") for r in rows]),
            "judge_score": mean([r[s].get("judge_score") for r in rows]),
        }
    out["strategies"] = per
    fixed = {s: per[s]["evidence_hit_rate"] for s in STRATEGIES}
    best = max(("sliding_window", "summarization", "rag"), key=fixed.get)  # single-paradigm baselines (6.1)
    out["best_fixed_baseline"] = best
    out["adaptive_minus_best_fixed_hit_rate"] = per["adaptive"]["evidence_hit_rate"] - fixed[best]
    out["adaptive_minus_always_hybrid_hit_rate"] = per["adaptive"]["evidence_hit_rate"] - fixed["hybrid"]
    by_cat = {}
    for cat in sorted({r["category"] for r in rows}):
        rs = [r for r in rows if r["category"] == cat and r["n_evidence"]]
        by_cat[CATEGORY_NAMES[cat]] = {s: mean([float(r[s]["hit"]) for r in rs]) for s in names} | {"n": len(rs)}
    out["evidence_hit_rate_by_category"] = by_cat
    labeled = [r for r in rows if r["oracle"] != "none"]
    f1, per_class = macro_f1([r["oracle"] for r in labeled], [r["adaptive_choice"] for r in labeled], STRATEGIES)
    out["controller"] = {
        "macro_f1_vs_objective_oracle": f1,
        "per_class": per_class,
        "acceptable_choice_accuracy": mean([float(r["adaptive_choice"] in r["acceptable"]) for r in labeled]),
        "oracle_distribution": dict(Counter(r["oracle"] for r in rows)),
        "choice_distribution": dict(Counter(r["adaptive_choice"] for r in rows)),
        "task_type_distribution": dict(Counter(r["task_type"] for r in rows)),
    }
    out["granularity"] = {
        m: {k: mean([r[f"gran_{m}"][k] for r in rows]) for k in ("ndcg@10", "recall@10", "tokens@10", "recall@word_budget")}
        for m in ("turn", "segment", "adaptive")
    }
    return out


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=1024)
    ap.add_argument("--conversations", type=int, default=10)
    ap.add_argument("--split", choices=["dev", "test", "all"], default="all",
                    help="dev = conversations 1,3,5,7,9 (even index), test = 2,4,6,8,10; tune on dev only")
    ap.add_argument("--reranker", default=DEFAULT_RERANKER, help="cross-encoder that reranks RAG candidates (selected on the dev split)")
    ap.add_argument("--no-reranker", dest="reranker", action="store_const", const=None, help="plain FAISS ranking (ablation)")
    ap.add_argument("--neighbors", type=int, default=0, help="adjacent turns added around each retrieved RAG turn")
    ap.add_argument("--full-headers", action="store_true", help="old verbose RAG chunk headers (ablation)")
    ap.add_argument("--default-rules", action="store_true", help="RuleConfig() defaults instead of the frozen controller config")
    ap.add_argument("--word-budget", type=int, default=400, help="equal-cost budget (words) for the granularity comparison")
    ap.add_argument("--no-nli", action="store_true", help="skip the NLI contradiction stage (much faster on CPU)")
    ap.add_argument("--llm", action="store_true", help="also answer questions with the configured LLM and score token-F1")
    ap.add_argument("--judge-answers", action="store_true", help="grade LLM answers with the judge model (correct/partial/wrong)")
    ap.add_argument("--max-questions", type=int, default=None, help="random sample of N questions per conversation")
    ap.add_argument("--sample-seed", type=int, default=0, help="seed for --max-questions sampling")
    ap.add_argument("--llm-summaries", action="store_true", help="build L1/L2/L3 with the configured LLM instead of the rule-based generator")
    ap.add_argument("--out", default=str(HERE / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    convs = load()[: args.conversations]
    if args.split != "all":
        convs = [c for i, c in enumerate(convs) if i % 2 == (0 if args.split == "dev" else 1)]
    emb = CachingEmbedder(SentenceTransformerEmbedder())
    nli = None if args.no_nli else CrossEncoderNLI()
    llm = get_llm(out / "llm_cache.jsonl") if (args.llm or args.llm_summaries) else None
    judge = get_llm(out / "judge_cache.jsonl", role="judge") if args.judge_answers else None
    if args.judge_answers and (judge is None or not args.llm):
        raise SystemExit("--judge-answers needs --llm and a configured judge (CEAI_JUDGE_MODEL or CEAI_LLM_MODEL)")
    if (args.llm or args.llm_summaries) and llm is None:
        raise SystemExit("--llm/--llm-summaries need CEAI_LLM_BASE_URL + CEAI_LLM_MODEL (free endpoint) or Claude credentials")
    all_rows, all_stats = [], []
    for conv in convs:
        rows, stats = run_conversation(conv, args, emb, nli, llm, judge)
        all_rows += rows
        all_stats.append(stats)
        print(f"{conv.sample_id}: {stats['turns']} turns, {stats['questions']} questions, {stats['total_s']:.0f}s"
              + (f", LLM {stats['llm']['calls']} calls @ {stats['llm']['s_per_call']} s/call" if stats.get('llm') and stats['llm']['calls'] else ""), flush=True)
        with open(out / "questions.jsonl", "a" if len(all_stats) > 1 else "w", encoding="utf-8") as f:
            f.write("\n".join(json.dumps(r) for r in rows) + "\n")

    summary = aggregate(all_rows)
    summary["config"] = {"budget": args.budget, "conversations": len(convs), "nli": nli is not None, "split": args.split,
                         "rag": {"compact_headers": not args.full_headers, "reranker": args.reranker, "neighbors": args.neighbors},
                         "qa_llm": f"run with {describe(llm)}" if (llm is not None and args.llm) else "not run (pass --llm with an LLM configured)",
                         "summary_generator": f"llm ({describe(llm)})" if args.llm_summaries else "rule_based",
                         "answer_judge": describe(judge) if judge is not None else "not run",
                         "max_questions_per_conversation": args.max_questions}
    summary["runs"] = all_stats
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nLoCoMo: {summary['n_questions']} questions, {len(convs)} conversations, budget {args.budget} tokens, NLI {'on' if nli else 'off'}\n")
    print(f"{'strategy':<16}{'ev_hit':>8}{'ev_cov':>8}{'ans_in_ctx':>11}{'tokens':>8}")
    for s, v in summary["strategies"].items():
        print(f"{s:<16}{v['evidence_hit_rate']:>8.3f}{v['evidence_coverage']:>8.3f}{v['answer_in_context']:>11.3f}{v['mean_tokens']:>8.0f}")
    print(f"\nadaptive - best single fixed paradigm ({summary['best_fixed_baseline']}): "
          f"{summary['adaptive_minus_best_fixed_hit_rate']:+.3f} evidence hit rate; "
          f"adaptive - always-hybrid: {summary['adaptive_minus_always_hybrid_hit_rate']:+.3f}")
    c = summary["controller"]
    print(f"controller macro-F1 vs objective oracle: {c['macro_f1_vs_objective_oracle']:.3f}; acceptable-choice acc {c['acceptable_choice_accuracy']:.3f}")
    print(f"   choices {c['choice_distribution']}  oracle {c['oracle_distribution']}")
    print("\nby category (evidence hit rate):")
    for cat, v in summary["evidence_hit_rate_by_category"].items():
        print(f"   {cat:<12} n={v['n']:<4} " + "  ".join(f"{s}={v[s]:.2f}" for s in STRATEGIES + ['adaptive']))
    print(f"\nRAG granularity (NDCG@10 / recall@10 / words@10 / recall@{args.word_budget} words):")
    for m, v in summary["granularity"].items():
        print(f"   {m:<9} {v['ndcg@10']:.3f} / {v['recall@10']:.3f} / {v['tokens@10']:.0f} / {v['recall@word_budget']:.3f}")
    print(f"\nQA: {summary['config']['qa_llm']}; judge: {summary['config']['answer_judge']}")
    if args.llm:
        for k, v in summary["strategies"].items():
            if v.get("qa_f1") is not None:
                judged = f"  judge={v['judge_score']:.3f}" if v.get("judge_score") is not None else ""
                print(f"   {k:<16} token-F1={v['qa_f1']:.3f}{judged}")
    print(f"written: {out / 'summary.json'}")


if __name__ == "__main__":
    main()
