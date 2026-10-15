# Pre-registration: v2 hybrid retrieval (written 2026-10-16, before any test split was run with it)

This file was committed **before** any test split was run with the v2 configuration. The commit
hash and date are in git history; the test runs come after it.

## What v2 is

- **v2_hybrid** = the frozen system (CLAUDE.md §12) plus **hybrid BM25 + dense retrieval** fused
  by reciprocal rank fusion (`RetrievalConfig.hybrid = True`, `packages/retrieval/lexical.py`).
  Nothing else changes: controller rules, reranker, budgets and the reranker's code-task gate are
  the same.
- It is selected with `CEAI_SYSTEM=v2_hybrid` (`eval/frozen.py`). Every result file records which
  system produced it.
- **Why hybrid, chosen on dev only:** on the LoCoMo dev split it improved RAG evidence hit
  0.709 → 0.762, +0.052 [+0.018, +0.088] (`docs/related_work.md` §5). MMR showed no effect and
  is not part of v2. No test split has been run with hybrid.

## Gates (dev or val only). A gate fails if v2 is significantly worse than frozen

"Significantly worse" means the 95% bootstrap interval of the paired difference (v2 − frozen, on
the same items) lies entirely below zero. Checked by `eval/v2_gate.py`.

| Gate | Data | Status |
|---|---|---|
| G1 | Coding demo: adaptive must catch both traps | **Passed** on 2026-10-16: 2/2 (frozen also 2/2) |
| G2 | Synthetic controller **val** split, adaptive evidence hit | **Passed** (2026-10-15, Colab): 0.9917 → 1.0000, +0.0083 [+0.0000, +0.0250] |
| G3 | LoCoMo-Plus **dev** split (10 warm-up turns), adaptive cue hit | **FAILED** (2026-10-15, Colab): 0.1343 → 0.0945, −0.0398 [−0.0697, −0.0149] |

**If any gate fails, no v2 test split is run.** v2 is then reported as dev-only.

## Test runs (each exactly once, with `CEAI_SYSTEM=v2_hybrid`)

These use the same splits, settings and question samples as the frozen test runs, so every
comparison is paired:

1. LoCoMo test (`--split test --no-nli`)
2. In-stream LoCoMo test (`--split test`)
3. LoCoMo-Plus test (`--split test --warmup-turns 10`)
4. Synthetic controller test (`--split test`)
5. LoCoMo test answer accuracy: the same 60 random questions per test conversation (seed 0),
   with Qwen2.5-7B answering and judging

## How results are reported

- **Every result is reported, whatever its sign**, including LoCoMo-Plus, where hybrid is not
  expected to help.
- Each result is shown as frozen vs v2 on the same items, with the paired difference and its
  95% interval.
- **The frozen system stays the system of record.** v2 is reported as a pre-registered secondary
  configuration.
- No change of any kind is made to v2 after seeing its test results. Any later change would be a
  v3 and would need fresh held-out data.

## Outcome (2026-10-15)

**Gate G3 failed, so no v2 test split was run.** The notebook stopped before any test data was
used, as pre-registered. v2 hybrid is reported as **dev-only**:

- **LoCoMo dev (explicit fact recall):** RAG evidence hit +0.052 [+0.018, +0.088].
- **LoCoMo-Plus dev (implicit cues):** adaptive cue hit −0.040 [−0.070, −0.015].

**Likely cause:** LoCoMo-Plus triggers deliberately share few words with the earlier cue, so the
BM25 ranking promotes turns that share surface words over the semantically related cue.

**Conclusion:** lexical retrieval is not a free gain. It helps explicit recall and hurts
implicit-cue recall. The frozen system remains the only configuration with test results.

Any follow-up (for example, using hybrid only for explicit `qa` turns) would be a new
configuration, designed with this dev evidence. It would need its own pre-registration and gates
before any test run.
