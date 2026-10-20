"""Record a demo session once, so the viewer can replay it turn by turn.

    python -m console.record                                  # original session, frozen system
    python -m console.record --scenario invoice-service       # a held-out session
    python -m console.record --all                            # every scenario
    python -m console.record --fast                           # no models (hashing embedder): layout checks only

Runs the real ``MemoryPipeline`` with the frozen system (the same setup as
``demo/coding_session/present.py``) and, after every user message, saves a snapshot of what each
stage did: the signal, the three candidates, the controller's features, rules and decision, the
assembled prompt, the escalations raised for the next turn, and the trap checks (adaptive, the
fixed 6-exchange window and each fixed strategy, all from the same history).

Snapshots are written to ``console/recordings/<scenario>.js`` for ``console/viewer.html``, which
then replays them with no models and no network. Nothing under ``packages/`` is changed and no
decision log is written.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

from contracts import ControllerDecision, OverrideInfo, count_tokens
from controller.rules import RULES, TurnCues
from demo.coding_session.run_demo import check_trap
from demo.coding_session.run_scenarios import slug
from demo.coding_session.scenarios import SCENARIOS, Scenario
from eval.frozen import frozen_controller, system_name, system_retrieval
from integration import MemoryPipeline, assemble_prompt
from retrieval import RetrievalConfig
from sliding_window import RecencyOnlyWindow

OUT_DIR = Path(__file__).parent / "recordings"
FIXED = ("sliding_window", "summarization", "rag", "hybrid")
RULE_KIND = re.compile(r"^\[([a-z_]+)\]\s*")
MAX_CONTEXT_CHARS = 6000


def _rule_table(controller, fv, cues: TurnCues) -> list[dict]:
    """Every rule, in order, with whether it matches this turn. The first match is the one that fired."""
    rows, fired = [], False
    for rule in RULES:
        hit = rule(fv, controller.config, cues)
        rows.append({
            "fn": rule.__name__.lstrip("_"),
            "matched": hit is not None,
            "fired": hit is not None and not fired,
            "rule": hit.rule if hit else None,
            "strategy": hit.strategy if hit else None,
            "hard": hit.hard if hit else None,
            "reason": hit.reason if hit else None,
        })
        fired = fired or hit is not None
    return rows


def _rationale(decision: ControllerDecision) -> dict:
    parts = decision.rationale.split(" | ")
    m = RULE_KIND.match(parts[0])
    return {
        "full": decision.rationale,
        "rule": m.group(1) if m else None,
        "rule_reason": RULE_KIND.sub("", parts[0]),
        "dwell": [p for p in parts if p.startswith("dwell")],
        "escalations": [p for p in parts if p.startswith("escalation")],
        "override": [p for p in parts if p.startswith("OVERRIDE")],
    }


def _candidates(outputs) -> dict:
    out = {}
    for name, o in outputs.items():
        q = o.quality.model_dump()
        if name == "rag":
            q = {"granularity_tag": q.get("granularity_tag"), "retrieved": len(q.get("retrieved_chunk_ids", [])),
                 "stale_flags": len(q.get("contradiction_flags", []))}
        elif name == "sliding_window":
            q = {"kept": len(q.get("selected_turn_ids", [])), **{k: round(v, 3) for k, v in q.get("scores", {}).items()}}
        out[name] = {"tokens": o.token_count, "latency_ms": round(o.readiness.estimated_latency_ms, 2), "quality": q}
    return out


def _forced(strategy, signal, outputs, msg) -> str:
    d = ControllerDecision(turn_id=signal.turn_id, selected_strategy=strategy, rationale=f"forced {strategy}",
                           controller_variant="rule_based", decision_latency_ms=0.0,
                           override=OverrideInfo(applied=False, by=None))
    return assemble_prompt(d, outputs, msg, signal.token_usage.budget).context


def record(sc: Scenario, budget: int = 700, fast: bool = False) -> dict:
    kw = {}
    if fast:
        from contracts.text import HashingEmbedder

        kw["embedder"] = HashingEmbedder()
        retrieval = RetrievalConfig(**system_retrieval(reranker=None, check_contradictions=False))
    else:
        from retrieval.rerank import DEFAULT_RERANKER

        retrieval = RetrievalConfig(**system_retrieval(reranker=DEFAULT_RERANKER))
    pipe = MemoryPipeline(slug(sc.name), token_budget=budget, controller=frozen_controller(),
                          retrieval_config=retrieval, **kw)

    # Keep the classifier's details (matched pattern, topic similarity), which TurnResult does not carry.
    last_obs = {}
    observe = pipe.manager.observe

    def observe_and_keep(*a, **k):
        obs = observe(*a, **k)
        last_obs["cls"] = obs.classification
        return obs

    pipe.manager.observe = observe_and_keep

    fixed6 = RecencyOnlyWindow(k=12)
    traps_at: dict[int, list] = {}
    for t in sc.traps:
        traps_at.setdefault(t.exchange, []).append(t)

    turns = []
    for ex, (user_msg, reply) in enumerate(sc.exchanges, start=1):
        res = pipe.user_turn(user_msg)
        sig, fv, d = res.signal, res.feature_vector, res.decision
        cls = last_obs.get("cls")
        cues = TurnCues(shift=sig.shift_detected, recall_request=sig.recall_request)
        traps = []
        for trap in traps_at.get(ex, []):
            row = {"name": trap.name, "description": trap.description, "planted_at": trap.planted_at,
                   "kind": sc.kinds.get(trap.name, "")}
            ok, why = check_trap(res.prompt.context, trap)
            row["adaptive"] = {"caught": ok, "detail": why, "strategy": d.selected_strategy}
            ok, why = check_trap(fixed6.build_context(sig, user_msg).context_text(), trap)
            row["fixed_6_exchange_window"] = {"caught": ok, "detail": why}
            for s in FIXED:
                ok, why = check_trap(_forced(s, sig, res.outputs, user_msg), trap)
                row[s] = {"caught": ok, "detail": why}
            traps.append(row)
        turns.append({
            "exchange": ex,
            "turn_id": sig.turn_id,
            "user": user_msg,
            "assistant": reply,
            "signal": {
                "turn_count": sig.turn_count,
                "task_type": sig.task_type,
                "matched_pattern": cls.matched_rule if cls else None,
                "topic_similarity": None if cls is None or cls.topic_similarity is None else round(cls.topic_similarity, 3),
                "shift": sig.shift_detected,
                "recall_request": sig.recall_request,
                "tokens_used": sig.token_usage.used,
                "budget": sig.token_usage.budget,
            },
            "features": fv.model_dump(),
            "rules": _rule_table(pipe.controller, fv, cues),
            "decision": {
                "strategy": d.selected_strategy,
                "latency_ms": d.decision_latency_ms,
                **_rationale(d),  # "override" here is the list of override notes from the rationale
                "override_info": d.override.model_dump(),
            },
            "candidates": _candidates(res.outputs),
            "prompt": {"tokens": count_tokens(res.prompt.context), "context": res.prompt.context[:MAX_CONTEXT_CHARS],
                       "truncated": len(res.prompt.context) > MAX_CONTEXT_CHARS},
            "raised": [{"kind": e.kind, "source_module": e.source_module,
                        "detail": {k: v for k, v in e.detail.items() if k != "flags"}} for e in res.escalations],
            "traps": traps,
        })
        fixed6.ingest(res.turn)
        if reply:
            fixed6.ingest(pipe.assistant_turn(reply))
    pipe.close()

    cfg, default = pipe.controller.config, pipe.controller.default_strategy
    names = [t["name"] for turn in turns for t in turn["traps"]]
    score = {s: sum(t[s]["caught"] for turn in turns for t in turn["traps"])
             for s in ("adaptive", "fixed_6_exchange_window", *FIXED)}
    return {
        "scenario": sc.name,
        "slug": slug(sc.name),
        "language": sc.language,
        "held_out": sc.held_out,
        "system": system_name(),
        "mode": "fast (hashing embedder, no reranker, no NLI): layout check only" if fast else "full",
        "budget": budget,
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rule_config": {**cfg.model_dump(), "default_strategy": default},
        "n_traps": len(names),
        "score": score,
        "turns": turns,
    }


def write(session: dict, out_dir: Path = OUT_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{session['slug']}.js"
    path.write_text("window.CEAI_SESSIONS = window.CEAI_SESSIONS || {};\n"
                    f"window.CEAI_SESSIONS[{json.dumps(session['slug'])}] = {json.dumps(session, indent=1)};\n",
                    encoding="utf-8")
    index = sorted(p.stem for p in out_dir.glob("*.js") if p.stem != "index")
    (out_dir / "index.js").write_text(f"window.CEAI_INDEX = {json.dumps(index)};\n", encoding="utf-8")
    return path


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenario", default=SCENARIOS[0].name, help="scenario name or slug")
    ap.add_argument("--all", action="store_true", help="record every scenario")
    ap.add_argument("--budget", type=int, default=700)
    ap.add_argument("--fast", action="store_true", help="no models: for checking the viewer layout only")
    ap.add_argument("--out", default=str(OUT_DIR))
    args = ap.parse_args()
    chosen = SCENARIOS if args.all else [s for s in SCENARIOS if args.scenario in (s.name, slug(s.name))]
    if not chosen:
        sys.exit(f"unknown scenario {args.scenario!r}; choose from: " + ", ".join(slug(s.name) for s in SCENARIOS))
    if not args.fast:
        print("Loading models (about 20 s)...", flush=True)
    for sc in chosen:
        session = record(sc, args.budget, args.fast)
        path = write(session, Path(args.out))
        s = session["score"]
        print(f"{sc.name}: {len(session['turns'])} turns, traps adaptive {s['adaptive']}/{session['n_traps']}, "
              f"fixed window {s['fixed_6_exchange_window']}/{session['n_traps']} -> {path}", flush=True)
    print("Open console/viewer.html in a browser.")


if __name__ == "__main__":
    main()
