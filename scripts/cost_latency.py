"""Write-time cost and build time per conversation, from timings already recorded (nothing is re-run).

    python scripts/cost_latency.py   ->  results/final/cost_latency.json, results/figures/memory_build_time.png

Sources (all on a free Colab T4, LoCoMo test conversations):
  * CEAI: ``runs[].ingest_s`` in results/final/locomo_test.json (frozen system; this LoCoMo run had the
    NLI staleness check off, ``--no-nli``, so NLI time is not included).
  * Baselines: ``ingest_seconds`` and ``write_llm_calls`` in results/final/baselines*/write_cost.jsonl.
A dollar figure is deliberately not computed: per-call token counts were not recorded for Mem0, so any
price would be a guess.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "results" / "final"


def costs(path: Path, system: str) -> list[dict]:
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    return [r for r in rows if r["system"] == system and "write_llm_calls" in r]


def main() -> None:
    loc = json.loads((FINAL / "locomo_test.json").read_text(encoding="utf-8"))
    ceai_runs = loc["runs"]
    table = {
        "CEAI (frozen)": {"build_seconds_per_conversation": statistics.mean(r["ingest_s"] for r in ceai_runs),
                          "write_llm_calls_per_conversation": 0,
                          "note": "all three strategy modules + conversation manager; NLI staleness check off in this run"},
    }
    for label, path, system in (("Mem0 (corrected)", FINAL / "baselines_mem0_fixed" / "write_cost.jsonl", "mem0"),
                                ("Summary buffer", FINAL / "baselines" / "write_cost.jsonl", "summary_buffer"),
                                ("Fixed-chunk RAG", FINAL / "baselines" / "write_cost.jsonl", "fixed_chunk_rag")):
        rs = costs(path, system)
        table[label] = {"build_seconds_per_conversation": statistics.mean(r["ingest_seconds"] for r in rs),
                        "write_llm_calls_per_conversation": statistics.mean(r["write_llm_calls"] for r in rs)}
    ceai = table["CEAI (frozen)"]["build_seconds_per_conversation"]
    for v in table.values():
        v["x_slower_than_ceai"] = v["build_seconds_per_conversation"] / ceai
    out = {"hardware": "free Colab T4, Qwen2.5-7B via Ollama for LLM-based systems", "conversations": len(ceai_runs),
           "mean_turns_per_conversation": statistics.mean(r["turns"] for r in ceai_runs), "systems": table}
    (FINAL / "cost_latency.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = list(table)[::-1]
    secs = [table[n]["build_seconds_per_conversation"] for n in names]
    fig, ax = plt.subplots(figsize=(8, 3.4), dpi=180)
    colors = ["#2a78d6" if n.startswith("CEAI") else "#898781" for n in names]
    ax.barh(names, secs, color=colors, height=0.55)
    ax.set_xscale("log")
    for y, (n, s) in enumerate(zip(names, secs)):
        calls = table[n]["write_llm_calls_per_conversation"]
        ax.text(s * 1.12, y, f"{s:,.0f} s  ·  {calls:.0f} LLM calls", va="center", fontsize=8.5, color="#0b0b0b")
    ax.set_xlabel("Seconds to build memory for one LoCoMo conversation (log scale, Colab T4)", fontsize=9, color="#52514e")
    ax.set_title("Building memory: CEAI makes no LLM calls", loc="left", fontsize=12, fontweight="bold")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_xlim(right=max(secs) * 12)
    ax.tick_params(colors="#52514e", labelsize=9)
    fig.text(0.01, 0.01, f"Mean over {len(ceai_runs)} LoCoMo test conversations (~{out['mean_turns_per_conversation']:.0f} turns). "
             "CEAI timing excludes the NLI staleness check (off in this run).", fontsize=7, color="#898781")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    (ROOT / "results" / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(ROOT / "results" / "figures" / "memory_build_time.png", facecolor="white")
    for n in list(table):
        v = table[n]
        print(f"{n:<18} {v['build_seconds_per_conversation']:>8.1f} s  {v['write_llm_calls_per_conversation']:>5.1f} calls  x{v['x_slower_than_ceai']:.0f}")


if __name__ == "__main__":
    main()
