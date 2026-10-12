"""Record-once / replay-many traces for controller evaluation.

Running the full pipeline (embeddings, summarizer, retrieval, NLI) is the expensive part, and none
of it depends on which strategy the controller picks: every module builds its context on every turn,
and escalation events come from module outputs only. So we run the pipeline ONCE per conversation
and record, in order:

  * every decision turn: the ``TurnSignal``, the query text, and the escalations it raised;
  * every probe: the ``TurnSignal``, the query, and for each of the four strategies the assembled
    context's evidence hit and token count (plus the context text, for the LLM judge).

Any controller (rule-based with any config, or a trained model) is then evaluated by *replaying*
these traces: call ``decide`` on each signal in order, register escalations after decision turns,
and look up the hit / tokens of the strategy it chose. The adaptive context is exactly the forced
context of the chosen strategy (``assemble_prompt`` uses only ``selected_strategy``), so replay gives
the same numbers as a live run - ``tests/test_controller_eval.py`` checks this.
"""

from __future__ import annotations

import gzip
import json
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable

from contracts import ControllerDecision, EscalationEvent, OverrideInfo, TurnSignal
from contracts.text import CachingEmbedder, Embedder, HashingEmbedder
from eval.metrics import oracle_label, required_hit
from integration import MemoryPipeline, assemble_prompt
from retrieval import RetrievalConfig

STRATEGIES = ["sliding_window", "summarization", "rag", "hybrid"]
SINGLES = ("sliding_window", "summarization", "rag")


def forced(turn_id: str, s: str) -> ControllerDecision:
    return ControllerDecision(turn_id=turn_id, selected_strategy=s, rationale=f"forced {s}", controller_variant="rule_based",
                              decision_latency_ms=0.0, override=OverrideInfo(applied=False, by=None))


def make_embedder(kind: str) -> Embedder:
    if kind == "hashing":
        return CachingEmbedder(HashingEmbedder())
    from retrieval import SentenceTransformerEmbedder

    return CachingEmbedder(SentenceTransformerEmbedder())


def make_nli(enabled: bool):
    if not enabled:
        return None
    from retrieval import CrossEncoderNLI

    return CrossEncoderNLI()


def trace_conversation(conv: dict, budget: int, emb: Embedder, nli, keep_contexts: bool = True) -> dict:
    pipe = MemoryPipeline(conv["id"], token_budget=budget, embedder=emb, nli=nli,
                          retrieval_config=RetrievalConfig(check_contradictions=nli is not None))
    probes_at = defaultdict(list)
    for p in conv["probes"]:
        probes_at[p["after_index"]].append(p)
    events: list[dict] = []
    for i, m in enumerate(conv["messages"]):
        if m["role"] == "user":
            r = pipe.user_turn(m["content"], respond=False)
            events.append({
                "type": "turn",
                "query": m["content"],
                "signal": r.signal.model_dump(mode="json"),
                "escalations": [e.model_dump(mode="json") for e in r.escalations],
            })
        else:
            pipe.assistant_turn(m["content"])
        for p in probes_at.get(i, []):
            r = pipe.user_turn(p["question"], remember=False, respond=False)
            b = r.signal.token_usage.budget
            ctxs = {s: assemble_prompt(forced(r.signal.turn_id, s), r.outputs, p["question"], b) for s in STRATEGIES}
            hits = {s: required_hit(c.context, p["required"], p["stale"]) for s, c in ctxs.items()}
            tokens = {s: ctxs[s].token_count for s in STRATEGIES}
            ev = {
                "type": "probe",
                "query": p["question"],
                "kind": p["kind"],
                "signal": r.signal.model_dump(mode="json"),
                "hits": hits,
                "tokens": tokens,
                "oracle": oracle_label(hits, tokens, b),
            }
            if keep_contexts:
                ev["contexts"] = {s: c.context for s, c in ctxs.items()}
            events.append(ev)
    pipe.close()
    return {"conv": conv["id"], "family": conv.get("family", "A"), "events": events}


def build_traces(convs: list[dict], budget: int, embedder: str, nli: bool, cache: Path | None, rebuild: bool = False,
                 version: str = "") -> list[dict]:
    """Trace every conversation, reusing the cache file when its header matches."""
    header = {"version": version, "budget": budget, "embedder": embedder, "nli": nli, "convs": [c["id"] for c in convs]}
    if cache is not None and cache.exists() and not rebuild:
        with gzip.open(cache, "rt", encoding="utf-8") as f:
            first = json.loads(f.readline())
            if first == header:
                return [json.loads(line) for line in f]
    warnings.filterwarnings("ignore")
    emb, scorer = make_embedder(embedder), make_nli(nli)
    traces = []
    for k, conv in enumerate(convs, 1):
        traces.append(trace_conversation(conv, budget, emb, scorer))
        if k % 20 == 0 or k == len(convs):
            print(f"  traced {k}/{len(convs)} conversations", flush=True)
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(cache, "wt", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n")
            for t in traces:
                f.write(json.dumps(t) + "\n")
    return traces


def replay(traces: Iterable[dict], controller_factory: Callable[[], object]) -> list[dict]:
    """Run a fresh controller over each conversation's trace; one row per probe."""
    rows = []
    for tr in traces:
        ctl = controller_factory()
        for ev in tr["events"]:
            sig = TurnSignal.model_validate(ev["signal"])
            if ev["type"] == "turn":
                ctl.decide(sig, commit=True)
                for e in ev["escalations"]:
                    ctl.register_escalation(EscalationEvent.model_validate(e))
                continue
            fv, d = ctl.decide(sig, commit=False)
            s = d.selected_strategy
            rows.append({
                "conv": tr["conv"],
                "family": tr["family"],
                "kind": ev["kind"],
                "query": ev["query"],
                "turn_count": fv.turn_count,
                "pressure": fv.token_budget_pressure,
                "task_type": fv.task_type,
                "prior_strategy": fv.prior_strategy,
                "time_since_last_switch": fv.time_since_last_switch,
                "adaptive": s,
                "adaptive_hit": ev["hits"][s],
                "adaptive_tokens": ev["tokens"][s],
                "hits": ev["hits"],
                "tokens": ev["tokens"],
                "acceptable": [x for x in STRATEGIES if ev["hits"][x]],
                "oracle": ev["oracle"],
                "rationale": d.rationale,
            })
    return rows
