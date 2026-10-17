# Pre-registration: v4 component candidates and the length test

Committed **before** any run of the items below (roadmap 6.1, 2.1, 2.2, 3.3 and 3.6). The rules are
the same as `CLAUDE.md` §12.7:

- choose on dev or val only;
- a failed gate means no test run;
- every result is reported whatever its sign.

The frozen system is unchanged unless a candidate passes both its component gate (below) and the
system gates (§6).

## 1. Sliding-window weights (roadmap 6.1)

- **Problem:** the frozen system ships equal weights, but the ablation ranked them 15th of 35.
- **Data:**
  - The 40 topic-shift workloads (`eval/synthetic/sliding_window`, `generate(n=40, seed=5)`) are
    split by position: **dev = even index** (20 conversations), **test = odd index** (20).
  - **Disclosure:** the earlier ablation ran on all 40, so its direction ("relevance-heavy wins") was
    already seen on what is now the test half. The test half therefore confirms a choice; it is not a
    blind test.
- **Selection:** the 35-point weight grid (steps of 0.25) at budget 100 (the headline budget) on dev.
  - Pick the highest dev gold-turn recall.
  - Ties go to lower mean tokens, then to the higher relevance weight.
- **Component gate:** the chosen weights beat equal weights on dev recall (strictly).
- **Test report (once):** chosen vs equal weights vs recency-only on the test half: recall,
  win/tie/loss vs recency, and the same at budget 220.

## 2. Staleness v2: NLI plus cheap cues (roadmap 2.1)

- **Option (a), a per-task-type threshold, is dropped before running.** The contradiction pairs have
  no task type, and at run time prose staleness is almost always `chat`, so there is nothing to
  condition on.
- **Option (b), an ensemble.** A logistic regression (scikit-learn, `C=1.0`, default solver) on four
  features of each pair that survives the prefilter:
  1. bidirectional NLI score (min of both directions; the v1 score);
  2. maximum of the two directions;
  3. cosine similarity of the two texts (MiniLM);
  4. a change cue in the newer text, fixed now as a regex over: *moved, now, no longer, anymore,
     any more, switched, changed, left, quit, instead, these days, used to, not anymore, stopped,
     started, new*.
  - Pairs the prefilter rejects stay unflagged, exactly as in v1.
- **Training and threshold:**
  - Fit on the **dev** pairs only.
  - Choose the threshold by maximum F1 on 5-fold out-of-fold dev predictions (folds stratified,
    seed 0).
- **Component gate:** out-of-fold dev F1 > v1's dev F1 (0.776 at threshold 0.95) **and** dev
  false-supersession rate no higher than v1's.
- **Test report (once):** P / R / F1, stale-fact leak rate and false-supersession rate, next to v1's
  test numbers (0.82 / 0.73 / 0.77, leak 0.27).
- **Unchanged:** code pairs keep the exact signature diff.

## 3. Dev-tuned chunking weights (roadmap 2.2)

- **What:** random search over the boundary score
  (`bias, w_semantic, w_length, w_turns, max_segment_tokens, max_segment_turns`).
  - The shift weight has no effect in this harness (no shift signal reaches the granularity
    indexes), so it is left at 4.0.
  - 60 configurations, seed 7, uniform ranges:

    | Parameter | Range |
    |---|---|
    | bias | [−6, 0] |
    | w_semantic | [0, 8] |
    | w_length | [0, 6] |
    | w_turns | [0, 4] |
    | max_segment_tokens | {100, 150, 200, 300} |
    | max_segment_turns | {3, 4, 6, 8} |

  - The current hand-set configuration is added as candidate 0.
  - This is "dev-tuned", not a learned classifier: there are no boundary labels to learn from.
- **Objective:** evidence recall at an equal 400-word budget on LoCoMo **dev** (conversations 1, 3,
  5, 7, 9), using the same measurement as `eval/locomo/run.py`.
- **Component gate:** the best configuration's dev recall > fixed-segment dev recall (strictly).
- **Test report (once, if the gate passes):** recall at 400 words for turn, segment, v1 adaptive and
  v2 adaptive on the LoCoMo test conversations. If it fails, the claim stays withdrawn and the dev
  numbers are reported.

## 4. Learned controller (roadmap 3.3, the P2 stub)

- **Data:** the frozen system's recorded synthetic traces (`*_b400_minilm_nli_rerank-noncode`, the
  traces behind the 2026-10-15 test numbers).
  - Train on **train**, select on **val**, test once on **test**.
- **Features** (pre-decision only, §5):
  - turn count, token pressure, task type (one-hot), prior strategy (one-hot), turns since the last
    switch;
  - the TurnSignal topic-shift flag;
  - whether a loss or contradiction escalation from an earlier turn is pending.
- **Label:** the objective oracle (the cheapest strategy whose context hits); probes with no hitting
  strategy are dropped from training.
- **Variants:** logistic regression (`max_iter=2000`), random forest (300 trees, seed 0) and gradient
  boosting (seed 0), all scikit-learn defaults otherwise.
  - The model decides every turn in replay, so its prior-strategy feature comes from its own
    history.
- **Selection:** the highest val evidence hit; ties go to lower mean tokens.
- **Gate (non-inferiority):** val evidence hit ≥ the frozen rules' val hit − 0.01.
- **Test report (once):** evidence hit, tokens and macro-F1 vs the frozen rules, with a
  conversation-level paired CI.
- **Not adopted into the frozen system in any case.** It is reported as the model-based variant.
  Every decision's rationale names the model and its top class probabilities.

## 5. Length test (roadmap 3.6)

- **Question:** does the adaptive advantage grow with conversation length?
- **Data:** a new set generated with **family C wording** (the test family; never tuned on), seed
  404. Same structure as the test set, but the detour before the late probes is fixed per group at
  **2, 10, 25 or 50 exchanges**, with 15 conversations per group.
- **System:** frozen, budget 400 (as the synthetic controller set). Nothing is tuned on it.
- **Report:**
  - Evidence hit per strategy and per length group.
  - Adaptive minus RAG, adaptive minus hybrid and adaptive minus window, with conversation-level CIs.
  - Also, with no new runs, the same breakdown on the existing test traces by detour-length tercile.
- **No gate:** this is a measurement, reported whatever the shape.

## 6. System gates for a v4 frozen system

A **v4 system** is the frozen system plus each of §1 and §2 that passed its component gate. §3 joins
only if its test result also beats fixed segments; §4 never joins. Before any v4 test run:

| Gate | Pass if |
|---|---|
| G1 | coding demo still 2/2, and the held-out scenario catches are not lower than the frozen system's |
| G2 | synthetic controller val: the paired CI of v4 − frozen evidence hit is not entirely below 0 |
| G3 | LoCoMo-Plus dev cue hit: same rule |
| G4 | LoCoMo dev evidence hit: same rule |

- If all gates pass, the v4 test runs once: synthetic test, LoCoMo test, LoCoMo-Plus test, in-stream
  LoCoMo test and the demo scenarios.
- If any gate fails, v4 is reported as dev-only and the frozen system stays.

## Outcomes (2026-10-17)

| Item | Gate (dev / val) | Test (run once) |
|---|---|---|
| §1 Sliding-window weights | **Passed.** The chosen weights (relevance 0.5, importance 0.5, freshness 0, state 0) reach dev recall 1.000; equal weights reach 0.733 (rank 15 of 35) | Budget 100: chosen **1.000** vs equal 0.706 vs recency-only 0.556 (80 wins / 0 losses vs recency; 53 wins / 0 losses vs equal). Budget 220: 1.000 vs 0.989 vs 0.556 |
| §2 Staleness ensemble | **Passed.** Out-of-fold dev F1 0.826 vs 0.776; false supersession 0.022 vs 0.156 | P **1.00** / R 0.69 / F1 **0.81** vs v1 0.82 / 0.73 / 0.77. Wrongly retired current facts **0%** (v1 23%). Stale-fact leak 0.31 (v1 0.27): recall is capped by the prefilter, and the ensemble trades one more leak for zero false retirements |
| §3 Dev-tuned chunking | **Passed.** Dev recall at 400 words: best of 61 configurations 0.516; fixed segment 0.463; hand-set 0.498 | Recall at 400 words: **dev-tuned 0.399** vs segment 0.376, hand-set 0.355, turn 0.328 (the last three reproduce the recorded test numbers). **Joins v4** |
| §4 Learned controller | **Failed.** Val evidence hit: LR 0.933, RF 0.917, GBDT 0.917 vs rules 0.992 (gate needs at least 0.982). Macro-F1 is higher (0.40–0.45 vs 0.33): imitating the cheapest correct strategy costs hits when the model is wrong | Not run. The rules stay; the model-based variant is implemented and reported as dev-only |
| §5 Length test | (no gate) | See below once run |
| §6 System gates (v4 = §1 + §2 + §3) | G1 **passed** (original 2/2, held-out 16/26 = frozen). **G2 failed:** synthetic val 0.992 → **0.800**, −0.192 [−0.242, −0.133] | Not run. **v4 is dev-only** |

- **Caveat on §1:** the synthetic workload rewards relevance heavily (recall 1.000), and freshness 0
  may hurt real conversations. That is exactly what gates G1–G4 check.
- **Note on §3:** the chunking result is a single test run on 5 conversations. It reverses the
  earlier "withdrawn" status of granularity only as an engineering result (dev-tuned boundary
  weights beat fixed segments at equal cost). It is not a learned-model claim.

### Why v4 failed G2 (diagnosis on val, 2026-10-17)

- **The sliding-window weights are the cause.**
  - Early recall falls from 1.00 to 0.30, and debug follow-up from 1.00 to 0.55. Every other probe
    kind is unchanged.
  - These probes come while the whole history still fits, so the controller picks the window as
    lossless.
  - With freshness weight 0, the window now drops older turns whose relevance-plus-importance score
    falls below the inclusion threshold, even though they fit.
- **The weights won on the sliding-window workloads**, where the budget always binds, but they break
  the system's "window is lossless when history fits" assumption.
- **Lesson:** a component optimum does not transfer to the system. This is what the system gates
  are for.

### Amendment: v4b (pre-registered 2026-10-17, after the G2 failure above, before any v4b run)

- **v4b = the frozen system + §2 (staleness ensemble) + §3 (dev-tuned chunking).** It does not
  include §1.
- **Disclosure:** v4b was defined after seeing v4 fail G2, and §1 was removed because of that
  failure. No other change.
- **Gates:** the same G1–G4 as §6, against the same frozen reference runs.
- **If all gates pass:** each test split runs once, as in §6.
- **If a gate fails:** v4b is dev-only too.
