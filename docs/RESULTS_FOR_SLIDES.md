# All results, ready for slides

Every number below was read from the result files in `results/final/` (2026-10-20). Each table says
**where it ran** (laptop CPU, or Colab: Google's free cloud GPU) and **what the metric means**.
Brackets give 95% confidence intervals (the range the true value very likely lies in); a difference
is **significant** when the whole range is on one side of zero. "Frozen" means the locked system
that every official test used; "v4b" is the improved version tested on 2026-10-18.

**Metrics used:**

| Metric | Meaning |
|---|---|
| Evidence hit | Did the information needed to answer reach the AI model? (the main objective measure) |
| Judge score | An AI judge marks each answer correct (1), partial (0.5) or wrong (0). Its marks agree with 4 humans at Cohen's kappa 0.650 |
| Token-F1 | How closely the answer's words match the correct answer (0 to 1) |
| Recall | Of everything that should have been found, how much was found |
| Precision | Of what was flagged, how much was right |
| Cue hit | Whether an implied earlier clue reached the model (LoCoMo-Plus) |

---

## 1. Headline numbers (one per slide)

| Claim | Number | Source |
|---|---|---|
| Controller on conversations that change type | **0.986 vs 0.874** best single method: **+0.112 [+0.093, +0.129]** | `controller_test.json` |
| Coding traps, original demo | Syno **2/2**; fixed window **0/2**; Mem0 **0/2** | `demo.json`, `demo_mem0/` |
| Coding traps, 12 unseen sessions | Syno **16/26**; Mem0 **5/26**; fixed window **3/26** | `demo_scenarios/`, `demo_mem0/` |
| AI calls to build memory, per conversation | Syno **0** vs Mem0 **54.4** | `cost_latency.json` |
| Time to build memory, one conversation | Syno **6.0 s** vs Mem0 **971.8 s** (**162× faster**) | `cost_latency.json` |
| LoCoMo answers vs Mem0 (same questions, model, judge) | Judge **0.507 vs 0.467** (equal: [−0.060, +0.127]); token-F1 **0.406 vs 0.278** (**+0.129**, significant) | `baselines_mem0_fixed/` |
| Advantage grows with length | Lead over the sliding window **+0.28 → +0.42** (2 → 50 exchange detours) | `results/figures/length_advantage.png` |
| AI judge is trustworthy | Cohen's kappa **0.650** vs 4 humans (60 answers) | `human_agreement/agreement.json` |

---

## 2. Controller (component 4), laptop

**Mixed conversations that change type** (70 held-out conversations, 420 questions):

| Method | Evidence hit | Tokens sent |
|---|---|---|
| **Adaptive (Syno)** | **0.986** | 249 |
| Always hybrid | 0.926 | 278 |
| Always RAG (best single) | 0.874 | 172 |
| Always summarization | 0.850 | 326 |
| Always sliding window | 0.698 | 278 |
| Random choice | 0.837 | — |

- Adaptive − best single: **+0.112 [+0.093, +0.129]**.
- Adaptive − always hybrid: **+0.060 [+0.036, +0.088]**, while sending **29 fewer tokens**.
- Decision time about **0.1 ms**.
- Choice "macro-F1" (how often the exact best strategy was picked, averaged over strategies): 0.331,
  vs 0.180 for always choosing the most common strategy and 0.195 for random. A correct-enough
  strategy was chosen **98.6%** of the time.

**Length test** (60 new conversations, frozen system):

| Detour length | Adaptive | RAG | Hybrid | Window | Adaptive − window |
|---|---|---|---|---|---|
| 2 exchanges | 0.956 | 0.867 | 0.978 | 0.678 | +0.278 |
| 10 | 0.989 | 0.833 | 0.911 | 0.722 | +0.267 |
| 25 | 1.000 | 0.867 | 0.956 | 0.644 | +0.356 |
| 50 | 1.000 | 0.867 | 0.922 | 0.578 | **+0.422** |

**Learned controller** (logistic regression / random forest / gradient boosting): validation 0.93 /
0.92 / 0.92 vs rules **0.99**, so the rules are kept.

---

## 3. Sliding window (component 1), laptop

40 conversations, 360 questions, budget 100 tokens:

| Window | Recall | Recall, earlier topic |
|---|---|---|
| **Syno scored window** | **0.719** | 0.369 |
| Fixed-token window | 0.567 | 0.025 |
| Recency-only | 0.556 | 0.000 |

- Syno vs recency-only: **59 wins, 301 ties, 0 losses**.
- Weight ablation (35 combinations): equal weights rank **15th**; relevance-heavy weights reach 1.000.
  The weights are a setting.

---

## 4. Summarization (component 2), laptop

30 test conversations with facts deliberately changed or deleted, budget 1,000 tokens:

| | Syno structured + merge | Same without merge | Naive summary |
|---|---|---|---|
| **Stale-fact leakage** (outdated fact shown as current) | **0.00** | 0.75 | 0.50 |
| **Exact code signatures kept** | **0.90** | 1.00 | 0.00 |
| Current facts recalled | **1.00** | 1.00 | 0.43 |
| Information loss score | 0.06 | 0.00 | 0.37 |

- The live loss score tracks real information loss: **Spearman correlation 0.91**.
- The "without merge" column shows that the **merge** is what removes the outdated facts.

---

## 5. RAG (component 3), laptop

**Staleness flags** (184 sentence pairs; threshold chosen on dev, reported on test):

| | Frozen | v4b ensemble |
|---|---|---|
| Precision | 0.82 | **1.00** |
| Recall | 0.73 | 0.69 |
| F1 | 0.77 | **0.81** |
| Current facts wrongly marked outdated | 23% | **0%** |
| Stale-fact leak | 0.27 | 0.31 |

- At equal F1, using similarity alone would wrongly retire **83%** of current facts; NLI retires 23%.
- Code staleness via exact signature comparison: leak **0%** (2 of 2).

**Search reading (LoCoMo test, evidence hit):** 0.391 → **0.655** (compact headers + reranker).

**Chunking** (LoCoMo test, recall at an equal 400-word budget):

| Turn | Fixed segment | Adaptive (hand-set) | **Adaptive (dev-tuned, v4b)** |
|---|---|---|---|
| 0.328 | 0.376 | 0.355 | **0.399** |

The dev-tuned chunking does not transfer to BEAM (see §8).

---

## 6. LoCoMo, the main public benchmark, laptop

Test split: 5 conversations, 963 questions with evidence.

| Method | Evidence hit (frozen) | Evidence hit (v4b) |
|---|---|---|
| **Adaptive (Syno)** | **0.653** | **0.761** (+0.108 [+0.051, +0.153]) |
| Always RAG | 0.655 | — |
| Always hybrid | 0.626 | — |
| Always window | 0.081 | — |
| Always summarization | 0.046 | — |

- Adaptive ties the best single method, because nearly every LoCoMo question is a recall question
  ("no regret").
- Adaptive evidence hit by question type: single-hop 0.75, temporal 0.72, adversarial 0.71,
  open-domain 0.30, multi-hop 0.24.

**Answer accuracy (Colab: Qwen2.5-7B answering and judging, 230 test questions):**

| Method | Judge score | Token-F1 |
|---|---|---|
| **Adaptive (Syno)** | **0.507** | **0.406** |
| Always RAG | 0.507 | 0.406 |
| Always hybrid | 0.504 | 0.385 |
| Always window | 0.124 | 0.089 |
| Always summarization | 0.109 | 0.074 |

**In-stream LoCoMo** (questions asked during the conversation): adaptive **0.704** (v4b **0.782**,
+0.078); RAG 0.704; hybrid 0.718; window 0.429; summarization 0.169.

---

## 7. External memory systems (Colab, identical conditions)

Same 230 LoCoMo test questions, same 7B model, same judge, same 1,024-token budget:

| System | Judge score | Syno − system (judge) | Token-F1 | Syno − system (F1) | AI calls to build memory |
|---|---|---|---|---|---|
| **Syno** | **0.507** | — | **0.406** | — | **0** |
| Mem0 (corrected run) | 0.467 | +0.039 [−0.060, +0.127] (equal) | 0.278 | **+0.129** [+0.038, +0.210] | 54.4 |
| Fixed-chunk RAG | 0.433 | **+0.074** [+0.017, +0.132] | 0.343 | **+0.064** [+0.026, +0.103] | 0 |
| LangChain-style summary buffer | 0.096 | **+0.411** [+0.310, +0.494] | 0.066 | **+0.340** [+0.240, +0.422] | 68.6 |
| Full context (60 questions) | 0.417 | −0.067 [−0.183, +0.050] (equal) | 0.195 | **+0.182** [+0.064, +0.299] | 0 (≈24k tokens per question) |

**Build cost per conversation:** Syno 6.0 s / 0 calls; Mem0 971.8 s / 54.4 calls; summary buffer
704.4 s / 68.6 calls; fixed-chunk RAG 1.0 s / 0 calls (chart: `results/figures/memory_build_time.png`).

**Coding traps on Mem0 (Colab):**

| | Original demo | 12 unseen sessions |
|---|---|---|
| **Syno** | **2/2** | **16/26** |
| Mem0 | 0/2 | 5/26 |
| Mem0 + last 6 exchanges | 0/2 | 6/26 |
| Fixed 6-exchange window | 0/2 | 3/26 |

Per trap type (unseen sessions), Syno vs Mem0: duplicate function **7/7 vs 1/7**; rename 3/7 vs 0/7;
signature change 3/4 vs 0/4; changed setting 1/5 vs 1/5; project decision 2/3 vs **3/3**.

---

## 8. Honest results (put at least one on a slide)

| Test | Result |
|---|---|
| **BEAM** (independent benchmark, 355 questions, laptop) | Frozen adaptive **0.346** vs always-RAG **0.445** (−0.099 [−0.135, −0.065]). Request-phrased questions are sent to the summary |
| BEAM with v4b | 0.248 (−0.099 vs frozen): the tuned chunking does not transfer to long coding answers |
| LoCoMo-Plus (implied clues, 200 test items) | Frozen 0.140 = RAG = hybrid; naive summary 0.185. v4b **0.215** (+0.075, significant) |
| Unseen coding sessions | Always-hybrid caught 18/26 vs adaptive 16/26 |
| v4 (all three improvements together) | Failed its check: 0.992 → 0.800; not adopted |
| AI-written summaries (`llm_policy`, Colab, 20 items) | No gain (0.10 = 0.10); 86 AI calls per conversation; 56% of outputs invalid |
| Learned controller | 0.93 vs rules 0.99 |
| Keyword search (v2), MMR, v3 | Failed their checks; not adopted |

---

## 9. v4b: pre-registered improvement (test, each run once, laptop)

| Test | Frozen | v4b | Difference |
|---|---|---|---|
| LoCoMo | 0.653 | **0.761** | **+0.108** [+0.051, +0.153] |
| In-stream LoCoMo | 0.704 | **0.782** | **+0.078** [+0.037, +0.108] |
| LoCoMo-Plus | 0.140 | **0.215** | **+0.075** [+0.030, +0.120] |
| Controller (mixed) | 0.986 | 0.983 | −0.002 (no change) |
| BEAM | 0.347 | 0.248 | **−0.099** [−0.147, −0.056] |

The frozen system stays the default; v4b is presented as an improvement for chat-style
conversations.

---

## 10. Where each result was produced

| Laptop (CPU, no AI model) | Colab (free T4 GPU, Qwen2.5-7B via Ollama) |
|---|---|
| Controller, length test, sliding window, summarization, staleness, chunking, LoCoMo / in-stream / LoCoMo-Plus evidence hit, BEAM, coding demo + 12 sessions, v4/v4b gates and tests, learned controller | LoCoMo answer accuracy (judge + F1), all external baselines (Mem0, fixed-chunk RAG, summary buffer, full context), Mem0 coding traps, `llm_policy` pilot, the human-agreement sheets |

**Charts ready for slides:** `results/figures/memory_build_time.png`, `length_advantage.png`,
`pareto_controller.png`, `pareto_locomo.png`.
