"""BEAM 100K on the frozen system (docs/beam_preregistration.md). Deterministic, no LLM.

    python -m eval.beam.run [--budget 1024] [--out eval/beam/results]

Every chat message is ingested in order, then each probing question is asked as a non-committing
probe; all strategy contexts come from the same module outputs (as in eval/locomo/run.py). Metrics:
evidence hit for questions citing source turns, answer-in-context (content words) for short answers.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import statistics
import warnings
from collections import Counter
from pathlib import Path

from contracts import ControllerDecision, OverrideInfo
from contracts.text import CachingEmbedder, content_words
from eval.frozen import frozen_controller, system_name, system_retrieval
from eval.metrics import cluster_bootstrap_ci, evidence_hit
from integration import MemoryPipeline, assemble_prompt
from retrieval import RetrievalConfig, SentenceTransformerEmbedder
from retrieval.rerank import DEFAULT_RERANKER

HERE = Path(__file__).parent
STRATEGIES = ["sliding_window", "summarization", "rag", "hybrid"]
NAMES = STRATEGIES + ["adaptive"]
INDEX = re.compile(r"\s*->->\s*\d+\s*,\s*\d+\s*$")


def forced(tid: str, s: str) -> ControllerDecision:
    return ControllerDecision(turn_id=tid, selected_strategy=s, rationale=f"forced {s}", controller_variant="rule_based",
                              decision_latency_ms=0.0, override=OverrideInfo(applied=False, by=None))


def cited_ids(q: dict) -> list[int]:
    ids = q.get("source_chat_ids")
    if ids:
        return [int(i) for i in ids]
    refs = " ".join(map(str, q.get("conversation_references", []) or []))
    return [int(x) for x in re.findall(r"chat_id:\s*(\d+)", refs)]


def short_answer(q: dict) -> str | None:
    a = q.get("answer")
    return a if isinstance(a, str) and 0 < len(a.split()) <= 25 else None


def answer_hit(answer: str, context: str) -> bool:
    words = set(content_words(answer))
    return bool(words) and words <= set(content_words(context))


def run_conversation(row: dict, budget: int, emb) -> list[dict]:
    cid = str(row["conversation_id"])
    pipe = MemoryPipeline(f"beam-{cid}", token_budget=budget, embedder=emb, nli=None, controller=frozen_controller(),
                          retrieval_config=RetrievalConfig(**system_retrieval(check_contradictions=False, reranker=DEFAULT_RERANKER)))
    text_of: dict[int, str] = {}
    for session in row["chat"]:
        for m in session:
            content = INDEX.sub("", m["content"])
            text_of[int(m["id"])] = content
            pipe.add_turn("user" if m["role"] == "user" else "assistant", content)
    rows = []
    for category, qs in ast.literal_eval(row["probing_questions"]).items():
        for q in qs:
            r = pipe.user_turn(q["question"], remember=False, respond=False)
            b = r.signal.token_usage.budget
            ctx = {s: assemble_prompt(forced(r.signal.turn_id, s), r.outputs, q["question"], b).context for s in STRATEGIES}
            ctx["adaptive"] = r.prompt.context
            ev = [text_of[i] for i in cited_ids(q) if i in text_of]
            ans = short_answer(q)
            out = {"conv": cid, "category": category, "adaptive_choice": r.decision.selected_strategy,
                   "task_type": r.feature_vector.task_type, "n_evidence": len(ev), "has_answer": ans is not None}
            for s, c in ctx.items():
                out[s] = {"evidence_hit": evidence_hit(ev, c)[1] if ev else None,
                          "answer_in_context": answer_hit(ans, c) if ans else None}
            rows.append(out)
    pipe.close()
    return rows


def summarize(rows: list[dict]) -> dict:
    def rate(rs, s, key):
        vals = [r[s][key] for r in rs if r[s][key] is not None]
        return statistics.mean(vals) if vals else None

    out: dict = {"n_questions": len(rows), "system": system_name()}
    for key in ("evidence_hit", "answer_in_context"):
        scored = [r for r in rows if r["adaptive"][key] is not None]
        per = {s: rate(scored, s, key) for s in NAMES}
        best = max(("sliding_window", "summarization", "rag"), key=lambda s: per[s])
        cis = {}
        for other in (best, "hybrid"):
            pairs = [{"conv": r["conv"], "d": float(r["adaptive"][key]) - float(r[other][key])} for r in scored]
            cis[f"adaptive_minus_{other}"] = cluster_bootstrap_ci(pairs, lambda x: sum(p["d"] for p in x) / len(x))
        out[key] = {"n": len(scored), "per_strategy": per, "best_single": best, **cis,
                    "by_category": {c: {s: rate([r for r in scored if r["category"] == c], s, key) for s in NAMES}
                                    | {"n": sum(r["category"] == c for r in scored)}
                                    for c in sorted({r["category"] for r in scored})}}
    out["controller_choices"] = dict(Counter(r["adaptive_choice"] for r in rows))
    out["task_types"] = dict(Counter(r["task_type"] for r in rows))
    return out


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=1024)
    ap.add_argument("--data", default=str(HERE / "data" / "beam_100K.json"))
    ap.add_argument("--out", default=str(HERE / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    emb = CachingEmbedder(SentenceTransformerEmbedder())
    done = {}
    qpath = out / "questions.jsonl"
    if qpath.exists():  # resume after an interruption
        for line in qpath.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.setdefault(r["conv"], []).append(r)
    rows = []
    for k, row in enumerate(data, 1):
        cid = str(row["conversation_id"])
        if cid in done:
            rows += done[cid]
            continue
        rs = run_conversation(row, args.budget, emb)
        rows += rs
        with open(qpath, "a", encoding="utf-8") as f:
            f.write("".join(json.dumps(r) + "\n" for r in rs))
        print(f"{k}/{len(data)} conversations", flush=True)
    summary = summarize(rows)
    summary["budget_tokens"] = args.budget
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    for key in ("evidence_hit", "answer_in_context"):
        v = summary[key]
        print(f"\n{key} (n={v['n']}): " + "  ".join(f"{s} {v['per_strategy'][s]:.3f}" for s in NAMES))
        for name in (f"adaptive_minus_{v['best_single']}", "adaptive_minus_hybrid"):
            c = v[name]
            print(f"  {name}: {c['estimate']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]")
    print(f"\ncontroller choices: {summary['controller_choices']}")


if __name__ == "__main__":
    main()
