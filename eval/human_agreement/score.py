"""Score filled labelling sheets: LLM judge vs humans, and humans vs each other.

    python -m eval.human_agreement.score [--sheets eval/human_agreement/sheets]

Reports (written to ``agreement.json``):
  * judge vs human  - percent agreement, Cohen's kappa (unweighted and linear-weighted over the
                      ordered classes WRONG < PARTIAL < CORRECT), binary agreement (correct vs not)
                      and the confusion matrix. Shared items use the human majority label.
  * human vs human  - Fleiss' kappa on the shared items (how hard the task is for people).
Rule of thumb for the slide: judge kappa >= 0.6 ("substantial") -> the free judge's scores are
citable alongside the deterministic metrics; below that, report only the deterministic metrics.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
CLASSES = ["WRONG", "PARTIAL", "CORRECT"]
ALIASES = {"c": "CORRECT", "correct": "CORRECT", "1": "CORRECT", "1.0": "CORRECT",
           "p": "PARTIAL", "partial": "PARTIAL", "0.5": "PARTIAL", ".5": "PARTIAL",
           "w": "WRONG", "wrong": "WRONG", "0": "WRONG", "0.0": "WRONG", "incorrect": "WRONG"}


def norm(label: str) -> str | None:
    return ALIASES.get((label or "").strip().lower())


def cohen_kappa(a: list[str], b: list[str], weighted: bool = False) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    k = len(CLASSES)
    idx = {c: i for i, c in enumerate(CLASSES)}
    w = [[(abs(i - j) / (k - 1) if weighted else float(i != j)) for j in range(k)] for i in range(k)]
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[idx[x]][idx[y]] += 1 / n
    pa = [sum(obs[i]) for i in range(k)]
    pb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    do = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k))
    de = sum(w[i][j] * pa[i] * pb[j] for i in range(k) for j in range(k))
    return 1 - do / de if de > 0 else 1.0


def fleiss_kappa(ratings: list[list[str]]) -> float:
    """ratings: per item, the list of labels from all raters (same number of raters per item)."""
    if not ratings:
        return float("nan")
    m = len(ratings[0])
    if m < 2:
        return float("nan")
    p_j = Counter()
    p_i = []
    for item in ratings:
        c = Counter(item)
        p_j.update(c)
        p_i.append((sum(v * v for v in c.values()) - m) / (m * (m - 1)))
    total = len(ratings) * m
    pe = sum((v / total) ** 2 for v in p_j.values())
    pbar = sum(p_i) / len(p_i)
    return (pbar - pe) / (1 - pe) if pe < 1 else 1.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheets", default=str(HERE / "sheets"))
    args = ap.parse_args()
    d = Path(args.sheets)
    key = json.loads((d / "key.json").read_text(encoding="utf-8"))

    labels: dict[str, dict[str, str]] = {}
    problems = []
    for name in key["assignment"]:
        path = d / f"{name}.csv"
        if not path.exists():
            problems.append(f"{name}: sheet missing")
            continue
        with open(path, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                lab = norm(row.get("label", ""))
                if lab is None:
                    problems.append(f"{name} {row['item_id']}: unreadable label {row.get('label')!r}")
                    continue
                labels.setdefault(row["item_id"], {})[name] = lab

    shared = key["shared_items"]
    human: dict[str, str] = {}
    for item, by in labels.items():
        votes = Counter(by.values()).most_common()
        if len(votes) > 1 and votes[0][1] == votes[1][1]:
            continue  # tie between humans: no reference label for this item
        human[item] = votes[0][0]
    items = sorted(i for i in human if key["items"][i]["judge_grade"] in CLASSES)
    j = [key["items"][i]["judge_grade"] for i in items]
    h = [human[i] for i in items]

    report = {
        "n_items_scored": len(items),
        "judge_vs_human": {
            "percent_agreement": sum(x == y for x, y in zip(j, h)) / len(items) if items else None,
            "cohen_kappa": cohen_kappa(j, h),
            "cohen_kappa_linear_weighted": cohen_kappa(j, h, weighted=True),
            "binary_correct_agreement": sum((x == "CORRECT") == (y == "CORRECT") for x, y in zip(j, h)) / len(items) if items else None,
            "confusion_judge_rows_human_cols": {a: {b: sum(1 for x, y in zip(j, h) if x == a and y == b) for b in CLASSES} for a in CLASSES},
        },
        "human_vs_human_fleiss_kappa_shared": fleiss_kappa(
            [[labels[i][a] for a in key["assignment"]] for i in shared if i in labels and len(labels[i]) == len(key["assignment"])]
        ),
        "problems": problems,
    }
    (d / "agreement.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    jv = report["judge_vs_human"]
    print(f"items scored: {len(items)}")
    if items:
        print(f"judge vs human: agreement {jv['percent_agreement']:.3f}, kappa {jv['cohen_kappa']:.3f} "
              f"(weighted {jv['cohen_kappa_linear_weighted']:.3f}), binary agreement {jv['binary_correct_agreement']:.3f}")
    print(f"human vs human (Fleiss, shared items): {report['human_vs_human_fleiss_kappa_shared']:.3f}")
    for p in problems:
        print("  !", p)
    print(f"written: {d / 'agreement.json'}")


if __name__ == "__main__":
    main()
