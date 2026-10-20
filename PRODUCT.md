# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Presentation panel** (primary moment: Progress Presentation 1, Wednesday 2026-10-21). Examiners watch the chat live on a projector and need to see, in seconds, which memory method Syno picked for each message and why.
- **Everyday users** of the chat after the presentation: people chatting with an assistant (mostly about code) who should not have to understand memory internals to use it.

## Product Purpose

Syno is adaptive memory middleware for multi-turn LLM chat. The chat app (`console/chat.html`, served by `console/chat.py`) is a normal AI chat where Syno manages the memory. Success: a person chats as usual, and every reply shows, at a glance, which memory method was used and which earlier messages it drew on, with the full reason one click away.

## Positioning

Per-turn switching between three memory paradigms (recent messages / sliding window, hierarchical summary, search / RAG, plus recent + search), with a logged, explainable, human-overridable decision and no LLM in the decision path. Other memory systems lock in one strategy.

## Operating Context

- Run locally with `python -m console.chat` (127.0.0.1:8800); single user, one conversation.
- Replies come from Ollama on the laptop (slow, about a minute), a hosted OpenAI-compatible API (fast), or nothing (memory-only mode: no answer, but the memory decision still shows).
- "Load a sample conversation" replays 15 messages of the coding demo so traps can be tried live.
- Shown on a projector and on a laptop, in light or dark.

## Capabilities and Constraints

- API: `GET /api/state`, `POST /api/send {text, memory}`, `/api/new`, `/api/sample`, `/api/connect`. Each assistant message carries `memory` (strategy, chosen_by, reason, notes, drew_on, tokens, budget, fill, context, rationale, ms), `ai_error`, `memory_only`.
- Per-message manual override: the user can pick a method for one message; it resets to Automatic afterwards.
- The page is a single HTML file read by `chat.py`; no build step, no external network dependency required at runtime.
- Terminology: "Recent messages", "Summary", "Search", "Recent + search", "Automatic".

## Evidence on Hand

- Real demo conversation: `demo/coding_session/script.py` (via `/api/sample`).
- Results in `results/RESULTS.md`; nothing in the chat UI may invent numbers or claims.

## Product Principles

1. The chat comes first; memory is visible but never in the way.
2. Every memory decision is explainable in plain words, with the raw context available.
3. The human can override, and the UI makes that obvious and reversible.
4. Credible research tool, not a product pitch: no hype, no gimmicks.

## Accessibility & Inclusion

Must read well on a projector (contrast, size) and work in both light and dark themes; keyboard operable.
