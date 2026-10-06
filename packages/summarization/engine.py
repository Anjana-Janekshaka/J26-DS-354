"""Hierarchical Summarization Engine (L1 / L2 / L3) as a strategy module.

Turns older than the raw tail are rolled into L1 records every ``l1_span`` turns; each new L1's
facts go through the contradiction-resolving merge. Every ``l2_fanin`` L1 records roll into an L2
record, and the single L3 profile is rebuilt from all L2s. At query time the most detailed tier
whose rendering fits the budget (after the raw tail) is emitted, and the anchor-recall loss score
is computed on the background worker.
"""

from __future__ import annotations

import time
from concurrent.futures import TimeoutError as FutureTimeout

from pydantic import BaseModel, Field

from contracts import (
    LOSS_THRESHOLD,
    ConversationTurn,
    Readiness,
    StrategyModuleOutput,
    SummarizationQuality,
    TurnSignal,
    count_tokens,
)

from .extract import extract_facts
from .generators import RuleBasedGenerator, TierGenerator
from .loss import LossWorker, anchor_loss, symbol_retention_rate
from .merge import SummaryState
from .records import L1Record, L2Record, L3Record


class SummarizationConfig(BaseModel):
    l1_span: int = Field(default=6, ge=1)
    tail_keep: int = Field(default=4, ge=0)
    l2_fanin: int = Field(default=3, ge=1)
    loss_timeout_s: float | None = None  # None: wait for the worker (deterministic)
    merge_contradictions: bool = True  # False only for the ablation: every fact kept, nothing superseded


_SECTION_ORDER = [
    ("code_signature", "Code symbols (current)"),
    ("rename", "Renames"),
    ("attribute", "Attributes & settings"),
    ("constraint", "Constraints"),
    ("decision", "Decisions"),
    ("request", "Open requests"),
    ("statement", "Facts"),
]


class HierarchicalSummarizer:
    name = "summarization"

    def __init__(self, generator: TierGenerator | None = None, config: SummarizationConfig | None = None):
        self.generator = generator or RuleBasedGenerator()
        self.config = config or SummarizationConfig()
        self.turns: list[ConversationTurn] = []
        self.summarized: list[ConversationTurn] = []
        self.unsummarized: list[ConversationTurn] = []
        self.l1: list[L1Record] = []
        self.l2: list[L2Record] = []
        self.l3: L3Record | None = None
        self.state = SummaryState()
        self.worker = LossWorker(anchor_loss)
        self._fact_seq = [0]
        self._l1_in_l2 = 0
        self._latency_ema_ms = 1.0
        self._provisional: dict[tuple[str, ...], L2Record] = {}

    # ------------------------------------------------------------------ ingestion
    def observe_signal(self, signal: TurnSignal) -> None:
        pass

    def ingest(self, turn: ConversationTurn) -> None:
        self.turns.append(turn)
        self.unsummarized.append(turn)
        cfg = self.config
        if cfg.merge_contradictions:
            # Keyed facts merge eagerly, per turn, so a change that is still in the raw tail already
            # supersedes the old value in every tier. The batched L1 record re-applies them later as
            # a no-op restatement.
            facts, _ = extract_facts(turn, self._fact_seq)
            for fact in facts:
                if fact.kind in ("code_signature", "rename", "attribute"):
                    self.state.apply(fact)
        while len(self.unsummarized) >= cfg.tail_keep + cfg.l1_span:
            chunk = self.unsummarized[: cfg.l1_span]
            self.unsummarized = self.unsummarized[cfg.l1_span :]
            rec = self.generator.l1(f"L1-{len(self.l1) + 1:04d}", chunk, self._fact_seq)
            self.l1.append(rec)
            for fact in rec.facts:
                if not cfg.merge_contradictions:
                    fact = fact.model_copy(update={"key": f"{fact.key}#{fact.fact_id}"})
                self.state.apply(fact)
            self.summarized.extend(chunk)
            if len(self.l1) - self._l1_in_l2 >= cfg.l2_fanin:
                group = self.l1[self._l1_in_l2 : self._l1_in_l2 + cfg.l2_fanin]
                self.l2.append(self.generator.l2(f"L2-{len(self.l2) + 1:04d}", group))
                self._l1_in_l2 += cfg.l2_fanin
                self.l3 = self.generator.l3("L3-current", self.l2, self.state.attributes())

    # ------------------------------------------------------------------ rendering
    def render_l1(self) -> str:
        if not self.l1:
            return ""
        lines = [f"[Memory summary | tier L1 | verbatim facts, merged | covers {self.l1[0].turn_range[0]}-{self.l1[-1].turn_range[1]}]"]
        by_kind: dict[str, list] = {}
        for fact in self.state.active.values():
            by_kind.setdefault(fact.kind, []).append(fact)
        for kind, title in _SECTION_ORDER:
            facts = sorted(by_kind.get(kind, []), key=lambda f: f.source_turn_id)
            if not facts:
                continue
            lines.append(f"{title}:")
            for f in facts:
                if kind == "rename":
                    old = f.key.split(":")[-1]
                    entry = f"- {old} -> {f.value.split('->')[-1].strip()} ({f.source_turn_id})"
                elif kind in ("code_signature", "attribute"):
                    label = "" if kind == "code_signature" else f"{f.key}: "
                    entry = f"- {label}{f.value} ({f.source_turn_id}"
                    olds = self.state.superseded_for(f.key)
                    if olds:
                        entry += "; supersedes " + ", ".join(f'"{o.value}" from {o.source_turn_id}' for o in olds[-2:])
                    entry += ")"
                else:
                    entry = f"- {f.value} ({f.source_turn_id})"
                lines.append(entry)
        # Symbols retired by a rename stay visible, marked, so the old name is never used again.
        renamed = [o for o in self.state.superseded if o.kind == "code_signature" and o.key not in self.state.active]
        if renamed:
            lines.append("Retired symbols (do not use):")
            lines += [f"- {o.value} ({o.source_turn_id}; superseded by {o.superseded_by})" for o in renamed]
        return "\n".join(lines)

    def _l2_records(self) -> list[L2Record]:
        records = list(self.l2)
        pending = self.l1[self._l1_in_l2 :]
        if pending:
            key = tuple(r.record_id for r in pending)
            if key not in self._provisional:
                self._provisional = {key: self.generator.l2(f"L2-provisional-{key[0]}", pending)}
            records.append(self._provisional[key])
        return records

    def _l3_record(self, l2s: list[L2Record]) -> L3Record | None:
        if self.l3 is not None and len(l2s) == len(self.l2):
            return self.l3
        return self.generator.l3("L3-current", l2s, self.state.attributes()) if l2s else None

    def _annotate_superseded(self, line: str) -> str:
        """Apply the merge across tiers: L2/L3 records are immutable history written before later
        changes, so any value they mention that has since been superseded is marked at render time."""
        low = line.lower()
        notes = []
        for old in self.state.superseded:
            if old.kind not in ("attribute", "code_signature") or old.value.lower() not in low:
                continue
            current = self.state.active.get(old.key)
            if current is not None and current.value.lower() in low:
                continue
            notes.append(f'"{old.value}" superseded' + (f' by "{current.value}"' if current is not None else ""))
        return line + (f" [{'; '.join(notes)}]" if notes else "")

    def _render_l3_text(self, l3: L3Record | None) -> str:
        if l3 is None:
            return ""
        return "\n".join(
            self._annotate_superseded(x)
            for x in (f"Profile (L3): {l3.persona}", f"Objective: {l3.main_objective}", f"Current state: {l3.final_state}")
        )

    def render_l2(self) -> str:
        l2s = self._l2_records()
        if not l2s:
            return ""
        lines = [f"[Memory summary | tier L2 | intent & decisions | {len(l2s)} records]"]
        l3 = self._render_l3_text(self._l3_record(l2s))
        if l3:
            lines.append(l3)
        for r in l2s:
            lines.append(self._annotate_superseded(f"- {r.intent}"))
            if r.decisions:
                lines.append("  decisions: " + "; ".join(self._annotate_superseded(d) for d in r.decisions))
            if r.open_goals:
                lines.append("  open goals: " + "; ".join(self._annotate_superseded(g) for g in r.open_goals))
        return "\n".join(lines)

    def render_l3(self) -> str:
        l3 = self._l3_record(self._l2_records())
        return "[Memory summary | tier L3 | profile]\n" + self._render_l3_text(l3) if l3 else ""

    def _fill_with_recent_facts(self, summary: str, remaining: int) -> str:
        """When a coarser tier was emitted, spend the leftover budget on the newest active L1 facts
        (verbatim, merged) instead of leaving it empty. ``tier_emitted`` still reports the main tier."""
        spare = remaining - count_tokens(summary) - 10
        lines: list[str] = []
        keyed_first = {"code_signature": 0, "rename": 0, "attribute": 0, "constraint": 1, "decision": 1}
        ordered = sorted(self.state.active.values(), key=lambda f: f.source_turn_id, reverse=True)
        for f in sorted(ordered, key=lambda f: keyed_first.get(f.kind, 2)):
            line = f"- {f.value} ({f.source_turn_id})"
            tok = count_tokens(line) + 1
            if tok > spare:
                continue
            lines.append(line)
            spare -= tok
        return summary + ("\nRecent facts (L1, newest first):\n" + "\n".join(lines) if lines else "")

    # ------------------------------------------------------------------ StrategyModule
    def build_context(self, signal: TurnSignal, query: str) -> StrategyModuleOutput:
        t0 = time.perf_counter()
        budget = signal.token_usage.budget
        tail: list[ConversationTurn] = []
        tail_tokens = 0
        for t in reversed(self.unsummarized):
            tok = count_tokens(t.render())
            if tail_tokens + tok > budget:
                break
            tail.insert(0, t)
            tail_tokens += tok
        tail_text = "\n".join(t.render() for t in tail)
        remaining = budget - tail_tokens - (2 if tail else 0)

        tier, summary = "L1", ""
        if self.l1:
            for tier, render in (("L1", self.render_l1), ("L2", self.render_l2), ("L3", self.render_l3)):
                summary = render()
                if count_tokens(summary) <= remaining:
                    break
            else:
                summary = _truncate_to_tokens(summary, max(0, remaining))
            if tier != "L1":
                summary = self._fill_with_recent_facts(summary, remaining)

        context ="\n\n".join(p for p in (summary, ("[Recent turns]\n" + tail_text) if tail_text else "") if p)

        source = self.summarized
        fut = self.worker.submit(source, summary)
        try:
            loss = fut.result(timeout=self.config.loss_timeout_s)[0]
        except FutureTimeout:
            loss = self.worker.last_score if self.worker.last_score is not None else anchor_loss(source, summary)[0]
        loss = round(float(loss), 4)
        srr = symbol_retention_rate(self.turns, context)

        elapsed = (time.perf_counter() - t0) * 1000
        self._latency_ema_ms = 0.8 * self._latency_ema_ms + 0.2 * elapsed
        return StrategyModuleOutput(
            module="summarization",
            candidate_context=context,
            readiness=Readiness(available=True, estimated_latency_ms=round(self._latency_ema_ms, 3)),
            quality=SummarizationQuality(
                tier_emitted=tier,  # type: ignore[arg-type]
                loss_score=loss,
                loss_threshold_exceeded=loss > LOSS_THRESHOLD,
                symbol_retention_rate=None if srr is None else round(srr, 4),
            ),
            token_count=count_tokens(context),
        )


def _truncate_to_tokens(text: str, max_tokens: int) -> str:
    if max_tokens <= 0:
        return ""
    lines = text.splitlines()
    out: list[str] = []
    used = 0
    for line in lines:
        tok = count_tokens(line) + 1
        if used + tok > max_tokens:
            break
        out.append(line)
        used += tok
    return "\n".join(out)
