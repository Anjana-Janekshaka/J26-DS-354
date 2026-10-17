"""The coding traps run against Mem0 (roadmap 3.1; docs/mem0_coding_preregistration.md).

    python -m demo.coding_session.run_mem0 [--budget 700] [--out runs/demo_mem0]

Needs an LLM for Mem0's extraction (CEAI_LLM_BASE_URL + CEAI_LLM_MODEL, Ollama on Colab) and
``pip install mem0ai ollama``. Mem0 sees the session the way a chat app feeds it: one ``add()`` per
completed exchange (user message + reply). At each trap the context is built two ways under the same
token budget as CEAI's demo:

  mem0               Mem0's retrieved memories for the trap message
  mem0_plus_window   the same memories plus the last 6 exchanges (the usual app pattern),
                     memories first, recent turns filling the rest of the budget

and checked with the same trap check as the CEAI arms (required text present, any stale form marked).
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from contracts import count_tokens

from .run_demo import check_trap
from .run_scenarios import slug
from .scenarios import SCENARIOS


def fit(blocks: list[str], budget: int) -> str:
    out, used = [], 0
    for b in blocks:
        t = count_tokens(b) + 1
        if used + t > budget:
            continue
        out.append(b)
        used += t
    return "\n".join(out)


def main() -> None:
    from eval.baselines.systems import Mem0Baseline

    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=700)
    ap.add_argument("--out", default="runs/demo_mem0")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    done = {}
    rows_path = out / "rows.jsonl"
    if rows_path.exists():
        for line in rows_path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done[(r["scenario"], r["trap"])] = r
    model, base = os.environ["CEAI_LLM_MODEL"], os.environ["CEAI_LLM_BASE_URL"].removesuffix("/v1")

    for sc in SCENARIOS:
        if all((sc.name, t.name) in done for t in sc.traps):
            continue
        m = Mem0Baseline(slug(sc.name), model, base)
        scope = f"{slug(sc.name)}:user"
        traps_at = {}
        for t in sc.traps:
            traps_at.setdefault(t.exchange, []).append(t)
        history: list[str] = []
        t0 = time.time()
        for ex, (user_msg, reply) in enumerate(sc.exchanges, start=1):
            for trap in traps_at.get(ex, []):
                res = m.mem.search(user_msg, top_k=30, filters={"user_id": scope})
                items = res.get("results", res) if isinstance(res, dict) else res
                memories = [f"memory: {it.get('memory', '')}" for it in sorted(items or [], key=lambda x: -float(x.get("score") or 0))]
                ctx = {"mem0": fit(memories, args.budget),
                       "mem0_plus_window": fit(memories + history[-12:], args.budget)}
                row = {"scenario": sc.name, "held_out": sc.held_out, "trap": trap.name, "kind": sc.kinds.get(trap.name, "?")}
                for arm, c in ctx.items():
                    caught, why = check_trap(c, trap)
                    row[arm] = caught
                    row[arm + "_detail"] = why
                    row[arm + "_tokens"] = count_tokens(c)
                row["memories"] = memories[:15]
                done[(sc.name, trap.name)] = row
                with open(rows_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(row) + "\n")
            msgs = [{"role": "user", "content": user_msg}] + ([{"role": "assistant", "content": reply}] if reply else [])
            try:
                m.mem.add(msgs, user_id=scope)
            except Exception:  # noqa: BLE001 - counted and reported
                m.add_failures += 1
            history += [f"user: {user_msg}"] + ([f"assistant: {reply}"] if reply else [])
        print(f"{sc.name:<28} {sum(done[(sc.name, t.name)]['mem0'] for t in sc.traps)}/{len(sc.traps)} (mem0)  "
              f"{sum(done[(sc.name, t.name)]['mem0_plus_window'] for t in sc.traps)}/{len(sc.traps)} (+window)  "
              f"{m.write_llm_calls} LLM calls, {m.add_failures} add failures, {time.time() - t0:.0f}s", flush=True)

    rows = list(done.values())
    held = [r for r in rows if r["held_out"]]
    summary = {"budget_tokens": args.budget, "model": model,
               "held_out": {a: {"caught": sum(r[a] for r in held), "of": len(held)} for a in ("mem0", "mem0_plus_window")},
               "original": {a: {"caught": sum(r[a] for r in rows if not r["held_out"]), "of": sum(not r["held_out"] for r in rows)}
                            for a in ("mem0", "mem0_plus_window")}}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
