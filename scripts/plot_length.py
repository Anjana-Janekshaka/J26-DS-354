"""Chart for the length test (docs/v4_preregistration.md section 5): evidence hit vs detour length.

    python scripts/plot_length.py  ->  results/figures/length_advantage.png
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = json.loads((ROOT / "eval/synthetic/controller/results_v4/length.json").read_text(encoding="utf-8"))["length_set_by_detour_exchanges"]
    xs = sorted(int(k) for k in d)
    series = [("adaptive", "Adaptive (Syno)", "#2a78d6", 2.6), ("hybrid", "Always hybrid", "#898781", 1.6),
              ("rag", "Always RAG", "#b9b7b2", 1.6), ("sliding_window", "Always sliding window", "#d4a373", 1.6)]
    fig, ax = plt.subplots(figsize=(7.5, 4), dpi=180)
    for key, label, color, lw in series:
        ys = [d[str(x)]["hit"][key] for x in xs]
        ax.plot(xs, ys, marker="o", color=color, lw=lw, label=label)
        ax.text(xs[-1] + 1.2, ys[-1], label, va="center", fontsize=8.5, color=color)
    ax.set_xticks(xs)
    ax.set_xlabel("Exchanges of unrelated detour before the late questions", fontsize=9, color="#52514e")
    ax.set_ylabel("Evidence hit rate", fontsize=9, color="#52514e")
    ax.set_ylim(0.5, 1.03)
    ax.set_xlim(0, xs[-1] + 14)
    ax.set_title("As conversations grow, adaptive stays on top; the sliding window falls away", loc="left", fontsize=11, fontweight="bold")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors="#52514e", labelsize=8.5)
    fig.text(0.01, 0.01, "60 new conversations (15 per length), held-out wording, frozen system, budget 400 tokens; nothing tuned on this set.",
             fontsize=7, color="#898781")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = ROOT / "results/figures/length_advantage.png"
    fig.savefig(out, facecolor="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
