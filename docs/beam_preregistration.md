# Pre-registration: BEAM as an independent benchmark (roadmap 4.1)

Committed **before** any system run on BEAM. BEAM is never used for tuning.

## Why

The controller's largest gain (+0.112) is on our own synthetic set. BEAM ("Beyond a Million Tokens",
arXiv 2510.27246; [dataset](https://huggingface.co/datasets/Mohammadta/BEAM), CC BY-SA 4.0) was
built by others. Its long conversations mix coding projects and general topics, and it has explicit
*knowledge update* and *contradiction resolution* question types.

## Data

- **The 100K split, all 20 conversations** (about 190 turns each, mostly long coding answers).
- 20 probing questions per conversation, 2 per category: abstention, contradiction resolution,
  event ordering, information extraction, instruction following, knowledge update, multi-session
  reasoning, preference following, summarization and temporal reasoning.
- Downloaded with `python -m eval.beam.download` (Hugging Face dataset-viewer API) into
  `eval/beam/data/`. The data is not committed; the licence asks for attribution.

## Protocol

- **System:** the frozen system (`CEAI_SYSTEM=frozen`), budget 1,024 tokens, reranker on with the
  code-task skip, NLI off (as in the frozen LoCoMo runs).
- **Ingestion:** every chat message is ingested in order (user and assistant), with the
  `->-> s,t` index markers stripped.
- **Probes:** each probing question is asked after the full conversation, as a non-committing
  probe. For every probe, the contexts of all four fixed strategies and of adaptive are built from
  the same module outputs, exactly as in `eval/locomo/run.py`.
- **Metrics (deterministic, no LLM):**
  1. **Evidence hit**, for questions that cite source turns (`source_chat_ids` or
     `conversation_references` of the form `chat_id: N`). Every cited turn must have at least 60%
     of its content words in the context, the same rule as LoCoMo.
  2. **Answer in context**, for questions with a short gold `answer` (at most 25 words). All the
     answer's content words must be in the context.
  - Questions with neither (abstention, instruction following, preference following, most
    summarization) are counted but not scored.
- **Report:**
  - Both metrics per strategy and for adaptive.
  - Adaptive minus the best single fixed strategy and minus always-hybrid, with conversation-level
    95% bootstrap CIs.
  - The same per category, and the controller's choice distribution.

## Reporting rule

- Reported whatever the sign, next to the LoCoMo result.
- **Expectation, stated in advance:** like LoCoMo, every BEAM question is asked at the end of the
  conversation, so the right choice is mostly RAG, and a tie with RAG is the likely outcome. BEAM
  tests whether the frozen system generalises to someone else's conversations without loss. It does
  not test switching inside a conversation.

## Outcome (run once, 2026-10-17; `results/final/beam/summary.json`)

**A negative result: adaptive is significantly below always-RAG on BEAM.**

| Metric | Window | Summarization | RAG | Hybrid | **Adaptive** | Adaptive − RAG | Adaptive − hybrid |
|---|---|---|---|---|---|---|---|
| Evidence hit (355 questions) | 0.087 | 0.023 | **0.445** | 0.389 | 0.346 | **−0.099 [−0.135, −0.065]** | −0.042 [−0.087, −0.003] |
| Answer in context (117) | 0.120 | 0.026 | **0.350** | 0.308 | 0.248 | **−0.103 [−0.161, −0.054]** | −0.060 [−0.118, +0.000] |

**Why (diagnosed after the run, not tuned):**

- The task classifier marks 255 of the 400 probes as `qa`. Adaptive routes those to RAG and equals it.
- The other 142 are phrased as requests or statements ("Can you list the order in which I…",
  "Could you show me how to…"). They are classified as `chat` or `exploration`, and the
  long-conversation rule sends them to **summarization**.
  - On those probes adaptive's evidence hit is **0.03**, against 0.28 for RAG.
- This is the same failure mode as LoCoMo-Plus (statement-style triggers routed to summarization).
  It is now confirmed on an independent dataset.

**What it means for the claims:**

- "No regret when one strategy is right" holds only when the task classifier recognises a recall
  request. On someone else's phrasing it does not hold for about a third of the probes.
- The fix candidate is a routing change: recall-style requests over budget go to RAG or hybrid,
  whatever the phrasing. That would be new work, pre-registered and chosen on dev sets, and BEAM
  stays untouched as a test.
