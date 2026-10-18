# Pre-registration: `llm_policy` strict vs assisted (roadmap 2.3)

Committed **before** any assisted run.

## What changes

- `MemoryPipeline(..., llm_policy="strict" | "assisted")`, default `strict`.
  - **`strict`** is exactly the frozen system: rule-based summary tiers and **zero LLM calls** in
    the memory path. Every existing result is a `strict` result.
  - **`assisted`**: the LLM writes **only the L2 (intent, decisions, open goals) and L3 (persona,
    objective, state) tiers**, using the existing tier prompts (`packages/summarization/prompts.py`).
    - L1 stays rule-based in both modes: exact facts, the keyed contradiction merge and code
      signatures. The coding-demo traps depend on these.
    - Invalid model output falls back to the rule-based tier and is counted.
- **The hard boundary:** the setting never reaches the controller.
  - `RuleBasedController.decide()` receives the same TurnSignal in both modes.
  - The only way the mode can change a choice is the designed §5 path: a different summary has a
    different measured loss, so a `loss_threshold_exceeded` escalation may fire differently and
    change the **next** turn's decision. That change is logged in the rationale.
  - `tests/test_llm_policy.py` checks both properties: identical controller inputs, and every
    differing choice explained by a loss escalation.
  - *(Corrected before any assisted run: an earlier draft said "identical choices", which the
    test showed is not true.)*
  - The §5 rule and the ~0.1 ms decision time hold in both modes.
- Every result file records the policy and the number of LLM calls.

## Question

Does assisted L2/L3 close the LoCoMo-Plus implicit-cue gap, and at what cost?

- Current numbers (test): adaptive 0.140 vs the naive LLM-free summary 0.185.
- Summarization alone (dev): 0.109.

## Protocol

- **Data:** LoCoMo-Plus **dev** only (even item ids), a seeded random subset of **60 items**
  (seed 2310). Assisted mode makes several LLM calls per item, and a free Colab T4 cannot do all
  201 in a session.
- **Runs:** strict and assisted on the same 60 items, with 10 warm-up decision turns and the frozen
  controller.
  - The model is the same Qwen2.5-7B through Ollama used everywhere else (`CEAI_LLM_*`), with role
    `summary` (600-token cap).
- **Metrics:**
  - Cue hit (the existing deterministic metric) for adaptive and for always-summarization.
  - Mean cue coverage.
  - LLM calls per item, seconds per item and the fallback count.
- **Known limitation, stated in advance:** cue hit checks that the cue's *words* reach the context.
  LLM-written tiers paraphrase, so this metric may undercount what assisted mode keeps. A
  paraphrase-aware judge is the stronger test. It is not run here, because a 7B judge failed the
  agreement check for strategy labels (CLAUDE.md §12.6).

## Amendment (2026-10-17, before any run)

- **Sample size cut from 60 to 20 items** (same seed, 2310). The reason is runtime, measured before
  running: the sampled items average 610 turns, which means about 66 summary calls per item and
  4,000–5,000 calls in total, or 7–14 hours on a free T4.
- With 20 items, the result is a pilot. A 95% CI entirely above 0 is unlikely at this size, so a test
  run is unlikely too. That is reported as is; the sample is not enlarged after seeing the result.

## Reporting rule

- Both modes are reported side by side, whatever the sign, with paired bootstrap CIs over items.
- `assisted` is **never** made the default.
  - If it helps, the claim is: *"zero LLM calls by default; an opt-in mode that spends N LLM calls
    per conversation for +X implicit-cue recall"*.
  - If it does not help, the claim is that rule-based tiers are not the bottleneck for implicit
    cues, and the toggle stays as an engineering option.
- No test-split run unless the dev difference for always-summarization has a 95% CI entirely above
  0. In that case, one LoCoMo-Plus test run of both modes on the 100 odd-id items with seed 2310.

## Outcome

Run once on Colab, 2026-10-18 (`results/final/llm_policy/`), 20 LoCoMo-Plus dev items, Qwen2.5-7B.

| Policy | Cue hit: adaptive | Cue hit: always-summarization | LLM calls per item | Invalid LLM outputs | Seconds per item |
|---|---|---|---|---|---|
| strict | 0.10 | 0.05 | 0 | — | 5 |
| assisted | 0.10 | 0.05 | 85.5 | **950 of 1,710 (56%)** | 469 |

Difference: 0.000 on every item for both arms, and also 0.000 on mean cue coverage.

**Diagnosis (replayed locally from the run's own LLM cache, no new LLM calls):**

- **The 7B model often did not follow the tier prompts.**
  - 56% of its outputs were invalid (for example, it copied the input L1 records back) and fell
    back to the rule-based tier.
  - Many valid ones misread the prompt's instruction as content: one L2 intent reads "user requests
    removal of specific facts", from the prompt's own "drop the individual facts" rule.
- **On these 600-turn conversations only the L3 tier fits the budget,** and the cue's words were in
  neither version. The assisted contexts did differ slightly from strict, just not on the cues.
- **The result:** with a 7B model, assisted mode costs about 86 LLM calls and roughly 90× the time
  per conversation, and gives no measurable gain.
- **Per the reporting rule:** `strict` stays the default. The toggle stays as an engineering option.
  - Whether a stronger model helps is still open: roadmap 1.1, a free 70B-class model.
  - It would need its own pre-registration, and the prompt wording may need fixing first, which
    counts as a system change.
- **No test run** (the dev CI is not above 0).
