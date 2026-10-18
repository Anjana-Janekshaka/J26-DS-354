"""Dev-tuned chunking weights (docs/v4_preregistration.md section 3).

    python -m eval.locomo.chunking_search            # dev: 60 random configs + the hand-set one, gate
    python -m eval.locomo.chunking_search --test     # test, once, after the gate

Measurement is the one in eval/locomo/run.py: per question, walk the chunk ranking (top 60) and keep
chunks until a 400-word budget is spent; recall = share of gold evidence turns covered. Turns are built
by the conversation manager exactly as in the pipeline, and each index sees the same turns.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import warnings
from pathlib import Path

from contracts.text import CachingEmbedder
from conversation_manager import ConversationManager
from retrieval import RetrievalConfig, RetrievalEngine, SentenceTransformerEmbedder
from retrieval.chunking import BoundaryConfig

from .loader import load

HERE = Path(__file__).parent
OUT = HERE / "results_v4"
WORD_BUDGET = 400


def split(name: str):
    return [c for i, c in enumerate(load()) if i % 2 == (0 if name == "dev" else 1)]


def build_turns(convs, emb):
    out = []
    for conv in convs:
        mgr = ConversationManager(conv.sample_id, 1024, embedder=emb)
        dia_to_tid, turns = {}, []
        for t in conv.turns:
            turn = mgr.observe("user", t.text, decision_point=False, speaker=t.speaker,
                               metadata={"date": t.date, "dia_id": t.dia_id}).turn
            dia_to_tid[t.dia_id] = turn.turn_id
            turns.append(turn)
        qs = [(q.question, {dia_to_tid[e] for e in q.evidence if e in dia_to_tid}) for q in conv.qa]
        out.append((turns, [q for q in qs if q[1]]))
    return out


def recall_at_budget(data, emb, mode: str, boundary: BoundaryConfig | None = None) -> float:
    vals = []
    for turns, qs in data:
        eng = RetrievalEngine(emb, None, RetrievalConfig(mode=mode, check_contradictions=False,
                                                         boundary=boundary or BoundaryConfig()))
        for t in turns:
            eng.ingest(t)
        for question, ev in qs:
            cov, words = set(), 0
            for c, _ in eng.search(question, 60):
                n = len(c.text.split())
                if words + n > WORD_BUDGET:
                    continue
                cov |= set(c.turn_ids)
                words += n
            vals.append(len(ev & cov) / len(ev))
    return statistics.mean(vals)


def candidates() -> list[dict]:
    rng = random.Random(7)
    hand = BoundaryConfig()
    out = [{"bias": hand.bias, "w_semantic": hand.w_semantic, "w_length": hand.w_length, "w_turns": hand.w_turns,
            "max_segment_tokens": hand.max_segment_tokens, "max_segment_turns": hand.max_segment_turns}]
    for _ in range(60):
        out.append({"bias": rng.uniform(-6, 0), "w_semantic": rng.uniform(0, 8), "w_length": rng.uniform(0, 6),
                    "w_turns": rng.uniform(0, 4), "max_segment_tokens": rng.choice([100, 150, 200, 300]),
                    "max_segment_turns": rng.choice([3, 4, 6, 8])})
    return out


def main() -> None:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    emb = CachingEmbedder(SentenceTransformerEmbedder())

    if not args.test:
        data = build_turns(split("dev"), emb)
        fixed = {m: recall_at_budget(data, emb, m) for m in ("turn", "segment")}
        print(f"dev fixed: {fixed}", flush=True)
        rows = []
        for i, cfg in enumerate(candidates()):
            r = recall_at_budget(data, emb, "adaptive", BoundaryConfig(**cfg))
            rows.append({"candidate": i, "config": cfg, "recall@400": r})
            print(f"  {i:>2} recall@400 {r:.4f}", flush=True)
        best = max(rows, key=lambda r: (r["recall@400"], -r["candidate"]))
        gate = best["recall@400"] > fixed["segment"]
        out = {"split": "dev", "fixed": fixed, "hand_set": rows[0], "best": best, "gate_passed": gate, "all": rows}
        (OUT / "chunking_dev.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"best #{best['candidate']} {best['recall@400']:.4f} vs segment {fixed['segment']:.4f} "
              f"(hand-set {rows[0]['recall@400']:.4f}): gate {'PASSED' if gate else 'FAILED'}")
        return

    dev = json.loads((OUT / "chunking_dev.json").read_text(encoding="utf-8"))
    assert dev["gate_passed"], "dev gate failed: no test run (pre-registration section 3)"
    data = build_turns(split("test"), emb)
    out = {"split": "test", "turn": recall_at_budget(data, emb, "turn"), "segment": recall_at_budget(data, emb, "segment"),
           "adaptive_v1": recall_at_budget(data, emb, "adaptive"),
           "adaptive_v2": recall_at_budget(data, emb, "adaptive", BoundaryConfig(**dev["best"]["config"]))}
    (OUT / "chunking_test.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
