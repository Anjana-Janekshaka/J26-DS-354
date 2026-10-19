# Every test we ran: why, what happened, what we changed

In order, from the first build (2026-10-06) to now (2026-10-18). Each test has three parts: **Why**
we ran it, the **Outcome**, and **What changed** because of it. Unusual words are explained in
brackets the first time they appear (see also the glossary in `docs/PANEL_EXPLAINER.md`).

**Three words used throughout:**

- **Evidence hit** (did the information needed to answer actually reach the AI model? This is our
  main objective measure).
- **Dev / test split** (each dataset is cut in two; we adjust the system only on the "dev" half and
  report on the unseen "test" half, so results are not inflated by practising on the exam).
- **Pre-registration** (writing down, *before* running an experiment, exactly what will be tested
  and what counts as success; the result is then reported whatever it is).

---

## Why this testing is legitimate (and how anyone can check it)

1. **We never tuned on the data we report.** Every dataset has a dev half for adjusting and a test
   half for reporting. The controller's test conversations use different wording from the ones the
   rules were written and tuned on.
2. **Settings were locked before testing, and each test ran once.** The configuration file was
   frozen, a validation check had to pass first, and the notebook's code refuses to re-run a
   finished test.
3. **Experiments were written down before they ran, and that is provable.** Every pre-registration
   file was committed to git (the version-control system that timestamps every change) before its
   results. For example, the 12 unseen coding sessions were committed at 13:18 on 10-17, before any
   result; v4b's plan was committed after v4 failed and before v4b ran. Anyone can check this with
   `git log`.
4. **Failures are reported, not hidden.** v2, v3 and MMR (failed gates), adaptive chunking on test,
   the learned controller, v4, BEAM and AI-written summaries are all reported with their numbers and
   reasons.
5. **Comparisons are fair and paired.**
   - Every method or system gets the same conversations, the same questions, the same memory budget,
     the same answering model and the same judge.
   - Inside CEAI, all methods build their context from the same stored memory at the same moment.
   - Results are compared question by question.
   - When we found our harness had handicapped Mem0, we declared the fix first and re-ran.
6. **Objective checks first.** The main measures (evidence hit, trap check, cue hit) are
   deterministic text checks that give the same answer every time and need no AI judge. AI-judged
   accuracy is a second measure, and it is checked against human marking.
7. **Uncertainty is shown.** Every difference comes with a 95% confidence interval. It is computed
   by *bootstrapping* (re-sampling the test conversations 2,000 times to see how much the result
   moves), resampling whole conversations, because questions from the same conversation are not
   independent. We call a difference real only if the whole interval is on one side of zero.
8. **Independent data, not just our own.**
   - LoCoMo and LoCoMo-Plus are public benchmarks from other researchers.
   - BEAM is a third, never used for any decision.
   - Mem0 is real third-party software.
9. **Reproducible.** The code, the frozen settings, the result files and the scripts that produce
   every table are in the repository. The Colab notebook prints the exact code version it ran, and
   89 automated tests run on every change.

## Honest limits of our testing (say these if asked)

- **The largest controller win (+0.112) is on conversations we generated.** It is held-out wording,
  but our own design. The independent BEAM benchmark did not show a gain.
- **The coding traps are few** (2 + 26), so they are a stress test, not a statistical benchmark.
  The check needs exact text, which favours systems that keep original messages.
- **AI-judged accuracy uses a 7B judge.** It passed the human-agreement check (kappa 0.650, just above
  the 0.6 bar), on 60 answers; a stronger second judge would make it firmer. Token-F1 is reported alongside.
- **Some test sets are small** (5 LoCoMo test conversations; 20 items for the AI-summary pilot), so
  intervals are wide.
- **v4b was defined after v4 failed.** This is disclosed, and v4b had to pass the same gates on dev
  before any test run.

---

## Phase A: Does each component work? (build week, 2026-10-06 → 10-09)

### A1. Automated tests (unit tests)

- **Why:** to prove every piece does what it should, and keeps doing it after every change. Unit
  tests are small programs that check one behaviour each.
- **How:** `pytest` (a standard Python testing tool) runs each test program; each one builds a tiny situation (e.g. a fake conversation using a simple stand-in for the meaning model) and checks an exact expected result. Run with `pytest -m "not models"`; GitHub runs the same command on every upload.
- **Outcome:** grown to **89 fast tests**, all passing. They cover message formats, each component,
  the controller rules, the no-leakage rule, logging, the dashboard and the full turn loop.
- **What changed:** one test checks that components never reach into each other's code (the import
  boundary). It keeps four people's work from tangling. CI (Continuous Integration: GitHub runs the
  tests automatically on every upload) was added on 10-18.

### A2. The coding demo, first run

- **Why:** a visible, objective proof. Does the right code reach the model in a realistic coding
  session with two traps, the duplicate function and the renamed function?
- **How:** A fixed 18-message script (`demo/coding_session/script.py`) with fixed assistant replies goes through the real system. At the two trap messages the program checks the text that *would* be sent to the model: the exact existing definition (e.g. `def format_due_date(`) must be present, and an old version (e.g. `get_user_tasks(user_id`) must not appear unless marked stale. No AI model writes anything, so the check is deterministic (gives the same result every run) and cannot be fooled by a lucky answer.
- **Outcome:** adaptive **2/2**, fixed 6-exchange window **0/2**. Two problems were found along the
  way:
  1. The **NLI model** (Natural Language Inference: a small model that tells whether one sentence
     contradicts another) raised false alarms. 3 of its 6 "contradictions" were wrong, all
     one-directional (A contradicts B, but B does not contradict A).
  2. The NLI model **cannot tell code names apart**: it scored `create_task(title, due)` vs
     `create_task(title, due_date)` as 0% contradictory.
- **What changed:**
  1. NLI is now scored **in both directions** and the lower score is kept, which removed all three
     false alarms.
  2. For code, staleness uses an **exact comparison of function definitions** with Python's code
     parser (**AST**, the Abstract Syntax Tree: Python's own structured reading of code).

### A3. Sliding window vs simpler windows, plus a weight ablation

- **Why:** does scoring messages (relevance, freshness, importance, topic) beat keeping the most
  recent ones? An **ablation** (trying many combinations of a setting to see which parts matter)
  over the four weights checks whether equal weighting is justified.
- **How:** 40 generated conversations with labelled topic changes; a fact is planted in one message and a question about it is asked later (360 questions). We check whether the planted message is among those the window kept. Every window gets the same token budget. Each question is compared one-to-one between the two windows (win / tie / loss).
- **Outcome:** **recall** (how often the needed message was kept) **0.719 vs 0.556** for
  **recency-only** (keeping the latest messages): better in **59** cases, worse in **0**. But **equal
  weights ranked only 15th of 35**; relevance-heavy weights did best.
- **What changed:** the weights were made a runtime setting and the claim was reworded: "the
  ablation shows relevance matters most". Changing the shipped weights was left for a properly
  split test (see G3).

### A4. Summarization on degradation traces

- **Why:** does the structured summary with its contradiction merge keep the right facts, compared
  with a **naive summarizer** (a simple one-step summary)? A **degradation trace** is a test
  conversation where facts are deliberately changed or deleted.
- **How:** 30 generated developer conversations in which facts and function definitions are deliberately changed or deleted (a *degradation*). Both summarizers see the same conversations and the same budget; the program checks whether the new value is present and whether the old value still appears as current, and computes the loss score against the details actually removed.
- **Outcome:**
  - **stale-fact leakage** (an outdated fact still shown as current): **0.00 vs 0.50**;
  - exact function definitions kept: **0.90 vs 0.00**;
  - information loss: 0.06 vs 0.37.
  - The live **loss score** follows real loss with a **correlation** (how closely two measures move
    together) of **0.91**.
- **What changed:** later (A8), a `user_state` fact type (habits, feelings, goals) was added,
  because implied clues were being lost.

### A5. Staleness flags on contradiction pairs

- **Why:** measure how well the staleness check spots outdated information, on 184 sentence pairs
  (some contradictory, some compatible).
- **How:** 184 generated sentence pairs, each labelled in advance as contradictory ("I live in Madrid" / "I moved to Berlin") or compatible, across categories (location, job, preferences, code). The pairs are split into dev and test; the alarm threshold is picked on dev only, then precision and recall are measured once on test.
- **Outcome:**
  - The alarm **threshold** (how confident NLI must be before flagging) was chosen on the dev half:
    0.95.
  - On the test half: **precision 0.82** (flags are right 82% of the time), **recall 0.73** (73% of
    real contradictions caught).
  - Later analysis in the style of MemStrata (a related research system): NLI wrongly retires 23%
    of current facts at equal F1, versus 83% for similarity alone; **stale-fact leak 0.27**.
- **What changed:** the threshold was fixed at 0.95. The 0.27 leak was declared openly and improved
  later (G4).

### A6. Controller on strategy-switch conversations, first version

- **Why:** the headline claim. Does choosing per turn beat any single fixed method on conversations
  that change type?
- **How:** Generated conversations that move through chat, code, debugging, a rename and a long detour, with test questions inserted at known points. At each question all four methods build their context from the *same* stored memory, and each is checked for the required evidence. Questions are *probes* (asked without being stored), so testing never changes the conversation. The correct answer for each question (the *oracle*) is decided objectively: the cheapest method whose context contains the evidence.
- **Outcome:** adaptive **1.000** vs best single method (RAG) 0.900 (+0.10) on 180 **probes** (test
  questions inserted into a conversation without changing it). Always-hybrid tied at 1.000.
- **What changed:** a weakness was spotted: the rules were written against the same wording the test
  used. So we built **phrasing families**: three differently-worded versions (A, B, C) of the
  conversations.
  - Rules are tuned on A and B (**train/val**: the data used to build and tune).
  - Results are reported only on C, which is never seen during tuning (**test**).
  - Every result also got a **95% confidence interval** (the range the true value very likely lies
    in), computed over whole conversations.

### A7. LoCoMo, first full run

- **Why:** **LoCoMo** is the standard public **benchmark** (a test set many researchers use) for
  long-conversation memory: about 600-message conversations with 1,986 questions. It was required by
  our plan.
- **How:** The public LoCoMo conversations are fed in message by message; then each of the 1,986 benchmark questions is asked as a probe. Evidence hit = every message the benchmark marks as the answer's source has at least 60% of its content words in the context sent to the model. All methods are scored on the same questions with the same budget.
- **Outcome:** adaptive **0.443** vs RAG 0.444, a **tie**. Almost every LoCoMo question is a recall
  question, so the controller rightly picks RAG. RAG itself found the evidence only 44% of the time.
- **What changed:** two things.
  1. The claim was framed honestly: "no regret when one strategy is right; a gain when the
     conversation changes type".
  2. Work started on improving how RAG reads results (C1).

### A8. LoCoMo-Plus, first run

- **Why:** **LoCoMo-Plus** tests *implied* memory (an earlier remark you must connect to a later
  one). It is a harder, supplementary benchmark.
- **How:** Each LoCoMo-Plus item hides an earlier *cue* and asks a later *trigger* question; we check whether the cue's words (at least 60% of them) reach the context. Same budget and questions for every method; even ids dev, odd ids test.
- **Outcome:** **a negative result.** Adaptive 0.087 vs RAG 0.167 vs hybrid 0.185. Statement-style
  messages were classified as chat and sent to the summary, which loses the clue.
- **What changed:**
  - added `user_state` facts to the summarizer (lifted summarization 0.090 → 0.109 on dev);
  - added **routing options** (alternative rules) to test properly (C5);
  - started the **dev/test discipline** for every dataset: LoCoMo conversations 1, 3, 5, 7, 9 are dev
    and 2, 4, 6, 8, 10 are test; LoCoMo-Plus even items are dev and odd items are test.

---

## Phase B: Measuring answer quality for free (2026-10-10 → 10-12)

### B1. First answer-accuracy run on Colab (the pilot)

- **Why:** evidence hit says the information *reached* the model; we also wanted to know whether the
  model then *answers correctly*.
- **How:**
  - A free AI model (**Qwen2.5-7B**, run through **Ollama**, a tool for running models locally) on
    **Colab** (Google's free cloud computers with a GPU, i.e. a graphics chip that runs AI fast)
    answers from each memory.
  - Another AI model, the **judge**, marks each answer correct (1), partly correct (0.5) or wrong
    (0).
- **Outcome:** it worked, but took **7 hours**. The sample was also biased: it took the first 50
  questions of each conversation, and LoCoMo lists questions grouped by category.
- **What changed:**
  - **parallel requests** (sending several questions at once);
  - **caching** (saving each answer so an interrupted run resumes);
  - a smaller default model;
  - a **seeded random sample** (a random but repeatable selection) instead of "first 50".

### B2. Can a 7B judge label the correct strategy?

- **Why:** the plan was a "dual-source oracle" (two independent ways of deciding the right
  strategy: an objective check and an AI judge).
- **How:** The judge was shown the four candidate contexts for each question and asked which was best; its choices were compared with the objective oracle and agreement measured with Cohen's kappa.
- **Outcome:** the 7B judge agreed with the objective check only **33%** of the time, with **Cohen's
  kappa 0.11** (agreement beyond chance; 0 = chance, 1 = perfect). It is unusable for this.
- **What changed:** strategy labels use only the objective check. For answer grading, we built
  **human-agreement sheets**: four people mark the same answers blind, and judge scores are cited
  only if kappa ≥ 0.6.
- **Human-agreement result (2026-10-19):**
  - **How:** 4 team members marked 60 of the test answers blind (without knowing which system wrote
    each one), using the same correct / partial / wrong rules as the judge. Shared items use the
    majority human label.
  - **Outcome:** the judge agrees with the humans **76.7%** of the time, **Cohen's kappa 0.650**
    (above 0.6, "substantial"), and 88.3% on correct-vs-not. It never marked an answer the humans
    called wrong as correct.
  - **What changed:** judged accuracy (e.g. CEAI 0.507 vs Mem0 0.467) is now citable, with token-F1
    reported alongside.

---

## Phase C: Improving and freezing the system (2026-10-13)

### C1. RAG read-path tuning (LoCoMo dev only)

- **Why:** RAG found the evidence too rarely (A7).
- **How:** Each read-path change was run on the LoCoMo **dev** conversations only (1, 3, 5, 7, 9), one change at a time, measuring evidence hit, whether the answer's words were in the context, and multi-step questions separately. Test conversations were not touched.
- **Outcome** (each step on the dev half):
  - old labels on each passage: **0.496**;
  - **compact headers** (shorter labels, which freed about 20 tokens per passage): **0.542**;
  - adding a **reranker** (a second, more careful model that re-orders search results):
    **0.709**;
  - adding **neighbour turns** (the messages around each hit) gave 0.735, but slightly *worse*
    answers.
- **What changed:** compact headers and the reranker were adopted. Neighbour turns were not.

### C2. The reranker on the coding demo

- **Why:** check that the improvement does not break the demo.
- **How:** The same coding demo (A2) re-run with the reranker on every turn, then with it skipped for coding messages.
- **Outcome:** with the reranker on every turn the demo fell to **1/2**. The reranker was trained on
  web text and ranks prose above code, so the existing function was pushed out.
- **What changed:** the reranker is **skipped for coding messages**, and the demo is back to 2/2. It
  is a measured trade-off, not a free gain.

### C3. In-stream LoCoMo (a new benchmark we built)

- **Why:** in plain LoCoMo, all questions come at the end. Here each question is asked either right
  after the session that holds its answer ("fresh") or at the end ("late"), so the right strategy
  changes during the conversation.
- **How:** The LoCoMo conversations are replayed session by session, and each question is inserted either right after the session holding its answer or at the very end; every method is scored at that moment, on the dev conversations.
- **Outcome (dev):** hybrid 0.758, adaptive 0.746, RAG 0.744. Even a perfect fresh/late router would
  only reach about 0.769.
- **What changed:** nothing in the system. The honest conclusion is that LoCoMo-style questions leave
  little room for routing, which is why the mixed-workload test (A6) matters.

### C4. Controller tuning

- **Why:** choose the rule thresholds systematically instead of by hand.
- **How:** Each conversation is run through the system once and recorded (a *trace*); every candidate rule setting is then replayed on the recorded traces, so 1,512 settings could be compared quickly and identically. Only the train and validation families were used; the test family (C) was never loaded.
- **Outcome:** a **grid search** (trying every combination) over 1,512 settings, on train + val only.
  The best was `low_pressure` 0.9 and `min_dwell_turns` 3, with val evidence hit **0.992**.
  - `low_pressure` is how full the budget must be before leaving the window.
  - `min_dwell_turns` is the minimum number of turns before switching again.
- **What changed:** these values were written to `frozen_rule_config.json`.

### C5. Routing variants, with a selection rule declared in advance

- **Why:** LoCoMo-Plus (A8) suggested sending long chat or lossy summaries to hybrid instead.
- **How:** The rule for choosing (best average over four named dev sets, equally weighted) was written down before the results were looked at, then applied mechanically.
- **Outcome:** the rule was declared *before* looking: best average over four dev sets. The current
  routing won (0.645 vs 0.638–0.640).
- **What changed:** the current routing was kept and the **configuration frozen** (locked).

### C6. Validation gate before testing

- **Why:** make sure the final code reproduces the frozen number before touching any test data.
- **How:** The final code re-ran the validation set and the notebook compared the number with the one stored when the configuration was frozen; it was programmed to stop before any test set if the number was lower.
- **Outcome:** **0.9917 = the frozen value**: passed.

---

## Phase D: The final test run (2026-10-14 → 10-15), each test set run once

**How:** with the configuration frozen and the validation gate passed (C6), the notebook ran each
test set exactly once; its code refuses to recompute a test result that already exists. All results
were saved as files in `results/final/` and the summary sheet `results/RESULTS.md` is generated from
those files by a script, so no number is typed by hand.

| Test | Result |
|---|---|
| Controller, mixed conversations (70, phrasing family C) | adaptive **0.986** vs best single 0.874: **+0.112 [+0.093, +0.129]**; +0.060 vs always-hybrid, with fewer tokens |
| LoCoMo test (966 questions) | adaptive 0.654 = RAG 0.656 (tie); read path 0.391 → 0.655 |
| LoCoMo answer accuracy (230 questions) | judge 0.507 (adaptive) = RAG |
| In-stream LoCoMo test | adaptive 0.704 = RAG; always-hybrid 0.718 (slightly better) |
| LoCoMo-Plus test | adaptive 0.140 = RAG = hybrid; the naive summary was best at 0.185 (a known weakness) |
| **Adaptive chunking** (choosing passage size automatically) | **0.355 vs fixed segments 0.376: did not hold on test** |
| Coding demo | 2/2 vs 0/2 |

**What changed:** the adaptive-chunking claim was **withdrawn** (it had looked better on early data,
0.428 vs 0.421, but lost on test). Every claim was narrowed against a 22-paper literature review
(`docs/related_work.md`).

---

## Phase E: Ideas from research papers (2026-10-15 → 10-16), all pre-registered

### E1. Hybrid keyword + meaning search (v2)

- **Why:** papers suggest combining **BM25** (classic keyword search) with meaning-based search.
- **How:** Pre-registered in `docs/v2_hybrid_preregistration.md` (committed before any run): the new setting and the frozen system run on the same dev items, and a gate fails if the 95% interval of the difference is entirely below zero. The notebook stops automatically if a gate fails.
- **Outcome:** LoCoMo dev **+0.052** (better), but LoCoMo-Plus dev **−0.040** (worse, significant).
  It **failed its gate** (a pass/fail check on dev data).
- **What changed:** not adopted, no test run. Lesson: keyword search helps explicit recall and hurts
  implied clues. No single setting wins everywhere, which supports being adaptive.

### E2. MMR re-ordering

- **Why:** **MMR** (Maximal Marginal Relevance: prefer results that are not near-duplicates of each
  other) is a common retrieval trick.
- **How:** Same dev conversations, frozen system with and without MMR, paired comparison.
- **Outcome:** +0.002, no effect.
- **What changed:** dropped.

### E3. v3: keyword search for questions + summary facts as extra search entries

- **Why:** a narrower version of E1, plus short fact sentences indexed for search.
- **How:** Pre-registered in `docs/v3_preregistration.md` with the same gates as E1 plus a dev answer-accuracy gate.
- **Outcome:** LoCoMo-Plus dev **0.134 → 0.020**, failing badly: the short facts crowded out the
  real clues. Answer accuracy +0.007, within noise.
- **What changed:** not adopted, no test run.

---

## Phase F: Comparison with other memory systems (2026-10-15 → 10-16)

### F1. External baselines, run 1

- **Why:** prove CEAI against systems people actually use, under identical conditions (same 230
  questions, model, judge and memory budget). The systems:
  - fixed-chunk RAG;
  - a LangChain-style summary buffer;
  - **Mem0** (a popular memory product, run with its real software);
  - full context (sending everything).
- **How:** The protocol (`docs/baselines_protocol.md`) was written first: the same 230 randomly sampled LoCoMo test questions CEAI had already answered, the same answering model, judge, answer prompt and 1,024-token memory budget for every system. Mem0 is the real `mem0ai` software run locally, not a re-implementation. CEAI and each system are compared question by question (*paired*).
- **Outcome:** CEAI was clearly ahead. But checking Mem0's logs showed **our** harness had cut off
  8.8% of Mem0's memory-extraction replies (our output limit was too low for it).
- **What changed:** we declared a **correction before re-running** (raise the limit to 8,000 tokens)
  and re-ran Mem0.

### F2. Mem0, corrected run

- **How:** Only the declared change (Mem0's output limit raised to 8,000 tokens) was made; everything else identical to F1.
- **Outcome:**
  - Judged accuracy CEAI 0.507 vs Mem0 0.467: **not significantly different**, so we call it equal.
  - **Exact-answer F1** (how closely the answer's words match the correct answer) **+0.129 for CEAI,
    significant**.
  - CEAI is significantly better than fixed-chunk RAG and the summary buffer.
- **What changed:** the claim became "same judged accuracy, higher exact-answer F1, zero memory-building
  AI calls" and **never** "beats Mem0 on accuracy".

### F3. Cost and latency, from recorded timings

- **Why:** "zero AI calls" is abstract; time is concrete.
- **How:** No new run: build times and AI-call counts were read from the logs the baseline runs had already written (`scripts/cost_latency.py`), on the same hardware for every system.
- **Outcome:** memory for one LoCoMo conversation: **CEAI ~6 s with 0 AI calls**; Mem0 ~972 s with
  ~54 calls (**162× slower**); summary buffer ~704 s.
- **What changed:** this became the lead claim: "the whole memory layer makes no AI calls".

---

## Phase G: The improvement round (2026-10-17 → 10-18), all pre-registered

### G1. Manual override, checked live

- **Why:** confirm that the "human can override" claim actually works.
- **How:** A scripted test sent override requests to the dashboard's web address while a session ran, then checked the next decision, the log and the dashboard, and sent an invalid request to confirm it was rejected.
- **Outcome:** works. The override is applied to the next decision, marked "OVERRIDE by …", and
  expires after one turn; invalid requests are rejected.
- **What changed:** it went into the live demo.

### G2. 12 new unseen coding sessions (26 traps)

- **Why:** one hand-built demo invites "did you build the test to pass?". These sessions were written
  *before* running, in Python, TypeScript, Go and SQL, with new trap types: changed settings and
  project decisions.
- **How:** Pre-registered (`docs/demo_scenarios_preregistration.md`) and committed before the first run: 12 sessions with 26 traps, each trap stating where its evidence was planted. An automatic test checks only that each trap is well-formed (the evidence really is where it says, and the question does not already contain the answer). Same trap check as A2, same budget, all methods scored on the same stored memory.
- **Outcome:** adaptive **16/26**, fixed window **3/26**, always-hybrid 18/26. Every
  duplicate-function trap was caught (7/7). Misses: changed settings, functions renamed to a new
  name, and non-Python code.
- **What changed:** the honest claim is "far better than a fixed window", not "better than every
  method". The misses went on the future-work list.

### G3. Sliding-window weights, chosen properly

- **Why:** fix the inconsistency from A3. The workload was split in two, the weights chosen on one
  half and tested on the other.
- **How:** The 40 window conversations were split 20 / 20. All 35 weight combinations were tried on the dev 20; the best was chosen and tested once on the other 20.
- **Outcome:** recall **1.000 vs 0.706** for equal weights on the test half.
- **What changed:** included in v4 (see G7).

### G4. Staleness check v2 (an ensemble)

- **Why:** reduce the 0.27 leak and the 23% wrongly retired facts from A5. An **ensemble** (combining
  several signals into one decision) mixes both NLI directions, similarity and change words like
  "moved" or "no longer". Its weights were learned on the dev half.
- **How:** The ensemble's weights were fitted on the dev pairs only, with its threshold chosen using cross-validation inside dev (training on part of dev and checking on the rest, repeatedly); then it was scored once on the test pairs.
- **Outcome (test):** **precision 1.00** (was 0.82); **wrongly retired current facts 0%** (was 23%);
  recall 0.69 (was 0.73).
- **What changed:** included in v4 and v4b.

### G5. Chunking weights, tuned on dev

- **Why:** see whether the withdrawn chunking idea (Phase D) works with weights chosen on data
  instead of by hand.
- **How:** 61 chunking settings tried on the LoCoMo dev conversations at an equal 400-word budget (every method gets the same number of words, so bigger chunks get no unfair advantage); the best was tested once on the test conversations.
- **Outcome (test):** **0.399 vs fixed segments 0.376** (hand-set weights were 0.355).
- **What changed:** included in v4 and v4b. Chunking is back as an engineering result.

### G6. Machine-learned controller

- **Why:** the plan's next step: learn the choices from recorded examples with logistic regression,
  random forest and gradient boosting (three standard learning methods).
- **How:** The models were trained on recorded decisions from the training family and compared with the rules on the validation family; the gate required being within 0.01 of the rules.
- **Outcome:** val evidence hit **0.93 / 0.92 / 0.92 vs 0.99 for the rules**. It failed its gate.
- **What changed:** the readable rules stay. The learned version is kept in the code as an option.

### G7. v4 system gates (all three improvements together)

- **Why:** an improvement that wins alone can still break the whole system, so the combined version
  must pass checks on four dev sets.
- **How:** Pre-registered in `docs/v4_preregistration.md`. A gate program (`eval/v4_gate.py`) runs the frozen system and v4 back to back on the same dev items: the 13 coding sessions, controller validation, LoCoMo-Plus dev and LoCoMo dev. It fails a gate if v4 is significantly worse, and stops at the first failure.
- **Outcome:** **failed**: controller val **0.992 → 0.800**. The cause: the new window weights (G3)
  dropped messages even when the whole history fitted.
- **What changed:** v4 was **not adopted**. We pre-registered **v4b** = v4 without the window
  weights, and disclosed that this was decided after seeing the failure.

### G8. v4b system gates

- **How:** The same gate program and the same frozen reference runs as G7.
- **Outcome (dev):** passed every gate.
  - Coding sessions 17/26 (frozen 16).
  - Controller val 0.992 (equal).
  - **LoCoMo-Plus 0.134 → 0.264** (almost double).
  - **LoCoMo 0.709 → 0.785**.
- **What changed:** v4b is allowed onto the test sets (G13).

### G9. Length test

- **Why:** the core idea says fixed methods get worse as conversations drift. So we tested 60 new
  conversations at four lengths.
- **How:** 60 new conversations generated with the held-out wording (family C) and fixed detours of 2, 10, 25 and 50 exchanges (15 each), frozen system, nothing tuned. Each length group is compared method against method with confidence intervals.
- **Outcome:** adaptive stays **0.96–1.00** at every length. The lead over the window grows **+0.28 →
  +0.42**. Over always-hybrid it is +0.04 to +0.08 from moderate length on (hybrid is slightly ahead
  at the shortest length, not significant).
- **What changed:** this became a supporting chart (`results/figures/length_advantage.png`).

### G10. BEAM, an independent benchmark

- **Why:** our biggest win (+0.112) comes from data we generated. **BEAM**, made by other researchers
  and never used for tuning, is an independent check.
- **How:** Pre-registered (`docs/beam_preregistration.md`) before running. BEAM's own questions cite the message ids that hold the answer; evidence hit uses those, and *answer in context* checks the gold answer's words for short answers. Frozen system, no settings changed, run once.
- **Outcome:** **negative.** Adaptive 0.346 vs always-RAG 0.445. The cause: about a third of BEAM's
  questions are phrased as requests ("Could you show me how…"). They are classified as chat and sent
  to the summary, which scores 0.03 on them. On questions recognised as recall, adaptive equals RAG
  (0.54).
- **What changed:** reported openly, as the first item of future work: route request-phrased recall
  to search. It is the same root cause as the LoCoMo-Plus weakness (A8).

### G11. Mem0 on our coding traps (Colab)

- **Why:** "we beat our own fixed window" is weaker than "we beat a real product".
- **How:** Pre-registered (`docs/mem0_coding_preregistration.md`). Mem0 receives each exchange as a chat app would feed it; at each trap, its retrieved memories (and, in a second variant, the last 6 exchanges too) are checked with exactly the same trap check and budget as CEAI. Its top memories are saved so anyone can read them.
- **Outcome:** original demo **Mem0 0/2** vs CEAI 2/2. Unseen sessions **Mem0 5/26** (6/26 with
  recent messages added) vs CEAI 16/26. Mem0 remembers that a function exists, not its exact code.
  It does better on project decisions (3/3 vs 2/3).
- **What changed:** this became a main results slide. We say plainly that the check needs exact text.

### G12. LLM-written summaries (the `llm_policy` toggle, Colab)

- **Why:** could an AI-written summary fix the LoCoMo-Plus weakness? It is an opt-in mode
  (`assisted`), while the default (`strict`) stays at zero AI calls.
- **How:** Pre-registered (`docs/llm_policy_preregistration.md`; the sample size cut was declared before running). The same 20 randomly chosen LoCoMo-Plus dev items run with both settings; paired comparison. The reasons for the failure were found by replaying the run's own saved AI outputs, without new calls.
- **Outcome:** **no gain** (0.10 vs 0.10). It cost 86 AI calls and ~90× the time per conversation.
  56% of the 7B model's outputs were unusable; some read our own instruction as content.
- **What changed:** `strict` stays the default. Whether a stronger model helps is open, and needs a
  free 70B model key.

### G13. v4b test runs (each once)

- **How:** Each v4b test set is run once by `eval/v4_test.py` and compared item by item with the frozen system's recorded test outputs, with confidence intervals.
- **Outcome:**

  | Test | Frozen | v4b | Difference |
  |---|---|---|---|
  | LoCoMo | 0.653 | **0.761** | **+0.108**, significant |
  | In-stream LoCoMo | 0.704 | **0.782** | **+0.078**, significant |
  | LoCoMo-Plus | 0.140 | **0.215** | **+0.075**, significant (now above the naive summary's 0.185) |
  | Controller (mixed conversations) | 0.986 | 0.983 | no real change |
  | **BEAM** (independent) | 0.347 | **0.248** | **−0.099, significantly worse** |

  - The BEAM loss is entirely in search (RAG 0.445 → 0.318); the window and summary are unchanged.
  - The only v4b change active in that harness is the tuned chunking. Its weights were tuned on
    LoCoMo's short chat messages, and BEAM's messages are long coding answers.
- **What changed:**
  - **The frozen system stays the default.**
  - v4b is presented as a pre-registered improvement for chat-style conversations, with its measured
    cost on long coding conversations.
  - Lesson: settings tuned on one kind of conversation do not transfer to another, which is itself
    an argument for adaptive memory.
  - Choosing the chunking per conversation type is a future, separately pre-registered step.

---

## Summary: what each test changed

| Test | Changed |
|---|---|
| Demo (A2) | Two-direction NLI; exact code comparison for code staleness |
| Window ablation (A3, G3) | Weights made configurable; the dev-chosen weights later broke the system (G7) and were dropped |
| Controller first run (A6) | Phrasing families, train/val/test, confidence intervals |
| LoCoMo (A7) | "No regret / gain on change" framing; RAG read-path work |
| LoCoMo-Plus (A8) | `user_state` facts; routing options; dev/test splits everywhere |
| Colab pilot (B1) | Parallel requests, caching, random sampling |
| 7B judge (B2) | Objective oracle only; human-agreement check |
| Read path (C1) | Compact headers + reranker (0.496 → 0.709 dev) |
| Reranker on demo (C2) | Reranker skipped for code |
| Tuning (C4, C5) | Frozen controller configuration |
| Final test (D) | Adaptive-chunking claim withdrawn; claims narrowed |
| v2, MMR, v3 (E) | Not adopted; "no single setting wins" lesson |
| Mem0 run 1 (F1) | Declared correction; fair re-run |
| Cost (F3) | "Zero AI calls" became the lead claim |
| Unseen sessions (G2) | Honest demo claim; future-work list |
| Learned controller (G6) | Rules kept |
| v4 gates (G7) | v4 rejected; v4b created |
| BEAM (G10) | Request-phrased routing is the top future-work item |
| Mem0 traps (G11) | Main comparison slide |
| `llm_policy` (G12) | Zero-AI default confirmed |
| v4b test (G13) | Frozen stays the default; v4b is a chat-style improvement; per-type chunking is future work |
