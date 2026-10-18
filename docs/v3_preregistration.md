# Pre-registration: v3 (written 2026-10-16, before any v3 result on any split)

This file is committed before v3 is run on any dev, val or test data, apart from the coding demo
check (G1 below).

## What v3 is

v3 = the frozen system plus two retrieval changes. Nothing else changes: controller rules,
reranker, budgets and the code-task reranker gate are as frozen.

- **A. Hybrid BM25 + dense retrieval for question turns only:**
  `RetrievalConfig.hybrid_task_types = ("qa",)`.
  - Evidence: on LoCoMo dev, hybrid lifted RAG evidence hit by +0.052 [+0.018, +0.088].
  - v2 applied hybrid to every turn and failed on LoCoMo-Plus dev (−0.040). LoCoMo-Plus triggers
    are classified as `chat`, so A leaves them unchanged.
  - **This is a design choice informed by v2's dev result.** It is stated here openly, and it is why
    v3 must pass all of its own gates.
- **B. Summarizer facts as RAG observations:** `RetrievalConfig.observations = True`.
  - The integration layer passes the summarizer's verbatim fact sentences (statement, user state,
    constraint and decision facts of at least 4 words) from every turn into RAG as short
    retrievable units.
  - Each is rendered with the turn's date and speaker and linked to its source turn.
  - Motivation: the LoCoMo paper reports that RAG over *observations* works better than RAG over
    raw dialogue. Shorter units also fit more distinct turns into the budget, which matters for
    multi-hop questions.
- Selected with `CEAI_SYSTEM=v3_qa_hybrid_obs`.

## Gates (dev or val only). Checked by `eval/v2_gate.py`

| Gate | Data | Pass rule | Status |
|---|---|---|---|
| G1 | Coding demo | adaptive catches both traps | **Passed** 2026-10-16: 2/2 |
| G2 | Synthetic controller val, adaptive evidence hit | not significantly worse than frozen (paired 95% CI not entirely below 0) | **Passed** (2026-10-16): 0.9917 → 1.0000, +0.0083 [+0.0000, +0.0250] |
| G3 | LoCoMo-Plus dev (10 warm-up turns), adaptive cue hit | not significantly worse than frozen | **FAILED** (2026-10-16): 0.1343 → 0.0199, −0.1144 [−0.1592, −0.0746] |
| G4 | **LoCoMo dev answer accuracy** (60 random questions per dev conversation, seed 0, Qwen2.5-7B answering and judging), adaptive judge score | **v3 − frozen point estimate > 0** | Passed by the rule (2026-10-16): 0.5175 → 0.5240, +0.0066 [−0.0582, +0.0690], **within noise** |

**If any gate fails, no v3 test split is run**, and v3 is reported as dev-only.

## Test runs (each exactly once, `CEAI_SYSTEM=v3_qa_hybrid_obs`, only if all gates pass)

1. LoCoMo test answer accuracy: the same 230 questions as the frozen run and the external
   baselines. This is the headline comparison: v3 vs frozen, and v3 vs Mem0 (corrected), fixed-chunk
   RAG, summary buffer and full context, all paired.
2. LoCoMo test evidence (`--split test --no-nli`).
3. In-stream LoCoMo test.
4. LoCoMo-Plus test (`--warmup-turns 10`).
5. Synthetic controller test.

## Reporting

- Every result is reported whatever its sign, paired against frozen on identical items.
- **The frozen system stays the system of record.** v3 is a pre-registered secondary configuration.
- No change to v3 after seeing any v3 test result.
- **Known metric caveat, declared now:** the evidence-hit metric counts how much of an evidence
  turn's wording reaches the context. A short observation can hold the answer while covering less
  of the turn's wording, so evidence hit may understate B. Answer accuracy (G4, test run 1) is the
  deciding metric.

## Outcome (2026-10-16)

**Gate G3 failed, so no v3 test split was run.** The notebook stopped before any test data was
used. v3 is reported as **dev-only**.

- **LoCoMo-Plus dev: adaptive cue hit 0.134 → 0.020.**
  - Likely cause: change B. Many short single-turn observations fill the budget, so the second line
    of a two-line cue (which a two-turn segment used to bring in) rarely fits any more.
  - Part of this is the evidence-metric caveat declared above, but the gate was declared on this
    metric.
- **LoCoMo dev answer accuracy: +0.007, interval −0.058 to +0.069.** The dev evidence gain from
  hybrid retrieval did not turn into better answers.

**Conclusion:** neither change improves accuracy enough to justify a test run, and observations
hurt implicit-cue recall. Three retrieval variants (v2 hybrid, MMR, v3) have now been evaluated
under the same discipline, and none beat the frozen system. **The frozen system remains the system
of record.**
