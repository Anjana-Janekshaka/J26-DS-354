import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from eval.human_agreement.score import cohen_kappa, fleiss_kappa

ROOT = Path(__file__).resolve().parents[1]
GRADES = ["CORRECT", "PARTIAL", "WRONG"]


def test_kappa_values():
    a = ["CORRECT", "WRONG", "PARTIAL", "CORRECT"]
    assert cohen_kappa(a, a) == pytest.approx(1.0)
    assert cohen_kappa(["CORRECT", "WRONG"] * 5, ["WRONG", "CORRECT"] * 5) < 0
    assert cohen_kappa(["CORRECT", "PARTIAL"], ["CORRECT", "WRONG"], weighted=True) > cohen_kappa(["CORRECT", "PARTIAL"], ["CORRECT", "WRONG"])
    assert fleiss_kappa([["CORRECT"] * 4, ["WRONG"] * 4, ["PARTIAL"] * 4]) == pytest.approx(1.0)


def test_make_and_score_sheets(tmp_path):
    rows = []
    for q in range(40):
        row = {"conv": "c", "category": 4, "question": f"Q{q}?", "gold_answer": f"gold {q}"}
        for k, s in enumerate(("adaptive", "rag", "sliding_window", "summarization", "hybrid")):
            row[s] = {"answer": f"answer {q}-{k}", "judge_grade": GRADES[(q + k) % 3]}
        rows.append(row)
    qfile = tmp_path / "questions.jsonl"
    qfile.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    sheets = tmp_path / "sheets"
    subprocess.run([sys.executable, "-m", "eval.human_agreement.make_sheets", "--questions", str(qfile), "--out", str(sheets)],
                   check=True, cwd=ROOT, capture_output=True)
    key = json.loads((sheets / "key.json").read_text(encoding="utf-8"))
    assert len(key["assignment"]) == 4 and len(key["shared_items"]) == 12
    header = (sheets / "annotator_1.csv").read_text(encoding="utf-8-sig").splitlines()[0]
    assert "judge" not in header and "strategy" not in header  # blind

    # Fill: annotators agree with the judge, using shorthand labels.
    for name in key["assignment"]:
        path = sheets / f"{name}.csv"
        with open(path, encoding="utf-8-sig", newline="") as f:
            data = list(csv.DictReader(f))
        for r in data:
            r["label"] = key["items"][r["item_id"]]["judge_grade"][0]
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    subprocess.run([sys.executable, "-m", "eval.human_agreement.score", "--sheets", str(sheets)], check=True, cwd=ROOT, capture_output=True)
    rep = json.loads((sheets / "agreement.json").read_text(encoding="utf-8"))
    assert rep["n_items_scored"] == 60
    assert rep["judge_vs_human"]["cohen_kappa"] == pytest.approx(1.0)
    assert rep["human_vs_human_fleiss_kappa_shared"] == pytest.approx(1.0)
    assert not rep["problems"]
