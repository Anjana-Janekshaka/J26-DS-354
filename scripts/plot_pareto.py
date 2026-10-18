"""Cost vs. evidence-hit charts (Pareto view) from the frozen test results. No number is re-run.

    python scripts/plot_pareto.py      ->  results/figures/pareto_controller.png, pareto_locomo.png

One mark per strategy: x = mean context tokens (cost), y = evidence hit with its 95% interval.
The dashed line joins the non-dominated strategies (no other strategy is both cheaper and better).
Identity is carried by direct labels; colour only highlights the adaptive controller.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "results" / "final"
OUT = ROOT / "results" / "figures"
NAMES = {"sliding_window": "Always sliding window", "summarization": "Always summarization", "rag": "Always RAG",
         "hybrid": "Always hybrid (window + RAG)", "adaptive": "Adaptive (CEAI)"}
INK, MUTED, GRID, HIGHLIGHT, BASE = "#0b0b0b", "#52514e", "#e1e0d9", "#2a78d6", "#898781"


def pareto(points: dict[str, tuple[float, float]]) -> list[str]:
    keep = [k for k, (x, y) in points.items()
            if not any((x2 <= x and y2 >= y) and (x2, y2) != (x, y) for x2, y2 in points.values())]
    return sorted(keep, key=lambda k: points[k][0])


def plot(points, ci, title, subtitle, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=200)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    front = pareto(points)
    ax.plot([points[k][0] for k in front], [points[k][1] for k in front], ls="--", lw=1.2, color=MUTED, zorder=1)
    # Points that coincide (adaptive often equals one fixed strategy) share one label.
    xr = max(p[0] for p in points.values()) - min(p[0] for p in points.values()) or 1.0
    yr = max(p[1] for p in points.values()) - min(p[1] for p in points.values()) or 1.0
    labels: dict[str, str] = {}
    for k in sorted(points, key=lambda k: k != "adaptive"):
        twin = next((j for j in labels if abs(points[j][0] - points[k][0]) < 0.02 * xr
                     and abs(points[j][1] - points[k][1]) < 0.01 * yr), None)
        if twin:
            labels[twin] = labels[twin].replace("\n", f" = {NAMES[k]}\n", 1)
        else:
            labels[k] = f"{NAMES[k]}\n{points[k][1]:.3f}"
    placed: list[tuple[float, float]] = []
    for k, (x, y) in sorted(points.items(), key=lambda kv: kv[0] != "adaptive"):
        lo, hi = ci.get(k, (y, y))
        hot = k == "adaptive"
        ax.errorbar(x, y, yerr=[[y - lo], [hi - y]], fmt="o", ms=9 if hot else 7, color=HIGHLIGHT if hot else BASE,
                    ecolor=HIGHLIGHT if hot else BASE, elinewidth=1.5, capsize=3, zorder=5 if hot else 3,
                    markeredgecolor="#fcfcfb", markeredgewidth=1.5)
        if k not in labels:
            continue
        crowded = any(abs(px - x) < 0.45 * xr and abs(py - y) < 0.08 * yr for px, py in placed)
        ax.annotate(labels[k], (x, y), xytext=(-9 if crowded else 9, -4), textcoords="offset points", fontsize=8.5,
                    ha="right" if crowded else "left", color=INK if hot else MUTED,
                    fontweight="bold" if hot else "normal", va="center")
        placed.append((x, y))
    ax.set_xlabel("Mean memory-context tokens per question (cost)", color=MUTED, fontsize=9)
    ax.set_ylabel("Evidence hit (95% CI)", color=MUTED, fontsize=9)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED, labelsize=8.5)
    xs = [p[0] for p in points.values()]
    span = max(xs) - min(xs)
    ax.set_xlim(min(xs) - 0.35 * span - 10, max(xs) + 0.6 * span + 10)
    fig.suptitle(title, x=0.02, ha="left", fontsize=12, fontweight="bold", color=INK)
    ax.set_title(subtitle, loc="left", fontsize=8.5, color=MUTED)
    fig.text(0.02, 0.01, "Dashed line: Pareto front (no strategy is both cheaper and more accurate).", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path.relative_to(ROOT))


def main() -> None:
    c = json.loads((FINAL / "controller_test.json").read_text(encoding="utf-8"))
    pts = {k: (c["mean_context_tokens"][k], c["evidence_hit_rate"][k]["estimate"]) for k in NAMES}
    ci = {k: (c["evidence_hit_rate"][k]["ci_low"], c["evidence_hit_rate"][k]["ci_high"]) for k in NAMES}
    plot(pts, ci, "Mixed-workload conversations: adaptive is cheaper and more accurate",
         f"Synthetic strategy-switch test split - {c['n_conversations']} conversations, {c['n_probes']} probes, "
         f"budget {c['budget_tokens']} tokens", OUT / "pareto_controller.png")

    lq = json.loads((FINAL / "locomo_test.json").read_text(encoding="utf-8"))
    rows_path = ROOT / "runs" / "colab3" / "final" / "locomo" / "questions.jsonl"
    ci2 = {}
    if rows_path.exists():
        from eval.metrics import cluster_bootstrap_ci  # noqa: E402
        rows = [json.loads(line) for line in rows_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for k in NAMES:
            r = cluster_bootstrap_ci(rows, lambda rs, k=k: sum(x[k]["hit"] for x in rs) / len(rs), group_key="conv")
            ci2[k] = (r["ci_low"], r["ci_high"])
    pts2 = {k: (lq["strategies"][k]["mean_tokens"], lq["strategies"][k]["evidence_hit_rate"]) for k in NAMES}
    if rows_path.exists():  # same per-question averaging as results/RESULTS.md
        pts2 = {k: (pts2[k][0], sum(x[k]["hit"] for x in rows) / len(rows)) for k in NAMES}
    plot(pts2, ci2, "LoCoMo (pure recall): adaptive matches the best strategy",
         f"LoCoMo test split - {lq['n_questions']} questions, {lq['config']['conversations']} conversations, "
         f"budget {lq['config']['budget']} tokens", OUT / "pareto_locomo.png")


if __name__ == "__main__":
    import sys

    sys.path[:0] = [str(ROOT), str(ROOT / "packages")]
    main()
