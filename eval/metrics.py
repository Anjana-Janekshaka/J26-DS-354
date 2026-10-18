"""Shared evaluation metrics (used by every harness so numbers are comparable)."""

from __future__ import annotations

import math
import re
import string
from collections import Counter

from contracts.text import content_words, normalize


def evidence_coverage(evidence_text: str, context: str) -> float:
    """Fraction of the evidence turn's content words present in the context (order-free)."""
    ev = set(content_words(evidence_text))
    if not ev:
        return 1.0
    ctx = set(content_words(context))
    return len(ev & ctx) / len(ev)


def evidence_hit(evidence_texts: list[str], context: str, threshold: float = 0.6) -> tuple[float, bool]:
    """(mean coverage over evidence turns, all evidence turns covered >= threshold)."""
    if not evidence_texts:
        return 1.0, True
    covs = [evidence_coverage(e, context) for e in evidence_texts]
    return sum(covs) / len(covs), all(c >= threshold for c in covs)


_ARTICLES = re.compile(r"\b(a|an|the|and)\b")


def normalize_answer(s: str) -> str:
    s = str(s).lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    return " ".join(_ARTICLES.sub(" ", s).split())


def answer_in_context(answer: str, context: str) -> bool:
    """All normalized answer tokens appear in the normalized context."""
    toks = normalize_answer(answer).split()
    if not toks:
        return False
    ctx = set(normalize_answer(context).split())
    return all(t in ctx for t in toks)


def token_f1(prediction: str, gold: str) -> float:
    p, g = normalize_answer(prediction).split(), normalize_answer(gold).split()
    common = Counter(p) & Counter(g)
    same = sum(common.values())
    if not p or not g or same == 0:
        return 0.0
    prec, rec = same / len(p), same / len(g)
    return 2 * prec * rec / (prec + rec)


def dcg(rels: list[float]) -> float:
    return sum(r / math.log2(i + 2) for i, r in enumerate(rels))


def ndcg_at_k(ranked_relevance: list[float], n_relevant_possible: int, k: int) -> float:
    ideal = dcg([1.0] * min(k, n_relevant_possible))
    return dcg(ranked_relevance[:k]) / ideal if ideal > 0 else 0.0


def macro_f1(gold: list[str], pred: list[str], labels: list[str] | None = None) -> tuple[float, dict[str, dict[str, float]]]:
    labels = labels or sorted(set(gold) | set(pred))
    per: dict[str, dict[str, float]] = {}
    for lab in labels:
        tp = sum(1 for g, p in zip(gold, pred) if g == lab and p == lab)
        fp = sum(1 for g, p in zip(gold, pred) if g != lab and p == lab)
        fn = sum(1 for g, p in zip(gold, pred) if g == lab and p != lab)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per[lab] = {"precision": prec, "recall": rec, "f1": f1, "support": sum(1 for g in gold if g == lab)}
    present = [lab for lab in labels if per[lab]["support"] > 0]
    return (sum(per[lab]["f1"] for lab in present) / len(present) if present else 0.0), per


def prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {"precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0, "tp": tp, "fp": fp, "fn": fn}


def brier(probs: list[float], labels: list[int]) -> float:
    return sum((p - y) ** 2 for p, y in zip(probs, labels)) / len(probs) if probs else 0.0


def expected_calibration_error(probs: list[float], labels: list[int], bins: int = 10) -> float:
    if not probs:
        return 0.0
    total = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i, p in enumerate(probs) if (lo <= p < hi) or (b == bins - 1 and p == 1.0)]
        if idx:
            conf = sum(probs[i] for i in idx) / len(idx)
            acc = sum(labels[i] for i in idx) / len(idx)
            total += len(idx) / len(probs) * abs(conf - acc)
    return total


def contains_normalized(needle: str, hay: str) -> bool:
    return normalize(needle) in normalize(hay)


ORACLE_PREFERENCE = ("sliding_window", "summarization", "rag", "hybrid")  # simplest / cheapest compute first


def oracle_label(hits: dict[str, bool], tokens: dict[str, int], budget: int) -> str:
    """Objective oracle: among strategies whose context satisfies the evidence requirement, the one
    with the smallest context, compared in 10%-of-budget buckets (differences below that are noise
    when every strategy fills the budget), ties broken by ``ORACLE_PREFERENCE``. 'none' if no hit."""
    ok = [s for s in ORACLE_PREFERENCE if hits.get(s)]
    if not ok:
        return "none"
    bucket = max(1, budget // 10)
    return min(ok, key=lambda s: (tokens[s] // bucket, ORACLE_PREFERENCE.index(s)))


STALE_MARKERS = ("[!] stale", "supersedes", "superseded", "retired")


def required_hit(context: str, required: list[str], stale: list[str] | None = None) -> bool:
    """All ``required`` strings present, and every ``stale`` string that appears is marked stale
    on its line (or its block carries a stale flag). Objective, no judge involved."""
    if not all(contains_normalized(r, context) for r in required):
        return False
    for s in stale or []:
        for block in context.split("\n\n---\n\n"):
            block_flagged = "[!] stale" in block
            lines = block.splitlines()
            for i, line in enumerate(lines):
                if contains_normalized(s, line):
                    section = next((l for l in reversed(lines[:i]) if l.rstrip().endswith(":") and not l.startswith("-")), "")
                    marked = block_flagged or any(m in line.lower() for m in STALE_MARKERS) or "retired" in section.lower()
                    if not marked:
                        return False
    return True


def cluster_bootstrap_ci(rows: list[dict], stat, group_key: str = "conv", n_boot: int = 2000, seed: int = 0,
                         alpha: float = 0.05) -> dict[str, float]:
    """Percentile bootstrap CI that resamples whole groups (conversations), not single rows.

    Probes from one conversation share history, so they are not independent; resampling them
    one by one would give intervals that are too narrow. ``stat`` maps a list of rows to a float.
    """
    import random
    from collections import defaultdict

    groups: dict = defaultdict(list)
    for r in rows:
        groups[r[group_key]].append(r)
    keys = sorted(groups)
    est = stat(rows)
    if len(keys) < 2:
        return {"estimate": est, "ci_low": est, "ci_high": est, "n_groups": len(keys)}
    rng = random.Random(seed)
    vals = sorted(stat([r for k in (rng.choice(keys) for _ in keys) for r in groups[k]]) for _ in range(n_boot))
    lo = vals[int(alpha / 2 * n_boot)]
    hi = vals[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return {"estimate": est, "ci_low": lo, "ci_high": hi, "n_groups": len(keys)}
