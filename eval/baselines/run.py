"""External memory baselines on the LoCoMo test split, under identical conditions to CEAI.

    python -m eval.baselines.run --ceai-questions <final/locomo_qa/questions.jsonl> --out <dir>
        [--systems fixed_chunk_rag,summary_buffer,mem0,full_context] [--full-context-per-conv 12]

Protocol (fixed before running): docs/baselines_protocol.md. Needs an LLM configured the same way
as the other harnesses (CEAI_LLM_BASE_URL / CEAI_LLM_MODEL, optional CEAI_JUDGE_MODEL).
Rows are appended per conversation and system, so an interrupted run resumes where it stopped.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from contracts import count_tokens
from contracts.text import CachingEmbedder
from eval.judge import GRADES, grade
from eval.locomo.loader import load
from eval.locomo.run import QA_SYSTEM
from eval.metrics import cluster_bootstrap_ci, token_f1
from integration.llm_client import CachedLLM, OpenAICompatibleLLM, concurrency, describe, get_llm
from retrieval import SentenceTransformerEmbedder

from .systems import FixedChunkRAG, FullContext, Line, Mem0Baseline, SummaryBuffer

ALL = ["fixed_chunk_rag", "summary_buffer", "mem0", "full_context"]


def sampled_questions(conv, n: int, seed: int):
    """Exactly the sample used by CEAI's frozen answer-accuracy run (eval/locomo/run.py)."""
    qs = conv.qa
    if n and n < len(qs):
        rng = random.Random(f"{seed}:{conv.sample_id}")
        keep = set(rng.sample(range(len(qs)), n))
        qs = [q for i, q in enumerate(qs) if i in keep]
    return [q for q in qs if q.answer is not None and q.category != 5]


def make_system(name: str, conv_id: str, emb, summarizer):
    if name == "fixed_chunk_rag":
        return FixedChunkRAG(emb)
    if name == "summary_buffer":
        return SummaryBuffer(summarizer)
    if name == "full_context":
        return FullContext()
    if name == "mem0":
        return Mem0Baseline(conv_id, os.environ["CEAI_LLM_MODEL"], os.environ["CEAI_LLM_BASE_URL"].removesuffix("/v1"))
    raise ValueError(name)


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ceai-questions", required=True, help="questions.jsonl from CEAI's frozen test answer-accuracy run")
    ap.add_argument("--systems", default=",".join(ALL))
    ap.add_argument("--budget", type=int, default=1024)
    ap.add_argument("--max-questions", type=int, default=60)
    ap.add_argument("--sample-seed", type=int, default=0)
    ap.add_argument("--full-context-per-conv", type=int, default=12)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    systems = [s for s in a.systems.split(",") if s]

    llm = get_llm(out / "llm_cache.jsonl")
    judge = get_llm(out / "judge_cache.jsonl", role="judge")
    if llm is None or judge is None:
        raise SystemExit("configure an LLM: CEAI_LLM_BASE_URL + CEAI_LLM_MODEL (see notebooks/free_gpu_eval.ipynb)")
    summarizer = CachedLLM(OpenAICompatibleLLM(os.environ["CEAI_LLM_BASE_URL"], os.environ["CEAI_LLM_MODEL"], max_tokens=400,
                                               timeout_s=float(os.environ.get("CEAI_LLM_TIMEOUT", "300"))),
                           out / "summary_cache.jsonl")
    emb = CachingEmbedder(SentenceTransformerEmbedder())

    ceai: dict = {}
    for line in Path(a.ceai_questions).read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if "question" in r:
                ceai[(r["conv"], r["question"])] = r

    rows_path, cost_path = out / "rows.jsonl", out / "write_cost.jsonl"
    done = {(r["conv"], r["system"]) for r in map(json.loads, rows_path.read_text(encoding="utf-8").splitlines())} if rows_path.exists() else set()
    convs = [c for i, c in enumerate(load()) if i % 2 == 1]  # LoCoMo test split
    for conv in convs:
        lines = [Line(t.speaker, t.text, t.date, t.session) for t in conv.turns]
        qs = sampled_questions(conv, a.max_questions, a.sample_seed)
        missing = [q.question for q in qs if (conv.sample_id, q.question) not in ceai]
        if missing:
            raise SystemExit(f"{conv.sample_id}: {len(missing)} questions not in the CEAI file - the samples differ")
        for name in systems:
            if (conv.sample_id, name) in done:
                print(f"{conv.sample_id} {name}: already done", flush=True)
                continue
            sys_qs = qs[: a.full_context_per_conv] if name == "full_context" else qs
            t0 = time.time()
            try:
                system = make_system(name, conv.sample_id, emb, summarizer)
                system.ingest(lines)
            except Exception as e:  # noqa: BLE001 - reported as a failure row, never dropped
                with open(cost_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"conv": conv.sample_id, "system": name, "error": f"{type(e).__name__}: {e}"}) + "\n")
                print(f"{conv.sample_id} {name}: FAILED {type(e).__name__}: {e}", flush=True)
                continue

            def answer(q, system=system):
                r0 = time.perf_counter()
                ctx = system.context(q.question, a.budget)
                read_ms = (time.perf_counter() - r0) * 1000
                pred = llm(QA_SYSTEM, f"[Memory context]\n{ctx}\n\nQuestion: {q.question}")
                g = grade(judge, q.question, str(q.answer), pred)
                return {"conv": conv.sample_id, "system": name, "question": q.question, "gold": str(q.answer), "category": q.category,
                        "answer": pred, "judge_grade": g, "judge_score": GRADES.get(g) if g else None,
                        "qa_f1": token_f1(pred, str(q.answer)), "context_tokens": count_tokens(ctx), "read_ms": read_ms}

            try:
                with ThreadPoolExecutor(1 if name == "mem0" else concurrency()) as pool:
                    results = list(pool.map(answer, sys_qs))
            except Exception as e:  # noqa: BLE001 - e.g. the LLM server timing out; recorded, run continues
                with open(cost_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"conv": conv.sample_id, "system": name, "error": f"{type(e).__name__}: {e}"}) + "\n")
                print(f"{conv.sample_id} {name}: FAILED while answering - {type(e).__name__}: {e}", flush=True)
                continue
            with open(rows_path, "a", encoding="utf-8") as f:
                for r in results:
                    f.write(json.dumps(r) + "\n")
            with open(cost_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"conv": conv.sample_id, "system": name, "write_llm_calls": system.write_llm_calls,
                                    "ingest_seconds": system.ingest_seconds, "turns": len(lines),
                                    "add_failures": getattr(system, "add_failures", None)}) + "\n")
            print(f"{conv.sample_id} {name}: {len(results)} questions, {system.write_llm_calls} write-time LLM calls, "
                  f"{time.time() - t0:.0f}s", flush=True)

    summarize(out, ceai, systems, describe(llm), describe(judge))


def summarize(out: Path, ceai: dict, systems: list[str], answer_model: str, judge_model: str) -> None:
    rows = [json.loads(x) for x in (out / "rows.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    costs = [json.loads(x) for x in (out / "write_cost.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()] if (out / "write_cost.jsonl").exists() else []

    def mean_ci(rs, key):
        rs = [r for r in rs if r.get(key) is not None]
        if not rs:
            return None
        c = cluster_bootstrap_ci(rs, lambda x: statistics.mean(r[key] for r in x), "conv", 2000)
        return {"estimate": c["estimate"], "ci_low": c["ci_low"], "ci_high": c["ci_high"], "n": len(rs)}

    summary: dict = {"answer_model": answer_model, "judge_model": judge_model, "protocol": "docs/baselines_protocol.md", "systems": {}}
    for name in systems:
        rs = [r for r in rows if r["system"] == name]
        if not rs:
            summary["systems"][name] = {"status": "not run or failed",
                                        "errors": [c.get("error") for c in costs if c["system"] == name and c.get("error")]}
            continue
        # CEAI on exactly the same questions
        paired = []
        for r in rs:
            c = ceai[(r["conv"], r["question"])]["adaptive"]
            if r["judge_score"] is not None and c.get("judge_score") is not None:
                paired.append({"conv": r["conv"], "d": c["judge_score"] - r["judge_score"], "c": c["judge_score"]})
        d = cluster_bootstrap_ci(paired, lambda x: statistics.mean(p["d"] for p in x), "conv", 2000) if paired else None
        cc = [c for c in costs if c["system"] == name and "write_llm_calls" in c]
        summary["systems"][name] = {
            "judge_score": mean_ci(rs, "judge_score"),
            "token_f1": statistics.mean(r["qa_f1"] for r in rs),
            "mean_context_tokens": statistics.mean(r["context_tokens"] for r in rs),
            "mean_read_ms": statistics.mean(r["read_ms"] for r in rs),
            "ceai_judge_score_same_questions": statistics.mean(p["c"] for p in paired) if paired else None,
            "ceai_minus_system": {"estimate": d["estimate"], "ci_low": d["ci_low"], "ci_high": d["ci_high"]} if d else None,
            "write_llm_calls_per_conversation": statistics.mean(c["write_llm_calls"] for c in cc) if cc else None,
            "ingest_seconds_per_conversation": statistics.mean(c["ingest_seconds"] for c in cc) if cc else None,
            "add_failures": sum(c.get("add_failures") or 0 for c in cc),
            "n_questions": len(rs),
        }
    allq = list(ceai.values())
    summary["ceai_frozen"] = {"judge_score": statistics.mean(r["adaptive"]["judge_score"] for r in allq if r["adaptive"].get("judge_score") is not None),
                              "token_f1": statistics.mean(r["adaptive"]["qa_f1"] for r in allq),
                              "write_llm_calls_per_conversation": 0, "n_questions": len(allq)}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nBaselines (answers: {answer_model}; judge: {judge_model})")
    print(f"{'system':<18}{'judge':>8}{'F1':>7}{'ctx tok':>8}{'write LLM calls/conv':>22}   CEAI - system [95% CI]")
    print(f"{'CEAI (frozen)':<18}{summary['ceai_frozen']['judge_score']:>8.3f}{summary['ceai_frozen']['token_f1']:>7.3f}{'':>8}{0:>22}")
    for name, v in summary["systems"].items():
        if "judge_score" not in v:
            print(f"{name:<18} {v['status']} {v.get('errors')}")
            continue
        d = v["ceai_minus_system"]
        print(f"{name:<18}{v['judge_score']['estimate']:>8.3f}{v['token_f1']:>7.3f}{v['mean_context_tokens']:>8.0f}"
              f"{v['write_llm_calls_per_conversation'] or 0:>22.0f}   {d['estimate']:+.3f} [{d['ci_low']:+.3f}, {d['ci_high']:+.3f}]"
              + (f"  (n={v['n_questions']})" if name == "full_context" else ""))
    print(f"written: {out / 'summary.json'}")


if __name__ == "__main__":
    main()
