# Zero-cost improvement roadmap

**Where this goes:** `docs/zero_cost_improvement_roadmap.md`, alongside `docs/related_work.md`,
`docs/baselines_protocol.md`, `docs/v2_hybrid_preregistration.md` and `docs/v3_preregistration.md`.

**What this is:** every item here is doable at **$0** — no paid API, no paid compute — using
infrastructure already in this repo: free-tier large models via Groq/OpenRouter (already supported
by `integration/llm_client.py`), local Ollama on free Colab/Kaggle GPU time, local scikit-learn
training, and `mem0ai` run locally. Nothing here is part of the frozen Progress Presentation 1
build. This is **after** that is done — see `CLAUDE.md` §12.8 "Open work" for how this list relates
to what was already flagged there.

**Ground rules — these are not new, they're the ones already in `CLAUDE.md` §12.7, repeated here so
this file is self-contained:**
1. Never tune anything on the test split. Any item below that changes frozen system behavior
   (marked **[needs pre-registration]**) gets its own `docs/<name>_preregistration.md` — config,
   gate, test-run rule — committed *before* running, same pattern as `v2_hybrid_preregistration.md`.
2. Gates run on dev/val first (`eval/v2_gate.py`). A failed gate means **do not run on test**, and
   the result still gets reported, same as the v2/v3 hybrid experiments.
3. Fair comparison only: same conversations, questions, budget, model, judge as whatever you're
   comparing against. Declare any correction (like the Mem0 token-limit fix) before rerunning.
4. Name components by role, not by person, in code and docs.

---

## 0. The one substitution that unlocks most of this list

`integration/llm_client.py` already speaks to "any OpenAI-compatible endpoint (Ollama, vLLM, LM
Studio, Groq, OpenRouter, DeepInfra)." Groq and OpenRouter both have free tiers for large open
models (Llama-3.3-70B-class and similar) — rate-limited, not metered. Pointing `scripts/
build_notebook.py`'s `RUN` dict at one of those instead of the local 7B via Ollama is what makes
items 1, 2 and 6 below free instead of requiring a paid API key. Nothing else in the stack changes.

---

## 1. Fix evaluation credibility first — nothing else matters if these aren't solid

### 1.1 Stronger answering model + judge
**Why:** the current Qwen2.5-7B may be compressing every strategy's score toward the same number
regardless of memory quality — a plausible explanation for several of the "ties" in `results/
RESULTS.md`.
**How, for $0:** swap the `RUN` dict in `scripts/build_notebook.py` to a free-tier 70B-class model
on Groq or OpenRouter, for both the answerer and the judge. No code changes beyond config.
**Files:** `scripts/build_notebook.py`, `integration/llm_client.py` (no changes needed, already
supports this).
**Protocol:** write `docs/stronger_model_protocol.md` before running — this doesn't change the
memory system, but it does produce new numbers against the same test split, so declare it the same
way the baselines protocol was declared. Run on dev first as a sanity check even though no tuning
decision depends on it.
**Effort:** S (config change + a longer free-tier run).

### 1.2 Two-judge cross-agreement
**Why:** right now there's one LLM judge checked against humans. Judge-vs-judge agreement between
two different free-tier models is a second, independent reliability signal, cheap to add.
**How, for $0:** run `eval/judge.py` twice with two different free-tier endpoints (e.g. a Groq model
and an OpenRouter model) over the same answers; compute kappa the same way `eval/human_agreement/`
already does for human-vs-judge.
**Files:** `eval/judge.py`, `eval/human_agreement/score.py` (reuse its kappa function).
**Effort:** S.

### 1.3 Finish the human-agreement labelling
**Why:** `CLAUDE.md` §12.3: "judge scores become citable only after the human-agreement check" —
this was still open as of the last status write-up.
**How:** already fully scripted — `eval.human_agreement.make_sheets` to (re)generate sheets if the
Colab-output copies were lost, four annotators ~20 minutes each, `eval.human_agreement.score` to get
kappa.
**Files:** `eval/human_agreement/`.
**Effort:** S (labor, not engineering).

---

## 2. Close the known weak points

### 2.1 RAG staleness leak (currently 0.27, with 23% false-positive supersession) **[needs pre-registration]**
**Why:** this is the weakest absolute number behind an actively-defended novelty claim
(`CLAUDE.md` §6.5, RAG claim 2).
**How, for $0:** two options, both pure code + local compute: (a) calibrate the NLI threshold
per task_type instead of one global threshold; (b) ensemble the NLI score with a cheap explicit-
recency heuristic (a timestamp/turn-distance signal) rather than letting NLI decide alone.
**Files:** `packages/retrieval/contradiction.py`, `packages/retrieval/nli.py`,
`eval/synthetic/retrieval/staleness.py` (the measurement).
**Protocol:** `docs/staleness_v2_preregistration.md`, gate on the dev contradiction-pairs set before
touching test.
**Effort:** M.

### 2.2 Learned granularity weights, revisiting the withdrawn chunking claim **[needs pre-registration]**
**Why:** the current boundary score uses hand-set weights and lost to fixed segments on test
(0.355 vs 0.376). A learned-weight version is the one thing LycheeMemory V2 *also* doesn't do — if
it beats fixed segments, you reclaim a real performance win, not just a design-level differentiator.
**How, for $0:** a small logistic regression over the existing boundary-score inputs, trained on
dev — CPU-only, seconds to train.
**Files:** `packages/retrieval/chunking.py`.
**Protocol:** `docs/chunking_v2_preregistration.md`, same gate structure as `v2_hybrid`.
**Effort:** M.

### 2.3 LLM-generated L2/L3 for the LoCoMo-Plus implicit-cue gap — ship as a policy toggle, not a one-way flip **[needs pre-registration]**
**Why:** worst benchmark result (adaptive 0.140 vs. naive summary 0.185) — implicit cues have no
literal key for rule-based extraction to grab onto. But flipping the LLM generator on permanently
gives up the "zero LLM calls anywhere in the memory path" claim entirely, for every benchmark, not
just this one. Don't choose one or the other — expose both as a single named setting.
**How, for $0:** add one config value, e.g. `llm_policy: "strict" | "assisted"`, recorded in every
result file the same way `CEAI_SYSTEM` already is, so provenance is never ambiguous about which
mode produced which number.
- **`strict`** (default): exactly the frozen system already tested — rule-based generator only,
  zero LLM calls anywhere in the memory path. This is what the "0 vs ~54 calls" slide uses.
- **`assisted`**: the existing `generators.py`/`prompts.py` LLM path (already built, currently off)
  is reachable, **L2/L3 only** — L1 (code signatures, keyed facts) stays rule-based always, no
  exceptions, so the contradiction-merge keying the demo depends on is never affected by this
  setting. Use the same free-tier model as §0.
**The one hard boundary, non-negotiable regardless of the toggle:** this setting must never reach
`RuleBasedController.decide()` — it only changes what a strategy module generates internally, never
which strategy gets picked or how fast. That's what keeps the §5 no-leakage rule and the ~0.1ms
decision time true in both modes.
**Why this is better than just flipping it on:** "zero LLM calls by default, measured that way, with
an opt-in mode that trades a small, bounded, logged cost for better performance specifically on
implicit-cue benchmarks" is a claim neither Mem0/MemGPT (always use an LLM, no off-switch) nor a
purely rule-based system (no on-switch) can make. Run LoCoMo-Plus dev under both modes and report
both numbers side by side instead of picking one.
**Files:** `packages/summarization/generators.py`, `packages/summarization/prompts.py`,
`packages/summarization/engine.py` (tier-selection logic), a new top-level config/flag (e.g.
`packages/contracts/config.py` or wherever `CEAI_SYSTEM` currently lives) for `llm_policy`.
**Protocol:** `docs/summarization_llm_tier_preregistration.md`, gated on LoCoMo-Plus dev
specifically, reporting both `strict` and `assisted` results.
**Effort:** M.

---

## 3. Add wins that are hard to argue with

### 3.1 Run the coding-trap demo against Mem0 directly
**Why:** "we catch 2/2 and a real competitor people use also misses them" beats "we catch 2/2
against our own fixed-window strawman."
**How, for $0:** `eval/baselines/` already has a working local `mem0ai` adapter (used for the
LoCoMo baseline comparison) — reuse it as a third arm in `demo/coding_session/run_demo.py` alongside
adaptive CEAI and the fixed window.
**Files:** `demo/coding_session/run_demo.py`, reusing `eval/baselines/`'s Mem0 adapter.
**Effort:** S–M.

### 3.2 Scale the demo from 1 script to 10–20
**Why:** one hand-built scenario invites "did you tune the demo to work"; an aggregate catch rate
over many scenarios doesn't.
**How:** write more sessions in the same shape as `demo/coding_session/script.py` — vary codebase,
vary trap type (stale config value, deprecated API, conflicting logic from two different edits) —
and extend `run_demo.py` to report an aggregate CAUGHT/MISSED rate.
**Files:** `demo/coding_session/script.py` (new variants), `demo/coding_session/run_demo.py`.
**Effort:** M.

### 3.3 Train the deferred LR/RF/GBDT controller
**Why:** `packages/controller/model_based.py` is an explicit `TODO: v2` stub, and decision logs now
exist from the frozen runs to train on. Specifically worth checking: does a learned controller find
the "recent cue → keep the window" rule that's a known, unaddressed gap on LoCoMo-Plus (noted in
`CLAUDE.md` §12.4)?
**How, for $0:** scikit-learn on the existing `runs/`/`results/final/` decision logs — local CPU
training, no new infra.
**Files:** `packages/controller/model_based.py`, `eval/synthetic/controller/`.
**Protocol:** evaluate on dev/val first against the frozen rule-based controller before any test
comparison — this is the one item that was *always* planned, but still needs the same discipline
since it's now being seriously evaluated rather than just scaffolded.
**Effort:** M.

### 3.4 Fill in the Zep / LangMem / Letta-MemGPT baselines
**Why:** these are the exact two systems (Zep, MemGPT) your headline novelty claim names directly —
right now the differentiation from them is citation-based, not measured.
**How:** all open-source, so $0 in licensing — the earlier blocker was setup complexity (Zep wants a
graph database running alongside it), not cost. Doable for free with a few hours of local setup
(e.g. a local Neo4j or the lighter-weight graph store Zep supports).
**Files:** new adapters under `eval/baselines/`, same pattern as the existing Mem0 adapter.
**Effort:** L (time, not money).

### 3.5 Measure real cost and latency, not just LLM-call count
**Why:** "0 LLM calls" is clean but abstract. Wall-clock time and $-per-1000-conversations is the
number a non-academic judge or an engineering manager actually weighs.
**How, for $0:** instrument the existing baseline-comparison run with timing, and compute $ cost
using each free-tier/local model's (zero) cost and a hypothetical paid-API rate for comparison —
the comparison itself needs no spend.
**Files:** `eval/baselines/`, `scripts/plot_pareto.py` (extend with a cost/latency chart).
**Effort:** S.

### 3.6 Show the adaptive advantage growing with conversation length
**Why:** the thesis is "fixed strategies degrade as conversations drift across types" — a chart
showing the advantage *increasing* with length is more convincing than any single fixed-length
number.
**How, for $0:** extend `eval/synthetic/controller/generate.py` (or `families.py`) to produce
conversations at several lengths, rerun the existing synthetic-set eval at each length.
**Files:** `eval/synthetic/controller/generate.py`, `families.py`, `run.py`.
**Effort:** M.

### 3.7 Verify / demo the manual-override feature
**Why:** `packages/dashboard/server.py` already accepts manual overrides per the current system
overview — this may already be further along than the P2-stub status implied earlier. Worth
confirming it's actually demo-ready (click an override live, see the decision log and dashboard
update) rather than just accepting the request silently.
**Files:** `packages/dashboard/server.py`, `packages/dashboard/static/index.html`.
**Effort:** S (verification + maybe a short walkthrough script).

---

## 4. Needs outside sourcing, not just engineering time

### 4.1 An independently-sourced mixed-domain conversation set
**Why:** the controller's best result (+0.112) lives on a synthetic set generated to match your own
thesis — the obvious objection is "you built the test to pass." A public, independently-collected
multi-domain dialogue corpus that happens to shift between chat/troubleshooting/lookup would be a
much harder result to dismiss.
**How, for $0:** use an existing public dataset rather than commissioning one. This is the one item
on this whole list that benefits from me going and finding/vetting a suitable free corpus rather
than just pointing at a file already in the repo — say the word and I'll go do that research.
**Effort:** depends on what's found; at minimum M (ETL into your existing harness format).

---

## 5. If the results hold up

### 5.1 Write it up
**Why:** `docs/related_work.md`'s 22-paper review is most of a literature-review section already.
If 1–3 above move the numbers, this stops being a student-project artifact and becomes a short,
citable technical report.
**How, for $0:** arXiv preprint submission and workshop-paper submission are both free; only a
subset of formal conference venues charge fees, and those are avoidable.
**Effort:** L, but no cost.

---

## 6. Novelty positioning changes, component by component

Everything above is engineering. This section is what to actually *say* differently once some of it
lands — the claims most worth changing, not just the numbers behind them.

### 6.1 Sliding window — fix a self-inconsistency, don't change the claim
The claim itself ("an evaluation contribution, not a mechanism claim") is correctly scoped and
should stay. But the 35-point weight ablation found equal weighting ranks 15th of 35 — relevance-
heavy weighting wins — and the frozen system still ships equal weights. That's backwards: the
experiment that tells you the better config exists, and it isn't the one running. **Ship the
ablation-winning weights as the default** (`packages/sliding_window/config.py`) and reframe the
line from "weighting is arbitrary but we tested it" to "we tested it and shipped the evidence-backed
configuration." Same claim, now internally consistent.

### 6.2 Summarization — sharpen with numbers, and fold in the §2.3 toggle
Lead with the result, not the mechanism description: "the only module here that measures what it's
about to lose, in real time, with 0.91 correlation to the actual loss" beats "a live control
signal." Once §2.3's `llm_policy` toggle exists, state the claim as two numbers, not one: stale-fact
leakage and signature retention under `strict`, plus the LoCoMo-Plus delta under `assisted` — this
turns the current weak spot into evidence of a deliberately engineered trade-off instead of a gap.

### 6.3 RAG — drop one claim from the slide, let the other carry the component
Claim 1 (adaptive granularity) lost its own performance test (0.355 vs 0.376 fixed segments).
Presenting it as "withdrawn as a performance claim, kept as a design element" invites exactly the
question you don't want on stage: "then why do you have it?" **Recommendation: drop it from the
novelty slide entirely** until §2.2's learned-weight experiment either reclaims it or confirms it
stays dropped. Let Claim 2 — extraction-free, LLM-free staleness flagging (P 0.82/R 0.73), the thing
MemStrata and Zep both need either clean typed triples or an LLM extractor to do — carry the whole
component's novelty story alone. One claim you don't have to hedge beats two where one needs a
caveat.

### 6.4 Controller — reorder what leads, don't invent a bigger claim
The accuracy win is real but fragile: large on your own synthetic set (+0.112), gone on LoCoMo
(ties), slightly negative in-stream (-0.013). Leading with "more accurate" means your strongest
number is the one benchmark you built yourself — the easiest for a skeptical panel to discount. The
number that holds on *every* benchmark with no exceptions is cost and transparency: 0 LLM calls vs.
Mem0's ~54, ~0.1ms decisions, a full logged/explainable/overridable trail. **Flip the headline**
from "more accurate" to "same accuracy as the best fixed strategy, at zero marginal cost, fully
explainable — and when the conversation changes type mid-way, also more accurate." Same underlying
result, reordered so the universally-true part leads and the conditional part supports it.

### 6.5 The unifying claim nobody's stated yet, and its one real trade-off
Each component currently argues "no LLM" separately. Put together: *the entire memory substrate —
write, retrieve, and route — makes zero generative LLM calls, on any benchmark tested, under the
`strict` policy.* Mem0 needs ~54 calls per conversation to extract memories; Zep needs an LLM to
extract graph edges; MemGPT has the LLM paging its own memory. Nobody else in the comparison set has
an architecture where *every* layer is this cheap and auditable, not just the top-level router. This
is bigger and cleaner than any single component's claim, and the evidence for it already sits
scattered across four separate results sections — it just hasn't been said as one sentence.

The trade-off, now resolved by §2.3's toggle instead of forcing a choice: the `assisted` policy is
an explicit, scoped, logged exception to this claim, not a quiet abandonment of it. State it that
way — "zero LLM calls by default; one named, bounded, opt-in exception for implicit-cue recall,
and here's exactly what it costs when it's on" — rather than letting LoCoMo-Plus's weak number
force a binary choice between the clean claim and the better score.

---

## Status (updated 2026-10-17)

| Item | Status |
|---|---|
| 3.7 Verify manual override | **Done.** Verified live: the POST reaches the next decision, `next_turn` expires, the dashboard shows it, and invalid requests get 400 |
| 3.5 Cost and latency | **Done** from recorded timings: `results/final/cost_latency.json` and `results/figures/memory_build_time.png` (CEAI about 6 s / 0 calls vs Mem0 about 972 s / 54 calls per conversation). There is no $ figure, because Mem0's per-call token counts were not recorded |
| 6.2–6.5 Claim reframing | **Done** as CLAUDE.md §6.6 (presentation framing). The numbers are unchanged |
| 6.1 Ship the ablation-winning sliding-window weights | **Deferred, and needs pre-registration.** It changes the frozen system, and the sliding-window ablation set has no dev/test split, so the weights would be chosen on the same data that reports them. First split that set, then pre-register |
| 1.1 / 1.2 Stronger free-tier model and judge | **Needs the user:** a free Groq or OpenRouter API key, set as an environment variable and never pasted in chat. Free-tier daily token limits must be checked first; one full comparison is roughly 1–2M tokens |
| 1.3 Human labelling | Needs the team (sheets ready) |
| 2.1, 2.2, 2.3, 3.3 | After Monday, each pre-registered (they change system behaviour) |
| 3.1, 3.2, 3.4, 3.6, 4.1, 5.1 | After Monday (Colab sessions, setup time or outside data) |
