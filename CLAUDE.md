# CEAI — Adaptive Memory Middleware — Build Guide

**Read this whole file before writing any code.** This is the single source of truth for what to
build, where it lives, what makes each piece novel, and how each piece proves itself. It supersedes
any conflicting detail in the four individual proposal PDFs for interfaces, ownership, and build
order — those stay the source for literature review and write-up language only.

Project: J26-DS-354, "Adaptive Memory Middleware for Multi-Turn Conversational LLM Applications"
(IT4010, SLIIT, CoEAI). Team: Liyanagamage A.J. (Sliding Window + Conversation Manager) · Nethmini
S.H.S. (Summarization) · Wijewardane D.M.R. (Retrieval/RAG) · Amarathunga A.A.N.N. (Controller/ASSE).
You (Wijewardane/Romal) are implementing all four components in this repo for Progress Presentation
1. Target: **80% real, working code** — see §7 for exactly what "80%" means per component.

---

## 1. The one-sentence pitch

Every existing memory system — Mem0, Zep, Letta/MemGPT, LangChain, Cognee — locks in one memory
strategy (sliding window, summarization, or retrieval) at design time. Conversations shift type
mid-session. CEAI is a runtime controller (ASSE) that switches between all three, per turn, using
live signals, with every decision logged, explained, and human-overridable. Nothing else does that
specific combination — see §6 for exactly how narrow and how defensible that claim is as of October
2026.

---

## 2. System architecture

```
                 ┌─────────────────────────────────────────┐
                 │   Conversation Manager & State Tracker    │   (packages/conversation_manager)
                 │  turn_count, task_type, token_usage,      │
                 │  conversation_state                       │
                 └───────────────────┬────────────────────────┘
                                      │ per-turn signal broadcast (TurnSignal)
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
   ┌──────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
   │ Sliding Window    │   │ Summarization Engine  │   │ Retrieval Engine (RAG)│
   │ (DSW)              │   │ (L1/L2/L3)             │   │                        │
   │ packages/sliding_  │   │ packages/summarization │   │ packages/retrieval     │
   │ window              │   │                        │   │                        │
   └─────────┬──────────┘   └──────────┬────────────┘   └───────────┬────────────┘
             │ StrategyModuleOutput      │ StrategyModuleOutput       │ StrategyModuleOutput
             └───────────────────────────┼─────────────────────────────┘
                                          ▼
                          ┌───────────────────────────────┐
                          │  ASSE — Runtime Memory          │   (packages/controller)
                          │  Controller                     │
                          │  rule-based now | LR/RF/GBDT later │
                          └───────────┬─────────────────────┘
                                      │ ControllerDecision
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
         ┌────────────────┐  ┌──────────────────┐  ┌───────────────┐
         │ Decision Logger  │  │ Runtime Dashboard  │  │ LLM Interface  │
         │ packages/        │  │ packages/dashboard  │  │                │
         │ decision_logger  │  │                      │  │                │
         └────────────────┘  └──────────────────┘  └───────────────┘
```

Every turn: Conversation Manager runs first and broadcasts `TurnSignal` → all three strategy modules
compute `StrategyModuleOutput` in parallel → ASSE picks one using **only pre-decision signals**
(never a module's own `quality` block for the same turn — see §5) → Decision Logger records it →
Dashboard renders it → LLM Interface assembles the final prompt from the selected module's output.

---

## 3. Directory structure — build exactly this

```
ceai-memory-middleware/
├── CLAUDE.md                       # this file
├── README.md                       # one-paragraph summary + how to run eval/demo
├── packages/
│   ├── contracts/                  # §4 schemas as code — nothing else is allowed to redefine these
│   ├── conversation_manager/       # Component: Conversation Manager (Liyanagamage's design)
│   ├── sliding_window/             # Component 1: Dynamic Sliding Window (Liyanagamage's design)
│   ├── summarization/              # Component 2: Hierarchical Summarization (Nethmini's design)
│   ├── retrieval/                  # Component 3: RAG (Wijewardane's design — your own)
│   ├── controller/                 # Component 4: ASSE (Amarathunga's design)
│   ├── decision_logger/            # schema: Amarathunga's spec, storage: Nethmini's spec
│   └── dashboard/                  # shell: Liyanagamage's spec, per-module panels: each owner's
├── eval/
│   ├── locomo/                     # primary benchmark harness (original LoCoMo, arXiv 2402.17753)
│   ├── locomo_plus/                # supplementary only — implicit-constraint eval, see §8
│   └── synthetic/                  # one subfolder per component's own ground-truth set
│       ├── sliding_window/         # topic-shift-labeled workloads
│       ├── summarization/          # degradation-injected traces
│       ├── retrieval/              # contradiction pairs
│       └── controller/             # strategy-switch-labeled conversations (dual-source oracle)
├── demo/
│   └── coding_session/             # the coding-assistant demo — see §9. Promote the existing
│                                    # ceai-demo/ scaffold here and wire it to real packages/*
└── integration/                    # end-to-end turn loop wiring all packages together
```

**Hard rule**: a module under `packages/*` only imports from `packages/contracts/` and its own code.
Never import another component's internals directly. If `contracts/` needs to change, that's a
reviewed change, not a unilateral edit — this is what actually prevents components from conflicting
with each other once four people's code (or four pieces of your own code) sit in one repo.

---

## 4. Shared contracts (canonical — implement these as real types, e.g. Pydantic)

### 4.1 `TurnSignal` — published by Conversation Manager, consumed by everyone

```json
{
  "turn_id": "string (monotonic)",
  "conversation_id": "string",
  "turn_count": "int",
  "task_type": "string (e.g. 'chat' | 'code_refactor' | 'qa' | 'debugging' | 'exploration')",
  "token_usage": {"used": "int", "budget": "int"},
  "conversation_state": "string (active_task_id, or 'shift_detected')",
  "timestamp": "iso8601"
}
```

### 4.2 `ControllerFeatureVector` — Tier 0/1, built and self-tracked by ASSE

```json
{
  "turn_count": "int",
  "token_budget_pressure": "float [0,1]",
  "task_type": "string",
  "prior_strategy": "string | null",
  "time_since_last_switch": "int (turns)"
}
```
`prior_strategy` and `time_since_last_switch` come from ASSE's own decision history — Conversation
Manager never tracks them.

### 4.3 `StrategyModuleOutput` — returned by each of the three strategy modules to ASSE

```json
{
  "module": "sliding_window | summarization | rag",
  "candidate_context": "string | array<turn>",
  "readiness": {"available": "bool", "estimated_latency_ms": "float"},
  "quality": { "...module-specific, below..." },
  "token_count": "int"
}
```

Sliding Window `quality`:
```json
{"selected_turn_ids": ["..."], "scores": {"relevance": 0.0, "freshness": 0.0, "importance": 0.0, "state": 0.0, "composite": 0.0}}
```

Summarization `quality`:
```json
{"tier_emitted": "L1 | L2 | L3", "loss_score": "float [0,1]", "loss_threshold_exceeded": "bool (loss_score > 0.15)", "symbol_retention_rate": "float | null (code sessions only)"}
```

RAG `quality`:
```json
{"granularity_tag": "turn | segment", "retrieved_chunk_ids": ["..."], "contradiction_flags": [{"chunk_id": "...", "nli_confidence": 0.0, "superseded_by": "chunk_id"}]}
```

### 4.4 `ControllerDecision` — ASSE's output; consumed by Decision Logger, Dashboard, LLM Interface

```json
{
  "turn_id": "string",
  "selected_strategy": "sliding_window | summarization | rag | hybrid",
  "rationale": "string (human-readable, built from feature_vector)",
  "controller_variant": "rule_based | logistic_regression | random_forest | gbdt",
  "decision_latency_ms": "float",
  "override": {"applied": "bool", "by": "string | null"}
}
```

### 4.5 `DecisionLogRecord` — append-only JSONL

```json
{
  "turn_id": "string",
  "feature_vector": "ControllerFeatureVector",
  "decision": "ControllerDecision",
  "module_outputs": {"sliding_window": "...", "summarization": "...", "rag": "..."},
  "logged_at": "iso8601"
}
```

**Important — port the existing demo onto these exact names before building the Dashboard.** The
`ceai-demo/harness.py` scaffold already built uses its own informal shapes (`active_strategy`,
`rationale` as a flat string). When you move it into `demo/coding_session/`, rename its output to a
real `ControllerDecision` object (fill `controller_variant: "rule_based"`, `override: {"applied":
false, "by": null}`) so the Dashboard (§3, `packages/dashboard`) renders the same field names whether
the data comes from the real pipeline or the demo script. Five-minute rename now saves a rebuild
later.

---

## 5. The one design rule that must never be violated

**ASSE's per-turn decision uses only `ControllerFeatureVector` (Tier 0/1) — never a module's own
`quality` block (Tier 2) from the same turn.** Tier 2 signals (summarization's `loss_threshold_
exceeded`, RAG's `contradiction_flags`) are computed only *after* that module already ran for that
turn — using them to pick that same turn's strategy is circular. Instead:

1. A Tier 2 signal can raise an **escalation event** after it fires: logged + shown on the Dashboard
   immediately, and folded into `prior_strategy`/feature-vector context for ASSE's **next** turn's
   decision — never retroactively changing the turn that just rendered.
2. Mid-turn repair (re-running the same turn with a different strategy) is an explicit v2 scope cut,
   not part of this build.

This single rule is what lets Nethmini's loss-triggered-switch design and Amarathunga's no-leakage
controller design both be true at once. Do not "optimize" this away by wiring `quality` straight into
the same-turn decision — it looks like it would work and it would quietly break the project's own
stated novelty claim about the controller being leakage-free.

---

## 6. The project's novelty claims — exact, narrowed, and what disproves/survives each one

Every claim below has already been checked against the live literature (October 2026). State them
in the presentation **exactly this narrow** — the unnarrowed version of each claim has already been
found to be partially pre-empted, and overclaiming is the single easiest way to lose LO1 marks or
lose a Q&A exchange.

### 6.1 Headline claim — ASSE orchestration (Component 4, Amarathunga's design)

> Not: "nobody switches between memory strategies at runtime." (False — see below.)
> Say instead: **"nobody switches, per conversational turn, between sliding window / hierarchical
> summarization / RAG specifically — with a logged, explainable, human-overridable decision trail."**

Two 2026 systems already do runtime, learned, per-step memory selection:
- **FluxMem** (arXiv 2602.14038) — MLP classifier picking Linear/Graph/Hierarchical memory
  *structures*, at episodic-consolidation boundaries, not every turn. +9.18% PERSONAMEM, +6.14%
  LoCoMo over its baseline.
- **MemCon** (arXiv 2607.13591) — RL/UCB contextual bandit picking among 6 MDP operations
  (Retrieve/PlanInject/Re-Retrieve/Consolidate/Forget/NoOp) — all variations *within* a retrieval-
  style paradigm, not across sliding-window/summarization/RAG.

Three axes survive, confirmed absent in **both** of the above plus MemRouter (2605.00356), AgeMem
(2601.01885), and ENGRAM (2511.12960, which names this gap explicitly as its own unimplemented
future work):
1. **Taxonomy** — sliding window / summarization / RAG are three architecturally distinct paradigms
   with different retention and compute tradeoffs (no store / compressive / retrieval-based), not
   organizational variants of one paradigm or a fixed menu of access ops.
2. **Granularity** — strictly per-turn, not per-episode or per-consolidation-boundary.
3. **Decision transparency** — logged + explainable + overridable. None of the five systems above
   implement this.

Also hold, with no narrowing needed: no commercial/open-source product (Mem0, Zep, Letta, LangGraph/
LangMem) ships cross-paradigm runtime switching as a user-facing feature — their "adaptive" marketing
means adaptive retrieval depth or graph updates, not discrete strategy-family switching.

**Validation that proves this claim**: run the real ASSE (rule-based variant) vs. each fixed-strategy
baseline (always-sliding-window, always-summarization, always-RAG) on LoCoMo + the synthetic
strategy-switch-labeled set. The number to put on a slide: **macro-F1 of strategy selection, and the
downstream QA-accuracy delta of adaptive vs. the best single fixed baseline.** A positive delta here
is the whole project's thesis in one chart.

### 6.2 Component 1 — Dynamic Sliding Window (Liyanagamage's design)

**Honest framing, not a mechanism-novelty claim**: DSW does not claim to be the first adaptive
short-term memory selector. Nearest neighbor: **Adaptive Focus Memory / AFM** (arXiv 2511.12712) —
real, close match, combines semantic relevance + recency decay + LLM-based importance with
Full/Compressed/Placeholder fidelity tiers. Differentiator: AFM varies *fidelity* per message using
an LLM classifier; DSW does binary include/exclude with cheap rule-based scoring, plus a dedicated
upstream Conversation-State signal AFM has no equivalent of. The defensible gap is evaluation, not
mechanism: nobody has systematically benchmarked this specific lightweight 4-factor combination
against recency-only and token-budget-only baselines, with a weight-ablation study justifying the
weighting. State it that way — don't overclaim mechanism novelty here, the panel can check AFM.

**Validation**: ablation over `w_relevance, w_freshness, w_importance, w_state` (don't hardcode
equal weights — make them runtime config, per §8 of the full spec), benchmarked against recency-only
and fixed-token-window baselines on LoCoMo. Number for the slide: **composite-score win rate vs.
recency-only baseline, plus the ablation chart showing equal-weighting isn't arbitrary.**

### 6.3 Component 2 — Hierarchical Summarization (Nethmini's design + generation-mechanism fix)

**Claim 1 (real)**: a real-time information-loss score used as a **live control signal** that
triggers a strategy switch — not an offline benchmark metric computed after the fact. Closest system,
ProMem ("Beyond Static Summarization," arXiv 2601.04463), evaluates memory integrity *post-hoc*
against benchmarks, using static fixed thresholds, never a live score feeding a switch decision.
Every other system/survey checked treats loss/compression-quality as offline evaluation only. This
is the strongest-standing of the three component claims — but it was also flagged as the
weakest-*sourced* at proposal stage (no "closest prior attempt" citation, unlike the other two). Fix
that before defense by citing ProMem explicitly as the "closest, and still not the same" system.

**The generation mechanism itself was underspecified in the original proposal — build it as follows**
(this closes a real gap the proposal left as "summarizes into structured key facts" with no method):
- Structured JSON per tier, not free text:
  `L1: {facts, entities, constraints, turn_range}` · `L2: {intent, decisions, open_goals,
  source_l1_ids}` · `L3: {persona, main_objective, final_state, source_l2_ids}`
- **Three distinct prompts**, one per tier (L1 = extract verbatim, no interpretation; L2 = describe
  intent/decisions from L1 facts, drop the individual facts; L3 = generalize who the user is and what
  they want — the only tier allowed to generalize). This, not just a higher compression ratio, is
  the actual L1/L2/L3 difference.
- **Contradiction-resolving merge**: before writing a new record, diff new facts against current
  summary state by key (e.g. `user.location` or, for code, a function's signature); on conflict, mark
  the old value superseded with a timestamp instead of letting both sit in the summary. This is the
  code-domain version of the renamed-API trap already proven in `demo/coding_session/`.
- **Stretch goal (don't block 80% on this)**: feed the loss score back into generation as a one-shot
  repair re-prompt ("these facts were dropped, incorporate them") before falling back to RAG — turns
  the scorer from a monitor into a feedback loop. Stronger claim than "detects loss and swaps
  strategy," but build the monitor-only version first.

**Validation**: loss-score reduction of structured-output + merge vs. a naive single-prompt
summarizer baseline, on the synthetic degradation-injected trace set (not LoCoMo-Plus — see §8 for
why). For code sessions specifically: **Symbol Retention Rate** — does the L1 tier still contain the
exact function signature N turns later. This metric is exactly what `demo/coding_session/`'s
duplicate-function trap already measures end to end.

### 6.4 Component 3 — RAG (Wijewardane's design — yours)

**Claim 1 — granularity-adaptive chunking, decided live at write time.** This has the most serious
challenger of any component claim: **LycheeMemory V2** (arXiv 2608.12990, independently verified
against two mirrors) computes a boundary score at construction time,
`p_t = σ(b + w_s·φ(s_t) + w_c·d_t + w_l·L_t + w_n·N_t)` (semantic surprise + cohesion drop +
token-length + turn-count pressure, δ=0.50 threshold), reporting 89.22% LoCoMo / 92.20%
LongMemEval-S accuracy and 75–86% construction-token savings vs. an A-Mem baseline. Its `N_t` maps
directly onto this component's own "turn-count" signal. **Do not claim unqualified novelty here —
reframe:** LycheeMemory V2's boundary score is a 4-signal, *hand-set-weight* (not learned —
confirmed in its own Appendix C.1) function producing one binary decision, with nothing else
attached. This component's gap: **pair the live granularity decision with a live contradiction/
staleness check on the resulting chunks — LycheeMemory V2 does not attempt this at all.** Also cite
its own stated limitations (single GPT-4o-Mini judge, no inter-judge agreement check; evaluated on a
filtered 1,540/1,986 LoCoMo questions, excluding the adversarial/counterfactual category) alongside
its headline numbers — don't just quote the good numbers back.

**Claim 2 — two-stage NLI-verified contradiction/staleness flagging.** Still genuinely open: CLEAR
(arXiv 2609.03482) uses NLI for answerability scoring, not supersession-flagging; TSM (arXiv
2601.07468) needs structured typed facts in a temporal KG, which free-text conversational memory
doesn't have. Design: cheap recency+topic-overlap prefilter generates candidate pairs → pretrained
NLI model (e.g. `cross-encoder/nli-deberta-v3-base`, no fine-tuning) scores contradiction probability
→ only pairs above threshold get flagged. One honest footnote for Q&A: an independent GitHub issue
(`AromalBiju1/GRAFT` #44, unrelated repo/person, verified) proposed the same NLI-over-keyword-overlap
idea the same week — context that the idea is "in the air," not citable prior art, not strong enough
to retire the claim.

**Validation**: DCG/NDCG on LoCoMo comparing adaptive granularity vs. fixed turn-level and fixed
segment-level baselines; contradiction-flag precision/recall on the synthetic contradiction-pairs set
(calibrated, not just accuracy — per MemStrata's own finding that unvalidated similarity/LLM-judge
methods leak stale facts).

---

## 7. What "80% done" means, concretely, per component (Progress Presentation 1 scope)

Build order matches priority, not calendar weeks — slot your own dates in. **P0 must be real and
running. P1 should be real. P2 can be a documented stub** (interface implemented, returns a
plausible fixture, clearly marked `# TODO: v2` — never silently fake a result as if it were real).

| Component | P0 (must work) | P1 (should work) | P2 (stub OK for now) |
|---|---|---|---|
| Conversation Manager | Turn counter, token-budget tracker, `TurnSignal` published to a shared bus | Rule-based task-type classifier (phrasing + topic-similarity drop) | — |
| Sliding Window | Composite scoring formula, runtime-config weights, chronological restore | Weight-ablation study | — |
| Summarization | L1 structured extraction + contradiction-merge (code-domain: exact signatures) | L2/L3 tiers; async loss-score worker (Method 1 only) | Dual Q&A Consistency on LoCoMo-Plus-adjacent synthetic set; repair-loop (§6.3 stretch) |
| RAG | FAISS IndexFlatIP + sentence-transformer embeddings, turn-level chunking, top-K retrieval | Granularity-adaptive chunking (turn vs. segment); NLI contradiction stage | Full calibrated precision/recall sweep |
| ASSE Controller | Rule-based decision engine, `ControllerDecision` with rationale, manual override | — | LR→RF→GBDT model-based variant (needs decision logs that don't exist yet — correctly deferred per original build order) |
| Decision Logger | Append-only JSONL writer/reader matching §4.5 exactly | — | — |
| Dashboard | Renders `ControllerDecision.rationale` + strategy-switch timeline live, reusing the demo's proven rationale-string pattern | Per-module panels (retrieval/summarization/controller) | Manual-override UI control |
| Coding demo | Already built and verified (`demo/coding_session/`) — port onto real packages/* per §4's naming note | — | — |

This table **is** your "80%" checklist — if every P0 cell is real and every P1 cell is at least
partially real, you are at 80% honestly, not by assertion.

---

## 8. Benchmark plan — standardized, do not deviate per component

**Primary benchmark for all four components: original LoCoMo** (Maharana et al., arXiv 2402.17753).
Gives grounded QA pairs for DCG/NDCG, factual-consistency, and (via each component's own synthetic
oracle-labeling protocol) strategy-selection ground truth.

**LoCoMo-Plus (arXiv 2602.10715) is supplementary only** — it evaluates implicit/latent-constraint
retention via LLM judge (causal/state/goal/value-based memory), has no code/IDE content, and
provides **no per-turn strategy ground truth**. Two teammates' original proposals (Nethmini,
Amarathunga) leaned on it for things it doesn't support — don't repeat that mismatch in the real
build: Summarization's Dual Q&A Consistency target goes on the synthetic developer-trace corpus, not
LoCoMo-Plus; any LoCoMo-Plus conversations used for the controller get their strategy-oracle labels
from the same dual-source (objective + LLM-judge) protocol as the synthetic set, never from
LoCoMo-Plus itself.

**Per-component ground truth, each its own synthetic set** (already scaffolded as folders in §3):
contradiction pairs (RAG), topic-shift-labeled workloads (Sliding Window), degradation-injected
traces (Summarization), strategy-switch-labeled conversations with dual-source oracle labels (ASSE).

---

## 9. The coding-assistant demo — your impressive, judge-visible proof

`demo/coding_session/` (promoted from the already-built and verified `ceai-demo/` scaffold) is the
single artifact that makes every claim above legible in ten seconds instead of requiring a trusted
LLM judge. It is deterministic — it checks **what context reaches the model**, not response quality
— so it never depends on live model output for its core proof.

Already proven with the throwaway scaffold (reproduce this with the real packages/* once built):
an 18-turn scripted session (exploration → debugging → long detour → duplicate-function trap →
renamed-API trap) run through a fixed 6-turn sliding-window baseline and an adaptive controller.
Result: fixed baseline misses both traps (0/2); adaptive catches both (2/2), with a printed
rationale per decision — e.g. *"build-request pattern matched → RAG override → found existing
definition at turn 2"* and *"rename tracker surfaced turn 9 (get_user_tasks: user_id → uid)."*

For the real build, this demo is also where Component 2's symbol-retention claim (§6.3) and
Component 3's contradiction-flagging claim (§6.4) get their most concrete, non-benchmark proof — a
renamed function parameter and a duplicate function are objective, checkable facts, not LLM-judge
calls. Use it as the live centerpiece of the presentation; use the LoCoMo numbers (§6, §8) as the
rigor behind it.

---

## 10. Build order

1. `packages/contracts/` as real code (Pydantic or equivalent) + a schema-validation test. Nothing
   else starts until this exists — every other package imports from here.
2. `packages/conversation_manager/` — stub `TurnSignal` is enough to unblock everyone else.
3. `packages/sliding_window/`, `packages/summarization/`, `packages/retrieval/` in parallel, each
   against the stubbed `TurnSignal`/`StrategyModuleOutput` contracts — no cross-imports between them.
4. `packages/controller/` (rule-based only) against stubbed module outputs — doesn't need the real
   modules yet, just contract-shaped fixtures.
5. `packages/decision_logger/` + `packages/dashboard/` shell, wired to the controller's real output —
   port the demo's rationale-string pattern here per §4's naming note.
6. Real integration: wire the actual Sliding Window / Summarization / RAG modules into the
   controller, logger, and dashboard end to end.
7. Promote `demo/coding_session/` onto the real pipeline; run the §8 benchmark suite; pull the
   numbers named in §6 for each component onto presentation slides.
8. (Post Progress Presentation 1, not part of 80%): model-based controller (LR→RF→GBDT) once enough
   real decision logs exist to train on.

---

## 11. Presentation checklist — depicting novelty and validation impressively

For each component, one slide/section with exactly three things, no more:
1. **The claim, narrowed** (copy the bolded "say instead" line from §6 — don't improvise a broader
   version live).
2. **The one system it's closest to, named**, with the one-sentence difference (also in §6 — this
   is what survives a panel member who's read the same paper).
3. **One number**, from §6's "validation that proves this claim" line — not a methodology
   description, the actual result.

Then one integration slide: the coding-demo CAUGHT/MISSED table (§9) as the single visual that ties
all four components' claims together — this is the slide judges/panel remember.

---

## 12. Build log & current status (updated 2026-10-15)

Sections 1–11 are the plan. This section records what was actually built, what the numbers are
so far, and the decisions taken during the build that later work must respect. Name components
by role here and in code, never by person.

### 12.1 What exists

- **Every package in §3 is implemented** and wired end to end in `integration/`: contracts, conversation
  manager, sliding window, summarization, retrieval, rule-based controller, decision logger and
  dashboard (live server + static export).
  - The P2 items are explicit `TODO: v2` stubs: the LR/RF/GBDT controller, loss Method 2 and the
    summary repair loop.
  - Run `pytest -m "not models"` for the fast suite.
- **`demo/coding_session/` was rebuilt from the §9 description.** The original `ceai-demo/` scaffold
  was not available.
- **Evaluation harnesses** (each writes `results/summary.json`):
  - `eval/locomo` (primary)
  - `eval/locomo_plus` (supplementary; deterministic "did the cue reach the context")
  - `eval/synthetic/{sliding_window,summarization,retrieval,controller}`
- **Free-LLM workflow**, used for answer accuracy, LLM-written summaries and judges:
  - `integration/llm_client.py`: adapter for OpenAI-compatible endpoints (Ollama, vLLM, LM Studio,
    Groq, OpenRouter, DeepInfra), with a disk cache so interrupted runs resume.
  - `notebooks/free_gpu_eval.ipynb`: runs on Colab or Kaggle with Ollama. It checks for the GPU and
    prints a runtime estimate before the long part. Rebuild it with `scripts/build_notebook.py`, and
    package the code for upload with `scripts/package_for_notebook.py`.
  - `eval/judge.py`: correct / partial / wrong answer judge (1 / 0.5 / 0).
  - `eval/human_agreement/`: blind labelling sheets plus judge-vs-human Cohen's kappa. A judge's
    numbers are citable only if kappa is at least 0.6.
- **RAG read path** (`RetrievalConfig`):
  - **Compact chunk headers** are the default: `[turns: t0012]`. The old headers spent about 20
    tokens per chunk, close to half of a 1,024-token budget.
  - **Optional cross-encoder reranker**: `reranker="cross-encoder/ms-marco-MiniLM-L-6-v2"`, in
    `packages/retrieval/rerank.py`. It is on by default in every benchmark harness and the demo
    (`--no-reranker` turns it off).
    - It is **skipped for code tasks** (`rerank_skip_task_types`: `code_generation` and
      `code_refactor`, read from the TurnSignal), which keep the bi-encoder ranking. See 12.3.
  - **Optional neighbour turns** around each hit (`neighbors`), kept as an ablation only.
- **More benchmarks and options:**
  - `eval/locomo/stream.py`, **in-stream LoCoMo**: each question is asked either right after the
    session holding its evidence ("fresh") or at the end ("late"), so the right strategy changes
    during the conversation.
  - `eval.locomo.run --split dev|test`: conversations 1, 3, 5, 7, 9 are dev, the rest test.
  - The answer prompt now tells the model to resolve relative dates against the session date.
- **Controller routing options** in `RuleConfig`: `long_chat_strategy`, `loss_escalation_target` and
  `qa_strategy`. Rules also receive the TurnSignal's topic-shift flag, a Tier 0 signal, so this
  doesn't break §5.
- **Frozen configuration:** `eval/synthetic/controller/frozen_rule_config.json`, loaded by
  `eval/frozen.py`. Every benchmark and the demo run with it. It is written by
  `eval.synthetic.controller.tune_rules`, which tunes on train + val only, and recording resumes
  after an interruption.
- **The notebook also runs GPU-only jobs** (controller tuning, LoCoMo-Plus dev routing variants),
  and installs Ollama only when an LLM job is selected.

### 12.2 Results

**Final test results, 2026-10-15: these are the numbers for slides.** They come from the frozen
configuration, with each test split run once. The full sheet with 95% intervals is
`results/RESULTS.md`, generated by `scripts/build_results.py` from `results/final/*.json`.

| Where | Result (test split) |
|---|---|
| Val gate before testing | adaptive 0.9917 = frozen value: **passed** |
| Controller, synthetic switch set (70 conversations, 420 probes) | evidence hit: adaptive **0.986** vs best single (RAG) 0.874, **+0.112 [+0.093, +0.129]**; vs always-hybrid 0.926, **+0.060 [+0.036, +0.088]**, using 29 fewer tokens. Selection macro-F1 0.331 (majority 0.180, random 0.195) |
| LoCoMo test (5 conversations, 966 questions) | evidence hit: adaptive 0.654, RAG 0.656 (a tie, −0.002 [−0.005, 0.000]), hybrid 0.627, window 0.084, summarization 0.049 |
| RAG read path, same test conversations | evidence hit **0.391 → 0.655** (compact headers + reranker) |
| LoCoMo test answer accuracy (230 random answerable questions, Qwen2.5-7B answering and judging) | judge score: adaptive 0.507 = RAG 0.507, hybrid 0.504, window 0.124, summarization 0.109. **Citable only after the human-agreement check.** |
| In-stream LoCoMo test | adaptive 0.704 = RAG; always-hybrid 0.718 (adaptive −0.013 [−0.029, −0.003]) |
| LoCoMo-Plus test (200 items) | cue hit: adaptive 0.140 = RAG = hybrid; the naive summary is best at 0.185 |
| RAG granularity, LoCoMo test at an equal 400-word budget | recall: segment 0.376, **adaptive 0.355**, turn 0.328. The earlier "adaptive best" (12.2, older table) **did not hold on test** |
| Coding demo | adaptive 2/2, fixed 6-exchange window 0/2 |
| Component evaluations on final code | summarization stale-fact leakage 0.00 vs 0.50 naive, signature retention 0.90 vs 0; contradiction flags P 0.82 / R 0.73 / F1 0.77; sliding window 59 wins / 0 losses vs recency at budget 100 |

**Earlier results (development history, superseded by the table above):**

| Where | Result |
|---|---|
| Coding demo (§9) | adaptive **2/2**, fixed 6-exchange window 0/2, always-window 1/2, always-summarization 2/2, always-RAG 2/2 |
| Controller, synthetic (180 probes) | evidence hit: adaptive **1.000** vs best single strategy (RAG) 0.900, **+0.10**; always-hybrid ties at 1.000. Selection macro-F1 0.35 |
| LoCoMo, 1,986 questions, NLI off | evidence hit: adaptive 0.443 vs RAG 0.444, a tie (almost every question routes to RAG); hybrid 0.358 |
| LoCoMo answer accuracy, Colab pilot (`eval/locomo/results_colab_pilot`) | Qwen2.5-7B answering and judging, 100 questions. Judge score: RAG 0.310, hybrid 0.315, adaptive 0.310, window 0.140, summarization 0.100. **Pilot only:** the sample was the first 50 questions per conversation (since replaced by a seeded random sample) |
| LoCoMo-Plus, 401 items | cue hit: adaptive 0.087 vs RAG 0.167 vs hybrid 0.185, a **negative result**: statement-style triggers are routed to summarization |
| Summarization (30 degradation traces, budget 1000) | structured + merge vs naive: loss 0.06 vs 0.37; symbol retention 0.90 vs 0.00; stale-fact leakage **0.00 vs 0.50** |
| Sliding window (budget 100) | gold-turn recall 0.719 vs recency-only 0.556 (59 wins / 0 losses) |
| RAG contradiction flags (184 pairs) | test P 0.82 / R 0.73 / F1 0.77 at threshold 0.95, chosen on dev |
| RAG granularity (LoCoMo, equal 400-word budget) | recall: adaptive 0.428, segment 0.421, turn 0.381 |

**Dev-split results, 2026-10-13.** These were used to choose settings; they are **not** test
results.

| Dev set | Result |
|---|---|
| LoCoMo dev (5 conversations, 999 questions), RAG read path | evidence hit, with adaptive equal to RAG: old headers **0.496** → compact headers 0.542 → **+ reranker 0.709** (answer in context 0.326 → 0.476; multi-hop 0.15 → 0.31). Adding one neighbour turn gave 0.735 but slightly *lower* answer-in-context and multi-hop, so it was not adopted |
| In-stream LoCoMo dev (1,018 questions, reranker on) | evidence hit: window 0.449, summarization 0.168, RAG 0.744, **hybrid 0.758**, adaptive 0.746. Fresh: window 0.828, hybrid 0.848, RAG 0.793. Late: RAG 0.697 |
| LoCoMo-Plus dev (201 items, 10 warm-up decision turns) | without reranker: RAG 0.164, hybrid 0.194, adaptive 0.169. With reranker: RAG 0.129, hybrid 0.164, adaptive 0.134 (current routing) or 0.164 (long chat / lossy summary → hybrid). The new `user_state` facts lifted summarization 0.090 → 0.109 |
| Synthetic controller val (tuning grid, 1,512 configs) | best val evidence hit 0.992 with the current routing at `low_pressure` 0.9 and `min_dwell_turns` 3 (val macro-F1 0.327 vs 0.263 for the old defaults). Routing long chat to hybrid: 0.933 |
| Coding demo with the frozen config | **1/2 with the reranker on every turn** (hybrid misses the duplicate-function trap), 2/2 without it, and **2/2 with the reranker skipped for code tasks** (the adopted setting) |

### 12.3 Findings that narrow the §6 claims

Present these as they are; don't argue around them.

- **§6.1 controller:** on pure-recall benchmarks (LoCoMo) adaptive *ties* the best fixed strategy,
  because the right choice is always RAG. Its gains show on mixed workloads: the coding traps and
  the synthetic switch set. Frame it as **"no regret when one strategy is right, a gain when the
  conversation changes type."**
- **§6.2 sliding window:** **equal weights are not optimal** in the ablation; relevance at 0.5 or
  more wins. Weights should be selected on dev, not defended as equal.
- **§6.4 RAG:**
  - **The NLI model cannot tell code identifiers apart**, so code-symbol staleness uses an exact AST
    signature diff (`verifier="signature_diff"`).
  - **The NLI scores are made bidirectional** (minimum of both directions). That removed the
    one-directional false positives seen in the demo.
- **The reranker is a trade-off, not a free gain.** It lifts LoCoMo dev RAG from 0.542 to 0.709, but
  it hurts LoCoMo-Plus (0.164 → 0.129) and code retrieval. It was trained on web QA (MS MARCO), so it
  ranks prose above code blocks. In the demo, hybrid's half-budget RAG slice then loses the existing
  definition.
- **Routing has little room on LoCoMo-style QA.** Hybrid and RAG retrieve nearly the same evidence,
  so even perfect fresh/late routing would reach only about 0.769, against 0.758 for always-hybrid.
  - The topic-shift flag barely separates fresh from late questions: it fires on 47% vs 62% of them.
  - Similarity to the last turns separates them better (AUC 0.74), but gave only +0.004, so it was
    not added.
- **Test-split findings:**
  - The controller's gain is clear and significant on mixed workloads: +0.112 over the best single
    strategy, and +0.060 over always-hybrid while using fewer tokens.
  - On LoCoMo-style recall it ties RAG, and always-hybrid is marginally better in-stream.
  - Adaptive chunking is **not** better than fixed segments at an equal word budget on test. Present
    granularity as an engineering choice (fewer tokens per hit than segments), not a claim.
- **Judges:** a 7B judge is fine for grading answers. It is **not** usable for the controller's
  strategy oracle: it agreed with the objective oracle at only 0.33 (kappa 0.11). That half of the
  dual-source oracle needs a much stronger judge (70B class or Claude).

### 12.4 Rules adopted during the build

- **Dev/test discipline.**
  - LoCoMo: conversations at even index (1, 3, 5, 7, 9) are dev, odd are test.
  - LoCoMo-Plus: even item ids are dev, odd are test.
  - The synthetic sets are split at conversation level (train / val / test in `splits.json`).
  - Tune only on dev, and report test once.
  - The coding demo is a check, never a tuning set.
- **Selection rule for controller routing, declared before the results:** the best average evidence
  hit across the dev sets, equally weighted. The dev sets are synthetic val, LoCoMo-Plus dev and
  in-stream LoCoMo dev, plus plain LoCoMo dev, which was added before deciding because it makes the
  choice stricter.
  - Result: keep the current routing (long chat → summarization, lossy summary → RAG,
    questions → RAG) with `low_pressure` 0.9 and `min_dwell_turns` 3. That averages 0.645, against
    0.638–0.640 for the alternatives.
- **Non-committing probes.** Evaluation questions are probes (`user_turn(..., remember=False)`): they
  never change turn counts, controller history or escalations.
- **The §5 rule is enforced structurally.** `RuleBasedController.decide()` receives only the
  `TurnSignal`, and escalations apply on the next turn only.
- **Fair comparisons only.** Every system or strategy compared gets the same conversations, the same
  token budget, the same answering model and the same judge. Never compare against numbers copied
  from other papers.
- **Commits are authored by the student only**, with no AI attribution lines.

### 12.5 Open work (in this order)

0. **Done 2026-10-15:** reranker scope settled (non-code turns only, val gate passed) and every
   test split run once (12.2). **No more tuning on any test split**; any change from here is v2.
1. **Human agreement labelling** of the test-answer judge: the sheets are in
   `runs/colab3/final/human_agreement/` (24 rows per annotator; keep `key.json` private). Score
   them with `python -m eval.human_agreement.score --sheets <folder>`.
2. **Demo package** for the presentation: the coding session on the live dashboard, plus a static
   fallback.
3. **A stronger judge** for the controller's strategy oracle: a pay-per-token 70B model (about $1) or Claude.
4. **External baselines** in the same harness: Mem0, LangChain summary-buffer memory, and full
   context. Measure answer accuracy, write-time LLM calls and the coding traps.
5. **An OpenAI-compatible proxy** so CEAI can sit in front of any chat app or agent, with the
   dashboard live during the presentation demo.
6. **Larger answer-accuracy sample** with a stronger model, for the final report (not needed for
   Progress Presentation 1).

### 12.6 Branches

- `development` is the integration branch.
- Each component has a working branch: `retrieval-augmented`, `summarization`,
  `sliding-window-conversation-manager` and `runtime-controller`.
- Component work merges into `development`, normally by pull request.
