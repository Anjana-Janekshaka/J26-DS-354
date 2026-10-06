"""LLM Interface: assembles the final prompt from the selected strategy's module output(s).

``hybrid`` = retrieved RAG blocks (up to half the budget, de-duplicated against the window)
followed by the sliding window's most recent selected turns.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from contracts import ControllerDecision, ConversationTurn, StrategyModuleOutput, count_tokens
from contracts.text import BLOCK_TURNS, CONTEXT_BLOCK_SEPARATOR

SYSTEM_PROMPT = (
    "You are a coding and conversation assistant. A memory middleware selected the context below "
    "from earlier in this conversation. Prefer facts marked as current; never use anything marked "
    "stale/superseded/retired. If the context already contains a definition you are asked to write, reuse it."
)


@dataclass
class AssembledPrompt:
    strategy: str
    system: str
    context: str
    user: str
    token_count: int
    sources: dict[str, list[str]] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return f"{self.system}\n\n[Memory context]\n{self.context}\n\n[Current message]\n{self.user}"


def _hybrid(window: StrategyModuleOutput, rag: StrategyModuleOutput, budget: int) -> tuple[str, dict[str, list[str]]]:
    turns: list[ConversationTurn] = window.candidate_context if isinstance(window.candidate_context, list) else []
    rag_text = rag.context_text()
    blocks = [b for b in rag_text.split(CONTEXT_BLOCK_SEPARATOR) if b.strip()] if rag_text else []

    recent_ids = {t.turn_id for t in turns[-4:]}
    chosen_blocks: list[str] = []
    covered: set[str] = set()
    used = 0
    for b in blocks:
        m = BLOCK_TURNS.search(b)
        ids = set(m.group(1).split()) if m else set()
        if ids and ids <= recent_ids:
            continue  # the window will carry these turns anyway
        tok = count_tokens(b) + 4
        if used + tok > budget // 2:
            continue
        chosen_blocks.append(b)
        covered |= ids
        used += tok

    window_turns: list[ConversationTurn] = []
    for t in reversed(turns):
        if t.turn_id in covered:
            continue
        tok = count_tokens(t.render()) + 1
        if used + tok > budget:
            break
        window_turns.insert(0, t)
        used += tok

    parts = []
    if chosen_blocks:
        parts.append("[Retrieved memory]\n" + CONTEXT_BLOCK_SEPARATOR.join(chosen_blocks))
    if window_turns:
        parts.append("[Recent turns]\n" + "\n".join(t.render() for t in window_turns))
    return "\n\n".join(parts), {"rag_blocks": [b.splitlines()[0] for b in chosen_blocks], "window_turns": [t.turn_id for t in window_turns]}


def assemble_prompt(
    decision: ControllerDecision, outputs: dict[str, StrategyModuleOutput], user_message: str, budget: int
) -> AssembledPrompt:
    s = decision.selected_strategy
    if s == "hybrid":
        context, sources = _hybrid(outputs["sliding_window"], outputs["rag"], budget)
    else:
        out = outputs[s]
        context = out.context_text()
        sources = {s: out.quality.selected_turn_ids if s == "sliding_window" else []}  # type: ignore[union-attr]
        if s == "rag":
            sources = {"rag": list(out.quality.retrieved_chunk_ids)}  # type: ignore[union-attr]
        elif s == "summarization":
            sources = {"summarization": [out.quality.tier_emitted]}  # type: ignore[union-attr]
    return AssembledPrompt(
        strategy=s,
        system=SYSTEM_PROMPT,
        context=context,
        user=user_message,
        token_count=count_tokens(context),
        sources=sources,
    )
