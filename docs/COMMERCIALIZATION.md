# CEAI: commercialization and user benefits

## 1. The problem people pay for today

Every LLM application with long conversations has to decide what the model remembers. Today a
developer either:

- **sends the whole history**, which is expensive and eventually overflows the context window;
- **keeps a fixed recent window**, which forgets earlier facts and code; or
- **buys a memory service** (Mem0, Zep, Letta). These run an LLM on every write to extract
  memories, so memory itself becomes a second LLM bill and a second source of latency.

## 2. What CEAI offers instead (measured, not projected)

| Benefit | Evidence |
|---|---|
| **No LLM bill for memory.** Memory is built and maintained with zero generative LLM calls | 0 calls per conversation vs ~54 for Mem0 (`results/final/cost_latency.json`) |
| **Fast enough to be invisible.** Memory for a ~580-turn conversation is built in ~6 s on a free GPU; each strategy decision takes ~0.1 ms | Same file; decision logs |
| **Same answer quality as a leading memory service** | Judged accuracy 0.507 vs Mem0 0.467 (difference not significant); exact-answer F1 **+0.129, significant** (CLAUDE.md §12.3) |
| **Fewer wrong-code mistakes in coding assistants** | Coding traps: CEAI 2/2 and 16/26 held-out; Mem0 0/2 and 5/26; fixed window 0/2 and 3/26 (`results/final/demo_mem0/`) |
| **Never silently serves stale facts** | Stale-fact leakage 0.00 vs 0.50 for a naive summarizer; stale chunks are marked, not hidden |
| **Auditable.** Every memory decision is logged with its reason and can be overridden live | Decision log + dashboard (FR10–FR13 in `docs/REQUIREMENTS.md`) |
| **Private by default.** Runs fully offline on a laptop CPU; no conversation leaves the machine | All models are local |

## 3. Who would use it

| Segment | Why CEAI fits |
|---|---|
| **Coding-assistant and IDE-plugin builders** | Long sessions that switch between exploring, debugging and writing code; duplicate functions and renamed APIs are the costly mistakes CEAI catches |
| **Customer-support and chat products** | High conversation volume, where a per-conversation memory LLM bill multiplies |
| **Privacy-sensitive organisations** (health, finance, government, on-premise deployments) | Memory without sending data to an extraction LLM, plus a full audit trail of what the model was shown |
| **Teams on small budgets / local models** | Works with any model behind an OpenAI-compatible endpoint, including free local ones |

## 4. How it could be offered

1. **Open-source core library** (the current packages): free adoption by developers, which builds
   users and credibility.
2. **Drop-in proxy** (planned): an OpenAI-compatible endpoint placed in front of any existing
   chat app. No code change for the customer: change one URL.
3. **Hosted dashboard and audit service for teams** (paid): decision history, overrides, alerts
   when stale facts are flagged, and compliance export of what the model was shown and why.
4. **Integration support** for organisations deploying on-premise.

## 5. Cost comparison a customer can check

Memory cost per conversation = (LLM calls to build memory) × (tokens per call) × (price per token).

- **CEAI:** 0 calls, so **0 regardless of model price**.
- **Mem0:** ~54 calls per ~580-turn conversation in our runs. Its cost scales with the customer's own
  model price and with conversation volume. We did not record Mem0's tokens per call, so we do not
  quote a dollar figure; a customer can plug in their own numbers.

## 6. Honest limits (what a customer should know)

- On one independent benchmark (BEAM), request-phrased recall questions are routed to the wrong
  strategy and CEAI scores below always-RAG. The fix is planned (`docs/RISKS_AND_PLAN.md`).
- Answer-accuracy numbers so far use a 7B model as the judge; a stronger judge and the human
  agreement check are in progress.
