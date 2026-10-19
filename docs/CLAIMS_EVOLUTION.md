# How each component's claim and design changed

For each component: the **initial claim** (from the original plan, CLAUDE.md §6.1–6.4), what
**challenged** it (published papers or our own tests), how the **design changed**, and the **final
claim** we present (CLAUDE.md §6.5–6.6). Unusual words are explained in brackets; see also
`docs/PANEL_EXPLAINER.md` (glossary) and `docs/TEST_HISTORY.md` (every test in detail).

**Why claims changed at all:**
- **Overclaiming** (saying more than the evidence supports) is the easiest way to lose marks in
  front of a panel that has read the same papers.
- Every claim was re-checked twice: against a 22-paper literature review, and against test results
  that were locked in advance. Where a claim did not survive, we narrowed it or withdrew it.

---

## Summary

| Component | Initial claim | Final claim (what we present) | Key number |
|---|---|---|---|
| **Controller (headline)** | Nobody switches memory strategy at runtime | Per-turn switching across three *different kinds* of memory, with a logged, explainable, overridable decision and **no AI model in the decision**. "Same accuracy as the best fixed method at no extra cost, and more accurate when the conversation changes type" | +0.112 on mixed conversations; ties RAG on LoCoMo; ~0.1 ms |
| **Sliding window** | (Already modest) an evaluation claim: a cheap 4-factor score beats recency | Unchanged claim; weights are a setting; "the ablation shows relevance matters most". A tuned weight set was tried and rejected because it broke the system | 59 wins / 0 losses vs recency-only |
| **Summarization** | A live information-loss score used as a control signal that triggers a switch | Unchanged, now led by the measured result: "it measures what it is about to lose, in real time (0.91 correlation), and that signal switches strategy" | Stale-fact leakage 0.00 vs 0.50 |
| **RAG, claim 1** | Chunk size decided automatically at write time, paired with a staleness check | **Withdrawn** as a novelty claim (lost on test). Returned only as an engineering result after weights were tuned on dev | 0.399 vs 0.376 fixed segments (v4b) |
| **RAG, claim 2** | Two-stage NLI-verified staleness flagging | **Strengthened and sharpened:** staleness flagging on raw conversation with **no AI model and no structured facts needed**: exact code comparison where possible, NLI otherwise | Precision 0.82 → **1.00**; wrongly retired facts 23% → **0%** (v4b) |
| **Whole system (new)** | — | "The entire memory layer (write, retrieve, route) makes **zero generative AI calls**" | 0 vs ~54 AI calls; 6 s vs 972 s (Mem0) |
| **Coding demo** | Adaptive catches both traps; fixed window catches neither | Holds on 12 unseen sessions and against Mem0, but is **not** "better than every fixed method" | 2/2 and 16/26 vs Mem0 0/2 and 5/26 |

---

## 1. Controller (ASSE): the headline

### Initial claim (original plan)

> "Every existing memory system locks in one strategy at design time. CEAI switches between all
> three at runtime." Planned proof: macro-F1 of strategy choice (a score of how often the chosen
> strategy matches the correct one, averaged over strategies), and the answer-accuracy gain over the
> best fixed strategy.

### What challenged it

- **Literature:** two 2026 systems already switch memory at runtime.
  - **FluxMem** picks between memory *structures* (ways of organising one memory) at consolidation
    points, not every turn.
  - **MemCon** picks between operations *inside* a retrieval-style memory.

  So "nobody switches at runtime" was false.
- **Later papers in our review:**
  - **MemGAS** and **RMM** adapt within retrieval;
  - **Self-RAG** decides only "search or not";
  - **MemGPT** lets the AI model manage its own memory (opaque and costly);
  - **MoMA** routes between models, not memories.
- **Our tests:**
  - **LoCoMo:** adaptive *tied* always-RAG, because nearly every question is recall.
  - **In-stream LoCoMo:** always-hybrid was marginally better.
  - **Macro-F1:** stayed low (0.33). Several strategies are often equally correct, so it
    under-states quality, and we stopped leading with it.
  - **BEAM** (independent benchmark): adaptive lost to RAG, because request-phrased questions were
    routed to the summary.

### How the claim changed

1. **Narrowed** (2026-10-06): *"per conversational turn, between sliding window / summarization /
   RAG specifically, with a logged, explainable, overridable decision"*. This keeps three axes that
   none of the five closest systems have:
   - **taxonomy:** three different *kinds* of memory;
   - **granularity:** every turn;
   - **transparency:** logged, explained, overridable.
2. **Added** (2026-10-15): "with **no AI model in the decision path**", which separates it from
   MemGPT.
3. **Framed** after the LoCoMo tie: **"no regret when one strategy is right; a gain when the
   conversation changes type."**
4. **Reordered** (2026-10-17): lead with what is true everywhere ("same accuracy as the best fixed
   method, at no extra cost, fully explainable"), then the conditional gain ("more accurate when the
   conversation changes type").
5. **Supported** by the length test: the lead over the window grows from +0.28 to +0.42 as
   conversations get longer.
6. **Limited** by BEAM: "no regret" holds only when the message classifier recognises a recall
   question.

### How the design changed

| Change | Triggered by |
|---|---|
| Rule-based controller, deciding from the turn signal only (the no-leakage rule) | Original plan (§5) |
| Test conversations in three wordings (train / val / test) | Rules had been written on the same wording as the first test |
| Routing options (`long_chat_strategy`, `qa_strategy`, `loss_escalation_target`) and the topic-shift flag | The LoCoMo-Plus negative result |
| Thresholds tuned on train + val (`low_pressure` 0.9, `min_dwell_turns` 3) and **frozen** | Systematic tuning (1,512 settings) |
| Routing kept after a selection rule declared in advance | Alternatives scored 0.638–0.640 vs 0.645 |
| **Learned controller** (logistic regression, random forest, gradient boosting) built and tested | The plan's next step. **It lost** (0.93 vs 0.99), so the rules stay |
| Manual override verified live | The "overridable" part of the claim |

**Final claim:** per-turn switching across three memory paradigms, logged, explainable,
overridable, no AI model in the decision. **+0.112** over the best single method on mixed
conversations (confidence range +0.093 to +0.129); ties RAG on LoCoMo; ~0.1 ms per decision.

---

## 2. Dynamic Sliding Window (with the Conversation Manager)

### Initial claim

Already modest in the plan: **not** "first adaptive short-term memory". The closest system, **AFM**
(Adaptive Focus Memory), already combines relevance, recency and importance. Our claim was an
*evaluation* claim: nobody has benchmarked this cheap four-factor score (relevance, freshness,
importance, topic state) against recency-only and fixed-size windows, **with an ablation (trying
many weight combinations) showing that equal weighting is not arbitrary**.

### What challenged it

- **Literature:** **Generative Agents** (a well-known paper) introduced recency + importance +
  relevance scoring, so we cite it as the origin. **LUFY** learns weights; **MemoryBank** uses a
  forgetting curve.
- **Our ablation:** equal weights ranked **15th of 35**; relevance-heavy weights won. The planned
  "equal weighting isn't arbitrary" line was therefore wrong as stated.
- **Our v4 test:** weights chosen properly on a dev split scored 1.000 vs 0.706 on the test split.
  But inside the full system they **broke** the controller (0.992 → 0.800): with freshness weight 0
  the window dropped messages even when everything fitted.

### How the claim changed

- "Equal weights justified" became **"weights are a runtime setting; the ablation shows relevance
  matters most"**.
- The failed v4 attempt became a lesson worth presenting: **a component's best setting can break the
  whole system, which is why system-level checks exist.**

### How the design changed

- The weights moved from fixed to runtime config (`sliding_window/config.py`, `CEAI_SW_WEIGHTS`).
- The last two messages are always kept, plus an inclusion threshold and a chronological restore.
- The dev-chosen weights (relevance 0.5, importance 0.5) were added in v4, then **removed** in v4b.

**Final claim:** an evaluation contribution. Recall **0.719 vs 0.556** for recency-only; **59 wins,
0 losses**.

---

## 3. Hierarchical Summarization

### Initial claim

**A real-time information-loss score used as a live control signal that triggers a strategy
switch**, not an after-the-fact benchmark metric. It was flagged in the plan as the strongest claim
but the weakest-sourced (no named closest system). The plan also noted that the *way summaries are
generated* was unspecified in the original proposal.

### What challenged it

- **Literature:**
  - **ProMem** measures memory integrity only *after the fact*. It is now cited as the closest
    system, and it is still not the same thing.
  - Our keyed merge sits next to **MemStrata** (deterministic keys), **Mem0** (an AI model decides
    updates) and **Zep** (an AI model invalidates old facts).
- **Our tests:**
  - Alone, summarization is weak at detail recall (0.05 on LoCoMo). The controller compensates by
    switching away when the loss score is high.
  - LoCoMo-Plus showed implied clues being lost.
  - The AI-written summary mode (`llm_policy="assisted"`) gave **no gain** with a 7B model.

### How the claim changed

- The claim itself is unchanged. It is now **led by the measured result**: "it measures what it is
  about to lose, in real time (**0.91 correlation** with actual loss), and that signal switches
  strategy".
- The demo shows it working: the renamed-API trap is caught *because* the loss score (0.59 > 0.15)
  switched the next turn to RAG.

### How the design changed

| Change | Triggered by |
|---|---|
| Structured tiers: **L1** exact facts, **L2** intent and decisions, **L3** user profile, with three distinct prompts for the optional AI generator | The plan's fix for the unspecified generation method |
| Rule-based generator as the default, with exact code signatures read by Python's parser (AST) | Determinism and no AI calls; signature retention 0.90 vs 0 |
| **Contradiction-resolving merge** by key (old fact marked *superseded* with a timestamp) | Stale-fact leakage 0.00 vs 0.50 |
| Eager merge (applied as each message arrives) | Renames inside the most recent messages must already supersede the old fact |
| `user_state` facts (habits, feelings, goals) | LoCoMo-Plus implied clues (summarization 0.090 → 0.109 on dev) |
| Loss score Method 1 (missing "anchors": names, numbers, code identifiers), on a background worker | Live and cheap; Method 2 and the repair loop left as documented future work |
| `llm_policy` toggle (`strict` default, `assisted` = AI writes L2/L3 only) | Tested: no gain, 56% invalid outputs, so `strict` stays the default |

**Final claim:** the live loss score is a control signal. **Stale-fact leakage 0.00 vs 0.50**,
signature retention 0.90 vs 0, correlation with real loss 0.91.

---

## 4. Retrieval (RAG)

### Initial claims

1. **Granularity-adaptive chunking:** deciding at write time whether to store each message alone or
   grouped with neighbours. The closest system, **LycheeMemory V2**, already decides boundaries with
   hand-set weights. The plan's narrowed version paired this decision with a live staleness check.
2. **Two-stage NLI staleness flagging:** a cheap pre-filter finds candidate old passages, then an NLI
   model (Natural Language Inference: a model that tells whether one sentence contradicts another)
   confirms contradictions.

### What challenged them

- **Claim 1:** **lost on the test set** at an equal word budget (0.355 vs 0.376 for fixed
  segments), after looking better on early data (0.428 vs 0.421). **MemGAS** and **SeCom** also
  adapt granularity.
- **Claim 2:**
  - In the demo, NLI raised one-directional false alarms (3 of 6) and **could not tell code names
    apart**.
  - **MemStrata** reports that NLI and AI judges leak stale facts, and needs neatly structured facts
    (subject, relation, object).
  - **Zep** needs an AI model to extract facts and to verify them.
  - Our stale-fact leak was 0.27, with 23% of current facts wrongly retired.
- **The read path:** RAG found the evidence only 39–50% of the time at first.

### How the claims changed

- **Claim 1:** **withdrawn** as a performance claim (2026-10-15), then **dropped from the novelty
  slide** entirely (2026-10-17), rather than kept with a caveat. After the boundary weights were
  tuned on dev, it beat fixed segments on LoCoMo test (**0.399 vs 0.376**, v4b), but it caused v4b's
  drop on BEAM (−0.099), where messages are long coding answers. It is presented as an
  **engineering result**, not a novelty claim.
- **Claim 2:** sharpened into the component's whole story: **"extraction-free, AI-free staleness
  flagging on raw conversation: an exact structural check for code, calibrated NLI otherwise"**.
  This is what MemStrata and Zep cannot do without structured facts or an AI extractor. The 0.27
  leak is stated plainly.

### How the design changed

| Change | Triggered by |
|---|---|
| NLI scored **in both directions** (keep the lower score) | One-directional false alarms in the demo |
| **Exact code-signature comparison** for code (AST) | NLI cannot tell `user_id` from `uid` |
| Alarm threshold 0.95 chosen on dev | Precision 0.82 / recall 0.73 on test |
| Stale passages **marked, never hidden**, with the newer passage pulled in next to them | Transparency; the model is told what is outdated |
| **Compact headers** + **cross-encoder reranker** | Evidence hit 0.496 → 0.709 (dev), 0.391 → 0.655 (test) |
| Reranker **skipped for code turns** | It ranks prose above code; the demo fell to 1/2 |
| Neighbour turns, keyword search (v2), MMR, fact "observations" (v3) | All tested; **none adopted** (worse answers, or failed gates) |
| **Staleness ensemble** (both NLI directions + similarity + change words, weights fitted on dev) | Reduce wrong retirements: precision **1.00**, false retirements **0%** (recall 0.73 → 0.69) |
| **Dev-tuned chunk boundaries** | Brought granularity back as an engineering result (0.399 on LoCoMo); it does not transfer to BEAM (−0.099), so the frozen chunking stays the default |

**Final claims:**
- **Staleness flagging:** precision 0.82 / recall 0.73 in the frozen system; **1.00 / 0.69 with 0%
  wrongly retired facts** in v4b.
- **Read path:** evidence hit 0.391 → 0.655.
- **Granularity:** an engineering result only.

---

## 5. New system-wide claim: zero AI calls in memory

### Where it came from

Each component argued "no AI model" separately. Measuring build time and AI calls side by side
(2026-10-17) made a single, bigger claim possible.

### The claim

> "The whole memory substrate (write, retrieve and route) makes **zero generative AI calls**."

- Memory for one ~580-message conversation is built in **~6 s with 0 AI calls**.
- **Mem0:** ~972 s and ~54 calls (162× slower). Summary buffer: ~704 s and ~69 calls.
- The one opt-in exception (`assisted` summaries) was tested and gave no gain, so the default stays
  strict.

### The Mem0 comparison claim

- **Initially:** "CEAI beats Mem0". Run 1 looked strong, but our harness had cut off 8.8% of Mem0's
  replies.
- **After the declared fix and re-run:** **"same judged accuracy (0.507 vs 0.467, not significant),
  higher exact-answer F1 (+0.129, significant), zero memory-building AI calls."** We never say
  "beats Mem0 on accuracy".

---

## 6. The coding demo claim

| When | Claim |
|---|---|
| Plan | Adaptive catches both traps (2/2); a fixed 6-exchange window catches neither (0/2) |
| After the reranker test | Still 2/2, but only with the reranker skipped for code (with it on, 1/2) |
| After 12 unseen sessions (pre-registered) | Adaptive 16/26 vs fixed window 3/26; every duplicate-function trap caught (7/7). **Always-hybrid caught 18/26**, so the claim is "far better than a fixed window", not "better than every method" |
| After running Mem0 on the same traps | Mem0 **0/2** and **5/26** vs CEAI **2/2** and **16/26**. Mem0 keeps that a function exists, not its exact code; it is better on project decisions (3/3 vs 2/3) |

---

## 7. What we explicitly do **not** claim

- That nobody switches memory at runtime (FluxMem and MemCon do, in narrower ways).
- That CEAI beats Mem0 on judged accuracy (the difference is not significant).
- That adaptive beats every fixed method everywhere: it ties RAG on LoCoMo, loses on BEAM, and
  always-hybrid caught slightly more unseen traps.
- That adaptive chunking is a novelty (withdrawn; engineering result only).
- That equal sliding-window weights are optimal, or that a learned controller works (it lost to the
  rules).
- That AI-written summaries help (no gain with a 7B model).
