"""Naive single-prompt summarizer baseline (build guide 6.3 validation).

No structure, no tiers, no merge. Rule-based mode keeps the first sentence of each summarized
turn (newest first until the budget is full); LLM mode sends one "summarize the conversation"
prompt. Same raw tail and same loss / SRR scoring as the hierarchical engine, so the comparison
isolates structured output + contradiction merge.
"""

from __future__ import annotations

import time

from contracts import (
    LOSS_THRESHOLD,
    ConversationTurn,
    Readiness,
    StrategyModuleOutput,
    SummarizationQuality,
    TurnSignal,
    count_tokens,
)
from contracts.text import sentences

from . import prompts
from .generators import LLMCallable
from .loss import anchor_loss, symbol_retention_rate


class NaiveSummarizer:
    name = "summarization"

    def __init__(self, tail_keep: int = 4, llm: LLMCallable | None = None, max_words: int = 25):
        self.tail_keep = tail_keep
        self.llm = llm
        self.max_words = max_words
        self.turns: list[ConversationTurn] = []

    def observe_signal(self, signal: TurnSignal) -> None:
        pass

    def ingest(self, turn: ConversationTurn) -> None:
        self.turns.append(turn)

    def _summary(self, old: list[ConversationTurn], budget: int) -> str:
        if not old:
            return ""
        if self.llm is not None:
            convo = "\n".join(t.render() for t in old)
            return self.llm(prompts.NAIVE_SYSTEM, convo)
        lines: list[str] = []
        used = 0
        for t in reversed(old):
            sents = sentences(t.content)
            if not sents:
                continue
            first = " ".join(sents[0].split()[: self.max_words])
            line = f"{t.speaker or t.role}: {first}"
            tok = count_tokens(line) + 1
            if used + tok > budget:
                break
            lines.insert(0, line)
            used += tok
        return "Summary: " + " ".join(lines)

    def build_context(self, signal: TurnSignal, query: str) -> StrategyModuleOutput:
        t0 = time.perf_counter()
        budget = signal.token_usage.budget
        split = max(0, len(self.turns) - self.tail_keep)
        old, tail = self.turns[:split], self.turns[split:]
        tail_text = "\n".join(t.render() for t in tail)
        summary = self._summary(old, max(0, budget - count_tokens(tail_text) - 4))
        context = "\n\n".join(p for p in (summary, tail_text) if p)
        loss = round(anchor_loss(old, summary)[0], 4)
        srr = symbol_retention_rate(self.turns, context)
        return StrategyModuleOutput(
            module="summarization",
            candidate_context=context,
            readiness=Readiness(available=True, estimated_latency_ms=(time.perf_counter() - t0) * 1000),
            quality=SummarizationQuality(
                tier_emitted="L1",
                loss_score=loss,
                loss_threshold_exceeded=loss > LOSS_THRESHOLD,
                symbol_retention_rate=None if srr is None else round(srr, 4),
            ),
            token_count=count_tokens(context),
        )
