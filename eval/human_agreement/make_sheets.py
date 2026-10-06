"""Build blind labelling sheets to check the LLM answer-judge against humans.

    python -m eval.human_agreement.make_sheets --questions <run>/questions.jsonl [--out eval/human_agreement/sheets]

Samples judged answers from a LoCoMo run made with ``--llm --judge-answers``, stratified over the
judge's grades so every class is tested. Writes one CSV per annotator (``annotator_1.csv`` ...).
Every annotator labels the same ``--shared`` items (for human-human agreement) plus their own
``--per-annotator`` items. Annotators never see the judge's grade or which memory strategy produced
the answer; those go to ``key.json`` for ``score.py``.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
STRATEGIES = ("adaptive", "rag", "sliding_window", "summarization", "hybrid")
COLUMNS = ["item_id", "question", "gold_answer", "response", "label", "notes"]


def load_pool(path: Path) -> list[dict]:
    pool, seen = [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if "question" not in row:
            continue
        for s in STRATEGIES:
            r = row.get(s) or {}
            if r.get("judge_grade") is None or "answer" not in r:
                continue
            key = (row["question"], r["answer"].strip().lower())
            if key in seen:  # identical answers to the same question are labelled once
                continue
            seen.add(key)
            pool.append({"question": row["question"], "gold_answer": row["gold_answer"], "response": r["answer"],
                         "judge_grade": r["judge_grade"], "strategy": s, "conv": row["conv"], "category": row["category"]})
    return pool


def stratified(pool: list[dict], n: int, rng: random.Random) -> list[dict]:
    by = defaultdict(list)
    for item in pool:
        by[item["judge_grade"]].append(item)
    for v in by.values():
        rng.shuffle(v)
    picked: list[dict] = []
    while len(picked) < n and any(by.values()):
        for g in sorted(by):
            if by[g] and len(picked) < n:
                picked.append(by[g].pop())
    return picked


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", required=True, help="questions.jsonl from eval.locomo.run --llm --judge-answers")
    ap.add_argument("--out", default=str(HERE / "sheets"))
    ap.add_argument("--annotators", type=int, default=4)
    ap.add_argument("--shared", type=int, default=12)
    ap.add_argument("--per-annotator", type=int, default=12)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    pool = load_pool(Path(args.questions))
    need = args.shared + args.annotators * args.per_annotator
    if len(pool) < need:
        raise SystemExit(f"only {len(pool)} judged answers available, need {need}; run more questions or lower the counts")
    items = stratified(pool, need, rng)
    rng.shuffle(items)
    for i, it in enumerate(items, 1):
        it["item_id"] = f"h{i:03d}"
    shared, rest = items[: args.shared], items[args.shared :]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    assignment: dict[str, list[str]] = {}
    for a in range(1, args.annotators + 1):
        mine = shared + rest[(a - 1) * args.per_annotator : a * args.per_annotator]
        rng.shuffle(mine)
        name = f"annotator_{a}"
        assignment[name] = [m["item_id"] for m in mine]
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel opens it as UTF-8
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            for m in mine:
                w.writerow({"item_id": m["item_id"], "question": m["question"], "gold_answer": m["gold_answer"],
                            "response": m["response"], "label": "", "notes": ""})
    key = {"source": str(args.questions), "shared_items": [m["item_id"] for m in shared], "assignment": assignment,
           "items": {m["item_id"]: {k: m[k] for k in ("judge_grade", "strategy", "conv", "category")} for m in items}}
    (out / "key.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"wrote {args.annotators} sheets ({args.shared} shared + {args.per_annotator} own items each) and key.json to {out}")
    print("Give each annotator ONLY their CSV and LABELLING_GUIDE.md; keep key.json private until scoring.")


if __name__ == "__main__":
    main()
