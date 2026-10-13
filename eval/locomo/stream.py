"""Mixed-workload ("in-stream") LoCoMo: questions are asked *during* the conversation.

    python -m eval.locomo.stream [--split dev|test|all] [--budget 1024] [--decision-turns 2]

Plain LoCoMo asks every question after the whole conversation, so the right memory strategy is
always retrieval and an adaptive controller can at best tie it. Real assistants are asked things
at every point of a conversation. Here each question (with evidence) is assigned, by a seeded coin
flip, to one of two positions:

  * fresh - right after the session that contains its latest evidence (recent context matters)
  * late  - after the final session (long-range recall)

Sessions are ingested in order; the last ``--decision-turns`` turns of each session run as real
decision turns (so the controller has its normal history and escalations) and the questions due
at that point are asked as non-committing probes. Scoring is the same deterministic evidence-hit
metric as ``eval.locomo.run``, per strategy and for the adaptive controller, plus context tokens.
Nothing here was tuned on these numbers; use ``--split dev`` while developing.
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
from eval.metrics import evidence_hit, macro_f1, oracle_label
from controller import RuleConfig
from integration import MemoryPipeline, assemble_prompt
from retrieval.rerank import DEFAULT_RERANKER
from retrieval import RetrievalConfig, SentenceTransformerEmbedder

from .loader import CATEGORY_NAMES, load

HERE = Path(__file__).parent
STRATEGIES = ["sliding_window", "summarization", "rag", "hybrid"]
SINGLES = ("sliding_window", "summarization", "rag")


def forced(tid: str, s: str) -> ControllerDecision:
    return ControllerDecision(turn_id=tid, selected_strategy=s, rationale=f"forced {s}", controller_variant="rule_based",
                              decision_latency_ms=0.0, override=OverrideInfo(applied=False, by=None))


def _session_of(dia_id: str) -> int | None:
    head = dia_id.split(":")[0]
    return int(head[1:]) if head.startswith("D") and head[1:].isdigit() else None


def schedule(conv, seed: int) -> dict[int, list[tuple[str, object]]]:
    """session number -> [(position, question)] to ask right after that session."""
    last = max(t.session for t in conv.turns)
    rng = random.Random(f"{seed}:{conv.sample_id}")
    due: dict[int, list] = defaultdict(list)
    for q in conv.qa:
        sessions = [s for s in (_session_of(e) for e in q.evidence) if s is not None]
        if not sessions:
            continue
        latest = max(sessions)
        if rng.random() < 0.5 and latest < last:
            due[latest].append(("fresh", q))
        else:
            due[last].append(("late", q))
    return due


def rule_config(args) -> RuleConfig | None:
    overrides = {k: v for k, v in (("long_chat_strategy", args.long_chat), ("loss_escalation_target", args.loss_target), ("qa_strategy", args.qa_strategy)) if v}
    return RuleConfig(**overrides) if overrides else None


def run_conversation(conv, args, emb) -> list[dict]:
    pipe = MemoryPipeline(f"stream-{conv.sample_id}", token_budget=args.budget, embedder=emb, nli=None,
                          retrieval_config=RetrievalConfig(check_contradictions=False, compact_headers=not args.full_headers,
                                                           reranker=args.reranker, neighbors=args.neighbors),
                          rule_config=rule_config(args))
    due = schedule(conv, args.seed)
    text_of = {t.dia_id: t.text for t in conv.turns}
    by_session: dict[int, list] = defaultdict(list)
    for t in conv.turns:
        by_session[t.session].append(t)
    rows = []
    for s in sorted(by_session):
        turns = by_session[s]
        for i, t in enumerate(turns):
            meta = {"date": t.date, "dia_id": t.dia_id}
            if i >= len(turns) - args.decision_turns:
                pipe.user_turn(t.text, respond=False, speaker=t.speaker, metadata=meta)
            else:
                pipe.add_turn("user", t.text, speaker=t.speaker, metadata=meta)
        for position, q in due.get(s, []):
            ev = [text_of[e] for e in q.evidence if e in text_of]
            r = pipe.user_turn(q.question, remember=False, respond=False)
            b = r.signal.token_usage.budget
            ctx = {st: assemble_prompt(forced(r.signal.turn_id, st), r.outputs, q.question, b) for st in STRATEGIES}
            row = {"conv": conv.sample_id, "session": s, "position": position, "category": q.category,
                   "pressure": r.feature_vector.token_budget_pressure, "task_type": r.feature_vector.task_type,
                   "shift": r.signal.shift_detected,
                   "adaptive_choice": r.decision.selected_strategy}
            for st, p in list(ctx.items()) + [("adaptive", r.prompt)]:
                cov, hit = evidence_hit(ev, p.context)
                row[st] = {"hit": hit, "coverage": cov, "tokens": p.token_count}
            row["oracle"] = oracle_label({st: row[st]["hit"] for st in STRATEGIES}, {st: row[st]["tokens"] for st in STRATEGIES}, b)
            rows.append(row)
    pipe.close()
    return rows


def summarize(rows: list[dict]) -> dict:
    names = STRATEGIES + ["adaptive"]

    def rate(rs, s):
        return sum(r[s]["hit"] for r in rs) / len(rs) if rs else None

    out = {"n_questions": len(rows),
           "strategies": {s: {"evidence_hit_rate": rate(rows, s), "mean_tokens": statistics.mean(r[s]["tokens"] for r in rows)} for s in names},
           "by_position": {p: {s: rate([r for r in rows if r["position"] == p], s) for s in names} | {"n": sum(r["position"] == p for r in rows)}
                           for p in ("fresh", "late")},
           "by_category": {CATEGORY_NAMES[c]: {s: rate([r for r in rows if r["category"] == c], s) for s in names}
                           | {"n": sum(r["category"] == c for r in rows)} for c in sorted({r["category"] for r in rows})},
           "controller": {"choices": dict(Counter(r["adaptive_choice"] for r in rows)),
                          "choices_by_position": {p: dict(Counter(r["adaptive_choice"] for r in rows if r["position"] == p)) for p in ("fresh", "late")},
                          "oracle": dict(Counter(r["oracle"] for r in rows))}}
    labeled = [r for r in rows if r["oracle"] != "none"]
    if labeled:
        out["controller"]["macro_f1_vs_objective_oracle"] = macro_f1([r["oracle"] for r in labeled], [r["adaptive_choice"] for r in labeled], STRATEGIES)[0]
    best = max(SINGLES, key=lambda s: out["strategies"][s]["evidence_hit_rate"])
    out["best_single_fixed"] = best
    out["adaptive_minus_best_single"] = out["strategies"]["adaptive"]["evidence_hit_rate"] - out["strategies"][best]["evidence_hit_rate"]
    out["adaptive_minus_always_hybrid"] = out["strategies"]["adaptive"]["evidence_hit_rate"] - out["strategies"]["hybrid"]["evidence_hit_rate"]
    return out


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=1024)
    ap.add_argument("--split", choices=["dev", "test", "all"], default="all", help="same conversation split as eval.locomo.run")
    ap.add_argument("--conversations", type=int, default=10)
    ap.add_argument("--decision-turns", type=int, default=2, help="last N turns of each session run as decision turns")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--reranker", default=DEFAULT_RERANKER, help="cross-encoder that reranks RAG candidates (selected on the dev split)")
    ap.add_argument("--no-reranker", dest="reranker", action="store_const", const=None, help="plain FAISS ranking (ablation)")
    ap.add_argument("--neighbors", type=int, default=0)
    ap.add_argument("--full-headers", action="store_true")
    ap.add_argument("--long-chat", choices=["summarization", "hybrid", "rag"], default=None, help="override RuleConfig.long_chat_strategy")
    ap.add_argument("--loss-target", choices=["rag", "hybrid"], default=None, help="override RuleConfig.loss_escalation_target")
    ap.add_argument("--qa-strategy", choices=["rag", "hybrid", "hybrid_unless_shift"], default=None, help="override RuleConfig.qa_strategy")
    ap.add_argument("--out", default=str(HERE / "results_stream"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    convs = load()[: args.conversations]
    if args.split != "all":
        convs = [c for i, c in enumerate(convs) if i % 2 == (0 if args.split == "dev" else 1)]
    emb = CachingEmbedder(SentenceTransformerEmbedder())
    rows: list[dict] = []
    with open(out / "questions.jsonl", "w", encoding="utf-8") as f:
        for conv in convs:
            t0 = time.time()
            rs = run_conversation(conv, args, emb)
            rows += rs
            for r in rs:
                f.write(json.dumps(r) + "\n")
            print(f"{conv.sample_id}: {len(rs)} questions, {time.time() - t0:.0f}s", flush=True)

    summary = summarize(rows)
    summary["config"] = {k: v for k, v in vars(args).items() if k != "out"}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    names = STRATEGIES + ["adaptive"]
    print(f"\nIn-stream LoCoMo: {len(rows)} questions, {len(convs)} conversations, split {args.split}, budget {args.budget}\n")
    print(f"{'strategy':<16}{'hit':>7}{'fresh':>8}{'late':>8}{'tokens':>8}")
    for s in names:
        v = summary["strategies"][s]
        print(f"{s:<16}{v['evidence_hit_rate']:>7.3f}{summary['by_position']['fresh'][s]:>8.3f}{summary['by_position']['late'][s]:>8.3f}{v['mean_tokens']:>8.0f}")
    print(f"\nadaptive - best single fixed ({summary['best_single_fixed']}): {summary['adaptive_minus_best_single']:+.3f}; "
          f"adaptive - always-hybrid: {summary['adaptive_minus_always_hybrid']:+.3f}")
    c = summary["controller"]
    print(f"choices fresh={c['choices_by_position']['fresh']} late={c['choices_by_position']['late']}")
    print(f"oracle {c['oracle']}  macro-F1 {c.get('macro_f1_vs_objective_oracle', float('nan')):.3f}")
    print(f"written: {out / 'summary.json'}")


if __name__ == "__main__":
    main()
