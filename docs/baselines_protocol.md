# Protocol: external memory baselines (written 2026-10-15, before any baseline was run)

This compares CEAI's frozen system with other memory approaches **inside our own harness, under
identical conditions**. It does not compare against numbers copied from other papers
(CLAUDE.md §12.4). The settings below were fixed before running and are not tuned afterwards.

## Shared conditions (identical for every system)

- **Questions:** LoCoMo **test** split (conversations 2, 4, 6, 8, 10). The same random sample as
  CEAI's frozen answer-accuracy run: 60 questions per conversation, seed 0, keeping answerable
  questions only (category 5 excluded), about 230 questions.
- **Turn rendering:** `[session date] speaker: text`, the same as CEAI.
- **Answering:** `qwen2.5:7b-instruct` (Ollama, temperature 0), with CEAI's answer prompt
  (`eval/locomo/run.py: QA_SYSTEM`) and the same `[Memory context] … Question:` format.
- **Grading:** `qwen2.5:7b-instruct` as judge with `eval/judge.py` (correct 1 / partial 0.5 / wrong 0),
  plus token-F1. Judge scores are citable only after the human-agreement check.
- **Memory budget:** 1,024 tokens of memory context for every memory system (cl100k token count),
  the same as CEAI. The exception is full context, which is a ceiling.
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` for every system that embeds.

## Systems

| System | What it is | Settings (fixed in advance) |
|---|---|---|
| **CEAI (frozen)** | The frozen configuration's answers from the 2026-10-15 test run (`final/locomo_qa`), on the same questions | As frozen; not re-run |
| **Fixed-chunk RAG** | The standard RAG baseline in the Mem0 paper: the whole conversation split into fixed-size chunks, top chunks by cosine similarity | 256-token chunks (whole turns, no splitting mid-turn); top chunks fill the 1,024-token budget, most relevant first |
| **Summary buffer** | LangChain's `ConversationSummaryBufferMemory` approach: recent turns kept verbatim, older turns folded into a running LLM summary | Buffer 600 tokens; when it is exceeded, the oldest turns are folded into the summary until the buffer is at 300 tokens. That is a batched prune, to keep LLM calls feasible, and a documented deviation from LangChain's per-message prune. Summary capped at about 250 words. Context = summary + buffer, truncated to the budget |
| **Mem0** | The `mem0ai` open-source library (version recorded at run time) with Ollama `qwen2.5:7b-instruct`, the MiniLM embedder and a FAISS store | One `add()` per session per speaker. Each speaker gets their own memory scope (as in the Mem0 paper), with their own turns as `user` and the other speaker as `assistant`; the session date is prefixed to every message. Search both scopes; memories ranked by score fill the budget |
| **Full context** | The whole conversation in the prompt: the ceiling reported in the Mem0 paper | No budget; Ollama context 32,768; first 12 sampled questions per conversation (a subset, for runtime) |

## Reported

- For each system: mean judge score with a 95% bootstrap interval over conversations, token-F1,
  mean memory-context tokens, and read latency per question.
- **Paired differences CEAI − system** on identical questions. For full context this is on its
  12-per-conversation subset.
- **Write-time cost:** LLM calls made while storing the conversation, and storage time. For CEAI
  this is 0 LLM calls: its summarizer is rule-based and its NLI check is not an LLM.
- **Every result is reported whatever its sign.** If a system fails to run (for example a Mem0
  JSON-mode failure with a 7B model), that is reported as a failure, not dropped.

## Outcome, run 1 (2026-10-16, Colab T4)

Results are in `results/final/baselines/` (summary, per-question rows, write costs). There are 230
questions; full context uses its 60-question subset.

| System | Judge score [95% CI] | CEAI − system [95% CI] | Token-F1 | Write-time LLM calls / conversation |
|---|---|---|---|---|
| **CEAI (frozen)** | **0.507** | — | 0.406 | **0** |
| Fixed-chunk RAG | 0.433 [0.381, 0.483] | **+0.074 [+0.017, +0.132]** | 0.343 | 0 |
| Mem0 (`mem0ai` 2.2.1) | 0.376 [0.342, 0.404] | **+0.130 [+0.036, +0.217]** | 0.191 | 54 (about 15 min per conversation) |
| Summary buffer | 0.096 [0.051, 0.140] | **+0.411 [+0.310, +0.494]** | 0.066 | 69 (about 12 min per conversation) |
| Full context (60 questions) | 0.417 | −0.067 [−0.183, +0.050] (not significant) | 0.195 | 0, but about 24k tokens per question |

**Caveat for Mem0:** 24 of its 272 extraction calls (8.8%) produced JSON cut off at the 1,500-token
output limit this harness set (`max_tokens`). The memories from those sessions were lost, which
handicaps Mem0. A corrected Mem0 run with `max_tokens` 8,000 is the fair comparison. Until it
exists, the Mem0 row must carry this caveat.

## Amendment: corrected Mem0 run (declared 2026-10-16, before running)

**Why:** in run 1, 8.8% of Mem0's extraction calls were cut off by this harness's own output limit,
which handicapped the baseline. The correction can only help Mem0, so it makes the comparison
stricter for CEAI.

**Change:**
- Mem0's `max_tokens` (Ollama `num_predict`) is raised from 1,500 to **8,000**.
- The Ollama server runs with a **16,384-token context** and one parallel slot, so the extraction
  prompt plus up to 8,000 output tokens fit.

**Unchanged:** everything else, including the questions, the answering model, the judge, the
1,024-token budget, the two speaker scopes and per-session `add()`.

**Reporting:** results go to `results/final/baselines_mem0_fixed/` and are reported **next to**
run 1, whatever the result. Run 1 is kept as it is.

- The corrected run **replaces run 1's Mem0 row** as the headline comparison.
- If extraction failures remain, their count is reported.
