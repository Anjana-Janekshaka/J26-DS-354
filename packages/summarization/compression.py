"""Compression-ratio accounting per tier.

Proposal targets (token *reduction*): L1 30-50%, L2 60-80%, L3 >= 90%. For every record we keep the
tokens of its direct input, of its own rendering, and of the raw turns it ultimately covers, so the
ratio can be read against either basis. The accounting never changes what is generated; it only
measures it (budget-driven generation to hit the targets is a separate, later step).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from contracts import count_tokens

from .records import L1Record, L2Record, L3Record

TARGETS: dict[str, tuple[float, float]] = {"L1": (0.30, 0.50), "L2": (0.60, 0.80), "L3": (0.90, 1.00)}


def l1_text(rec: L1Record) -> str:
    return "\n".join(f"- {f.value} ({f.source_turn_id})" for f in rec.facts)


def l2_text(rec: L2Record) -> str:
    return "\n".join([rec.intent, *rec.decisions, *rec.open_goals])


def l3_text(rec: L3Record) -> str:
    return "\n".join([rec.persona, rec.main_objective, rec.final_state])


@dataclass(frozen=True)
class TierStat:
    record_id: str
    tier: str
    tokens_in: int  # direct input: raw turns (L1), its L1 renderings (L2), its L2 renderings (L3)
    tokens_out: int  # the record's own rendering
    tokens_raw: int  # raw conversation tokens the record ultimately covers

    @property
    def ratio_vs_input(self) -> float:
        return 1.0 - self.tokens_out / self.tokens_in if self.tokens_in else 0.0

    @property
    def ratio_vs_raw(self) -> float:
        return 1.0 - self.tokens_out / self.tokens_raw if self.tokens_raw else 0.0


def l1_stat(rec: L1Record, raw_tokens: int) -> TierStat:
    return TierStat(rec.record_id, "L1", raw_tokens, count_tokens(l1_text(rec)), raw_tokens)


def l2_stat(rec: L2Record, inputs: list[TierStat]) -> TierStat:
    return TierStat(
        rec.record_id, "L2", sum(s.tokens_out for s in inputs), count_tokens(l2_text(rec)), sum(s.tokens_raw for s in inputs)
    )


def l3_stat(rec: L3Record, inputs: list[TierStat]) -> TierStat:
    return TierStat(
        rec.record_id, "L3", sum(s.tokens_out for s in inputs), count_tokens(l3_text(rec)), sum(s.tokens_raw for s in inputs)
    )


def _in_range(tier: str, ratio: float) -> bool:
    lo, hi = TARGETS[tier]
    return lo <= ratio <= hi


def build_report(stats: list[TierStat]) -> dict:
    """Per-tier token-weighted ratios plus every record, with a pass/fail against ``TARGETS``."""
    tiers: dict[str, dict] = {}
    for tier in ("L1", "L2", "L3"):
        rows = [s for s in stats if s.tier == tier]
        if not rows:
            tiers[tier] = {"n": 0}
            continue
        t_in, t_out, t_raw = (sum(getattr(s, k) for s in rows) for k in ("tokens_in", "tokens_out", "tokens_raw"))
        vs_input = 1.0 - t_out / t_in if t_in else 0.0
        vs_raw = 1.0 - t_out / t_raw if t_raw else 0.0
        tiers[tier] = {
            "n": len(rows),
            "tokens_in": t_in,
            "tokens_out": t_out,
            "tokens_raw": t_raw,
            "ratio_vs_input": round(vs_input, 4),
            "ratio_vs_raw": round(vs_raw, 4),
            "target": list(TARGETS[tier]),
            "in_target_vs_input": _in_range(tier, vs_input),
            "in_target_vs_raw": _in_range(tier, vs_raw),
        }
    return {
        "targets": {k: list(v) for k, v in TARGETS.items()},
        "tiers": tiers,
        "records": [
            {**asdict(s), "ratio_vs_input": round(s.ratio_vs_input, 4), "ratio_vs_raw": round(s.ratio_vs_raw, 4)} for s in stats
        ],
    }
