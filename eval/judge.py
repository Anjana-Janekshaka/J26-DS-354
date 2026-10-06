"""LLM-as-judge answer grading (correct = 1, partial = 0.5, wrong = 0), the scheme LoCoMo-Plus uses.

The judge sees the question, the gold answer and the model's answer - never the strategy that
produced it. Its labels are only citable together with the human-agreement check in
``eval/human_agreement`` (judge vs. annotators, Cohen's kappa).
"""

from __future__ import annotations

import re

JUDGE_SYSTEM = (
    "You grade answers to questions about a long conversation. Compare the RESPONSE with the GOLD answer.\n"
    "CORRECT: the response states the same fact as the gold answer (wording, date format or extra harmless detail may differ).\n"
    "PARTIAL: the response contains part of the gold answer, or is correct but vaguer.\n"
    "WRONG: the response contradicts the gold answer, misses it, or says it does not know.\n"
    "Reply with exactly one word: CORRECT, PARTIAL or WRONG."
)
GRADES = {"CORRECT": 1.0, "PARTIAL": 0.5, "WRONG": 0.0}
_WORD = re.compile(r"\b(CORRECT|PARTIAL|WRONG)\b")


def judge_prompt(question: str, gold: str, response: str) -> str:
    return f"QUESTION: {question}\nGOLD: {gold}\nRESPONSE: {response}\n\nGrade:"


def parse_grade(text: str) -> str | None:
    m = _WORD.search(text.upper())
    return m.group(1) if m else None


def grade(judge, question: str, gold: str, response: str) -> str | None:
    return parse_grade(judge(JUDGE_SYSTEM, judge_prompt(question, gold, response)))
