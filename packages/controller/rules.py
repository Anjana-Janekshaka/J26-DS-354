"""Rule table for the rule-based ASSE controller.

Inputs are ONLY the Tier 0/1 ``ControllerFeatureVector`` plus escalation events raised on
*earlier* turns (section 5). Rules are evaluated in order; each returns a strategy and a
human-readable reason. ``hard`` rules switch immediately; soft rules respect the minimum dwell
time (``time_since_last_switch``) to avoid flapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from pydantic import BaseModel, Field

from contracts import ControllerFeatureVector, EscalationEvent, SelectedStrategy


class RuleConfig(BaseModel):
    low_pressure: float = Field(default=0.6, ge=0.0, le=1.0)  # whole history (nearly) fits
    high_pressure: float = Field(default=0.9, ge=0.0, le=1.0)
    min_dwell_turns: int = Field(default=2, ge=0)
    # Strategy for long open-ended chat/exploration once the history no longer fits.
    long_chat_strategy: Literal["summarization", "hybrid", "rag"] = "summarization"
    # Where a summary-loss escalation (raised on the previous turn) sends a summarization choice.
    loss_escalation_target: Literal["rag", "hybrid"] = "rag"
    # Recall questions over budget: always RAG, always hybrid, or hybrid unless the conversation
    # manager flagged a topic shift (a question about the current topic keeps the recent window).
    qa_strategy: Literal["rag", "hybrid", "hybrid_unless_shift"] = "rag"


@dataclass
class RuleHit:
    rule: str
    strategy: SelectedStrategy
    reason: str
    hard: bool


# Rules see the Tier 0/1 feature vector plus one more pre-decision Tier 0 signal from the
# conversation manager's TurnSignal: whether this message was flagged as a topic shift.
Rule = Callable[[ControllerFeatureVector, RuleConfig, bool], RuleHit | None]


def _fits(fv: ControllerFeatureVector, cfg: RuleConfig, shift: bool = False) -> RuleHit | None:
    if fv.token_budget_pressure < cfg.low_pressure:
        return RuleHit(
            "history_fits",
            "sliding_window",
            f"token pressure {fv.token_budget_pressure:.2f} < {cfg.low_pressure:.2f}: full recent history fits, window is lossless",
            hard=False,
        )
    return None


def _qa(fv: ControllerFeatureVector, cfg: RuleConfig, shift: bool = False) -> RuleHit | None:
    if fv.task_type != "qa":
        return None
    mode = cfg.qa_strategy
    if mode == "hybrid_unless_shift":
        mode = "rag" if shift else "hybrid"
    if mode == "rag":
        why = " (topic shift detected)" if cfg.qa_strategy == "hybrid_unless_shift" else ""
        return RuleHit("recall_question", "rag", f"task_type=qa (recall of earlier facts){why} with history over budget -> RAG retrieves the specific turns", hard=True)
    return RuleHit("recall_question", "hybrid",
                   "task_type=qa on the current topic (no shift) with history over budget -> hybrid: recent window plus retrieved earlier turns", hard=True)


def _build(fv: ControllerFeatureVector, cfg: RuleConfig, shift: bool = False) -> RuleHit | None:
    if fv.task_type == "code_generation":
        return RuleHit(
            "build_request",
            "hybrid",
            "task_type=code_generation (build-request pattern) -> hybrid: recent window + RAG to surface existing definitions before writing new code",
            hard=True,
        )
    return None


def _refactor(fv: ControllerFeatureVector, cfg: RuleConfig, shift: bool = False) -> RuleHit | None:
    if fv.task_type == "code_refactor":
        return RuleHit(
            "refactor_request",
            "summarization",
            "task_type=code_refactor -> summarization: merged L1 symbol table carries current signatures and renames",
            hard=True,
        )
    return None


def _debug(fv: ControllerFeatureVector, cfg: RuleConfig, shift: bool = False) -> RuleHit | None:
    if fv.task_type == "debugging":
        return RuleHit("debugging", "sliding_window", "task_type=debugging -> sliding window: latest edits and traces are local and recent", hard=False)
    return None


_LONG_CHAT_REASON = {
    "summarization": "summarization keeps the gist of the long history",
    "hybrid": "hybrid keeps the recent window and retrieves related earlier turns",
    "rag": "RAG retrieves the earlier turns related to this message",
}


def _long_open(fv: ControllerFeatureVector, cfg: RuleConfig, shift: bool = False) -> RuleHit | None:
    if fv.task_type in ("chat", "exploration") and fv.token_budget_pressure >= cfg.low_pressure:
        s = cfg.long_chat_strategy
        return RuleHit(
            "long_open_conversation",
            s,
            f"task_type={fv.task_type} with token pressure {fv.token_budget_pressure:.2f} -> {_LONG_CHAT_REASON[s]}",
            hard=False,
        )
    return None


RULES: list[Rule] = [_fits, _qa, _build, _refactor, _debug, _long_open]


def apply_escalations(
    hit: RuleHit, events: list[EscalationEvent], cfg: RuleConfig | None = None
) -> tuple[SelectedStrategy, list[str]]:
    """Fold escalations from the previous turn into this turn's choice (never the turn that raised them)."""
    target = (cfg or RuleConfig()).loss_escalation_target
    strategy = hit.strategy
    notes: list[str] = []
    for ev in events:
        if ev.kind == "loss_threshold_exceeded" and strategy == "summarization":
            strategy = target
            notes.append(
                f"escalation from {ev.source_turn_id}: summary loss {ev.detail.get('loss_score', '?')} > 0.15 "
                f"(tier {ev.detail.get('tier_emitted', '?')}) -> switch summarization to {'RAG' if target == 'rag' else 'hybrid'}"
            )
        elif ev.kind == "contradiction_flagged" and strategy == "sliding_window":
            strategy = "hybrid"
            notes.append(
                f"escalation from {ev.source_turn_id}: {ev.detail.get('n_flags', '?')} stale chunk(s) flagged -> "
                "hybrid so the superseding facts are retrievable next to the recent window"
            )
        else:
            notes.append(f"escalation from {ev.source_turn_id} ({ev.kind}) noted; no change for {strategy}")
    return strategy, notes
