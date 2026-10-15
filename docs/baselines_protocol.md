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
