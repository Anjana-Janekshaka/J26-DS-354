# CEAI — Adaptive Memory Middleware — Build Guide

**Status (2026-10-17): built, frozen and evaluated; the v4 improvement round is in progress (§12.11).
A new session should read §12.0 first, then §12.11, then §6.5 for the current claims.** **Read this whole file before writing any code.** This is the single source of truth for what to
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

### 6.5 Literature update and narrowed claims (2026-10-15; supersedes 6.1–6.4 where they differ)

These claims were re-checked against the team's 22-paper reading set and the frozen test results.
The paper-by-paper table, MemStrata's staleness metrics on our data and the derived improvements are
in `docs/related_work.md`. **Present these lines, not the older wording.**

| Component | Claim to present | Closest systems and the difference | Number |
|---|---|---|---|
| **Controller (headline)** | **Per-turn switching between three memory paradigms (sliding window, hierarchical summarization, RAG), with a logged, explainable, overridable decision and no LLM in the decision path** | FluxMem / MemCon (6.1); **MemGAS** and **RMM** adapt *within* retrieval; **Self-RAG** decides retrieve-or-not; **MemGPT** lets the LLM page memory (opaque, costly); **MoMA** routes models, not memory | Mixed workloads: **+0.112** over the best single strategy and **+0.060** over always-hybrid with fewer tokens (Pareto: `results/figures/pareto_controller.png`); LoCoMo: ties the best strategy; decision latency about 0.1 ms |
| Sliding window | Unchanged (6.2): an evaluation claim, not a mechanism claim | **Generative Agents** (recency + importance + relevance: cite as the origin), AFM, LUFY (learned weights), MemoryBank (forgetting curve) | 59 wins / 0 losses vs recency-only; the ablation selects the weights |
| Summarization | Unchanged: the live loss score used as a control signal (6.3) | ProMem (post-hoc only); the keyed merge sits next to **MemStrata** (deterministic keys), **Mem0** (LLM UPDATE) and **Zep** (LLM invalidation) | Stale-fact leakage 0.00 vs 0.50; signature retention 0.90 vs 0 |
| RAG claim 1 (granularity) | **Withdrawn as a performance claim.** It did not beat fixed segments on test (recall at 400 words: 0.355 vs 0.376). Kept as a design element | **MemGAS** (read-time entropy router), **SeCom** (segments plus denoising), LycheeMemory V2 | — |
| RAG claim 2 (staleness) | **Extraction-free, LLM-free staleness flagging on raw conversation chunks: an exact structural check (code signature) where a key exists, calibrated NLI where none does** | **MemStrata** needs clean (subject, relation, object) triples and reports that NLI/LLM judges leak; **Zep** needs LLM-extracted edges and an LLM verifier; CLEAR / TSM (6.4) | P 0.82 / R 0.73. At equal F1, NLI cuts wrongly retired current facts from **0.83** (similarity only) to **0.23**. **Stale-fact leak 0.27: state it plainly** |

### 6.6 Presentation framing (2026-10-17; from `docs/zero_cost_improvement_roadmap.md` §6)

This is how to *say* the §6.5 results. **The numbers are unchanged, and so is the frozen system.**

- **Unifying claim, the lead slide:** *"The whole memory substrate (write, retrieve and route) makes
  zero generative LLM calls."*
  - The summarizer is rule-based; the NLI checker and the reranker are small, non-generative models;
    the controller is rules.
  - Measured: memory for a LoCoMo conversation is built in **about 6 s with 0 LLM calls**, against
    **about 972 s and 54 calls for Mem0** (162× slower) and about 704 s and 69 calls for the
    summary buffer. Source: `results/final/cost_latency.json`, `results/figures/memory_build_time.png`.
  - Caveat: CEAI's timing excludes the NLI staleness check, which was off in that LoCoMo run.
  - Contrast: Mem0 extracts with an LLM, Zep builds graph edges with an LLM, and MemGPT lets the LLM
    page its own memory.
- **Controller: order the claims so the universally true part leads:**
  - First: *"Same accuracy as the best fixed strategy, at zero marginal cost, fully explainable"*
    (true on every benchmark).
  - Then: *"When the conversation changes type mid-way, also more accurate"* (+0.112 on the mixed
    set, 2/2 vs 0/2 in the demo).
  - Do not lead with the synthetic-set number.
- **RAG: drop adaptive granularity from the novelty slide entirely.** Let the staleness claim carry
  the component alone (P 0.82 / R 0.73, LLM-free, no triples needed). Granularity returns only if a
  pre-registered learned-weight version beats fixed segments.
- **Summarization: lead with the measured result.** *"It measures what it is about to lose, in real
  time (0.91 correlation with actual loss), and that signal switches strategy."* Then stale-fact
  leakage 0.00 vs 0.50.
- **Sliding window: claim unchanged.**
  - **Known inconsistency, to fix after Monday:** the ablation favours relevance-heavy weights, but
    the frozen system ships equal weights.
  - Fixing it means changing the frozen system, and the ablation set has no dev/test split. So it
    needs a dev/test split of that set and a pre-registration first (roadmap §6.1). Until then, say:
    *"weights are runtime config; the ablation shows relevance matters most."*
- **Manual override: verified live (2026-10-17).**
  - A POST to `/api/override` makes the next decision use the requested strategy, marked
    `OVERRIDE by …` in the rationale.
  - A `next_turn` override expires after one turn, the dashboard shows the overridden decision, and
    invalid requests get HTTP 400.

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

## 12. Build log and current status (as of 2026-10-17)

Sections 1–11 are the original plan; §6.5 holds the claims as they now stand. This section records
what was built and measured, and the decisions later work must respect. **In a new session, read
12.0 first.** Name components by role in code and docs, never by person.

### 12.0 Snapshot: read this first

- **State:**
  - All of §3 is built, integrated and tested (89 fast tests). The system configuration is
    **frozen**, and every test split was run **once**.
  - Progress Presentation 1 **moved to Wednesday 2026-10-21**. The extra days are used for the
    roadmap items as a pre-registered **v4 round (§12.11)**; the frozen system stays the system of
    record until v4 passes all its gates.
- **Headline results** (test splits, frozen system; 95% bootstrap intervals over conversations):
  - **Controller, on mixed-workload conversations:** evidence hit **0.986** vs best single strategy
    0.874 (**+0.112 [+0.093, +0.129]**), and **+0.060** vs always-hybrid while using fewer tokens.
  - **Coding demo:** adaptive catches **2/2** traps; a fixed 6-exchange window catches **0/2**.
  - **LoCoMo:** adaptive **ties** the best fixed strategy (RAG). The RAG read path itself improved
    **0.391 → 0.655** evidence hit on the same test conversations.
  - **External baselines** (same 230 LoCoMo test questions, same model, judge and budget):
    - **vs Mem0 (corrected run):** judged accuracy not significantly different (CEAI 0.507 vs
      0.467), token-F1 **+0.129** (significant).
    - **Write cost:** CEAI makes **0 LLM calls to store memory**; Mem0 makes about 54 per
      conversation.
    - **vs fixed-chunk RAG and a LangChain-style summary buffer:** CEAI significantly better on
      both metrics.
  - **Components:**
    - Summarization: stale-fact leakage **0.00 vs 0.50** naive.
    - RAG staleness flags: precision **0.82**.
    - Sliding window: **59 wins / 0 losses** vs recency-only.
- **Tried and not adopted** (all pre-registered or dev-only, honest negatives): v2 hybrid retrieval,
  MMR, v3 (hybrid for question turns + observations). See 12.4.
- **Left before Wednesday:** finish the v4 round (§12.11: gates, length test, BEAM, two Colab jobs),
  write the slide text from the final numbers, the teammates' labelling sheets, and a merge into
  `development`. The demo package is **done** (`demo/coding_session/present.py`, `docs/DEMO_GUIDE.md`).
- **Presentation framing** (how to state the results; 2026-10-17): §6.6. **Post-Monday improvement plan:**
  `docs/zero_cost_improvement_roadmap.md`.
- **Non-negotiable rules** (12.7):
  - Never tune on test; pre-register any new candidate and gate it on dev/val.
  - Commits are authored by the student only, with no AI attribution.
  - No personal names in code.

### 12.1 What exists

- **Packages** (all of §3), wired end to end in `integration/pipeline.py`: contracts, conversation
  manager, sliding window, summarization, retrieval, rule-based controller, decision logger and
  dashboard (live server and static export).
  - The P2 items are explicit `TODO: v2` stubs: the LR/RF/GBDT controller, loss Method 2 and the
    summary repair loop.
- **`demo/coding_session/`** was rebuilt from the §9 description; the original `ceai-demo/`
  scaffold was not available.
  - `python -m demo.coding_session.run_demo` writes `runs/demo/` (decision log, dashboard HTML,
    `results.json`).
- **RAG read path** (`RetrievalConfig`):
  - Compact chunk headers `[turns: t0012]`.
  - A cross-encoder reranker (`cross-encoder/ms-marco-MiniLM-L-6-v2`), **skipped for code-task
    turns** (`rerank_skip_task_types`), because a web-QA reranker ranks prose above code.
  - Optional and **off in the frozen system:** neighbour turns, hybrid BM25 (`hybrid`,
    `hybrid_task_types`, `packages/retrieval/lexical.py`), MMR (`mmr_lambda`) and observations
    (`observations`, fed from the summarizer by the integration layer).
- **Controller:** `RuleConfig` routing options (`long_chat_strategy`, `loss_escalation_target`,
  `qa_strategy`). Rules also see the TurnSignal topic-shift flag, which is Tier 0, so §5 holds.
- **Frozen configuration:**
  - `eval/synthetic/controller/frozen_rule_config.json` (tuned on train + val), loaded by
    `eval/frozen.py`.
  - `CEAI_SYSTEM` selects the system variant: `frozen` (default), `v2_hybrid` or
    `v3_qa_hybrid_obs`. Every result file records which system produced it.
- **Evaluation harnesses** (each writes `summary.json` plus per-item rows):
  - `eval/locomo/run.py` (primary; `--split dev|test`; `--llm --judge-answers` for answer accuracy)
  - `eval/locomo/stream.py` (in-stream questions)
  - `eval/locomo_plus/run.py` (supplementary)
  - `eval/synthetic/{controller,sliding_window,summarization,retrieval}`, with
    `eval/synthetic/retrieval/staleness.py` for the MemStrata-style metrics
  - `eval/baselines/` (external baselines: fixed-chunk RAG, summary buffer, Mem0 via `mem0ai`,
    full context)
  - `eval/v2_gate.py` (pre-registration gates G2–G4)
- **LLM tooling (free):**
  - `integration/llm_client.py`: OpenAI-compatible client with a disk cache.
  - `eval/judge.py`: correct / partial / wrong judge.
  - `eval/human_agreement/`: blind labelling sheets and Cohen's kappa. Judge scores are citable only
    if kappa is at least 0.6.
- **Colab workflow:**
  - `notebooks/free_gpu_eval.ipynb` is generated by `scripts/build_notebook.py`. Jobs are switched
    by the `RUN` dict; Ollama starts or restarts via `start_ollama()`.
  - Package the code with `scripts/package_for_notebook.py` (zip with a `BUILD_INFO.txt` stamp).
  - On Colab: upload the zip to My Drive, upload the notebook, set a T4 GPU, Run all, check the
    `CODE VERSION` line, then download `ceai_results.zip`.
- **Results tooling:**
  - `scripts/build_results.py` writes `results/RESULTS.md` from `results/final/*`.
  - `scripts/plot_pareto.py` writes `results/figures/pareto_*.png`.
- **Docs:**
  - `docs/SYSTEM_OVERVIEW.md`: how the system is built, every directory and file, the code ideas,
    and a timeline of the changes.
  - `docs/related_work.md`: the 22-paper review, a threat assessment and the paper-derived
    experiments.
  - `docs/baselines_protocol.md`: the baselines protocol, its amendment and the outcomes.
  - `docs/v2_hybrid_preregistration.md` and `docs/v3_preregistration.md`: each with its gates and
    outcome.

### 12.2 Final test results (frozen system; the numbers for slides)

The full sheet with intervals is `results/RESULTS.md`, and the sources are in `results/final/`.

| Where | Result (test split, run once) |
|---|---|
| Val gate before testing | adaptive 0.9917 = frozen value: **passed** |
| Controller, synthetic switch set (70 conversations, 420 probes) | adaptive **0.986** vs best single (RAG) 0.874, **+0.112 [+0.093, +0.129]**; vs always-hybrid 0.926, **+0.060 [+0.036, +0.088]** with 29 fewer tokens. Selection macro-F1 0.331 (majority 0.180, random 0.195) |
| LoCoMo test (5 conversations, 966 questions) | evidence hit: adaptive 0.654, RAG 0.656 (tie, −0.002 [−0.005, 0.000]), hybrid 0.627, window 0.084, summarization 0.049 |
| RAG read path, same test conversations | **0.391 → 0.655** (compact headers + reranker) |
| LoCoMo answer accuracy (230 random answerable test questions; Qwen2.5-7B answering and judging) | judge: adaptive 0.507 = RAG 0.507, hybrid 0.504, window 0.124, summarization 0.109. Token-F1 adaptive 0.406 |
| In-stream LoCoMo test | adaptive 0.704 = RAG; always-hybrid 0.718 (adaptive −0.013 [−0.029, −0.003]) |
| LoCoMo-Plus test (200 items) | cue hit: adaptive 0.140 = RAG = hybrid; the naive summary is best at 0.185 (known weakness) |
| RAG granularity at an equal 400-word budget | recall: segment 0.376, adaptive 0.355, turn 0.328, so **adaptive chunking is not better** |
| Coding demo | adaptive 2/2, fixed 6-exchange window 0/2 |
| Summarization (30 degradation traces) | stale-fact leakage **0.00 vs 0.50** naive; signature retention **0.90 vs 0**; the live loss score tracks deletion (Spearman 0.91) |
| RAG staleness flags (184 pairs; threshold chosen on dev) | **P 0.82 / R 0.73 / F1 0.77**. At equal F1, NLI wrongly retires 23% of current facts vs 83% for similarity only. **Stale-fact leak 0.27** |
| Sliding window (40 conversations, 360 probes) | budget 100: recall 0.719 vs recency-only 0.556 (**59 wins / 0 losses**); the ablation ranks equal weights 15th of 35 (relevance-heavy wins) |

Pareto charts (cost vs evidence hit): `results/figures/pareto_controller.png`,
`results/figures/pareto_locomo.png`.

### 12.3 External baselines (`docs/baselines_protocol.md`; results in `results/final/baselines*`)

Conditions: the same 230 LoCoMo test questions as CEAI's frozen answer run, the same Qwen2.5-7B
answering and judging, the same answer prompt and the same 1,024-token memory budget. Full
context is a ceiling run on 60 of the questions. Paired as CEAI − system:

| System | Judge | CEAI − system (judge) | Token-F1 | CEAI − system (F1) | LLM calls to store memory / conversation |
|---|---|---|---|---|---|
| **CEAI (frozen)** | **0.507** | — | **0.406** | — | **0** |
| **Mem0 (corrected run)** | 0.467 | +0.039 [−0.060, +0.127] **(n.s.)** | 0.278 | **+0.129 [+0.038, +0.210]** | about 54 (15–20 min) |
| Fixed-chunk RAG | 0.433 | **+0.074 [+0.017, +0.132]** | 0.343 | **+0.064 [+0.026, +0.103]** | 0 |
| Summary buffer (LangChain-style) | 0.096 | **+0.411 [+0.310, +0.494]** | 0.066 | **+0.340 [+0.240, +0.422]** | about 69 |
| Full context (60 questions) | 0.417 | −0.067 [−0.183, +0.050] (n.s.) | 0.195 | **+0.182 [+0.064, +0.299]** | 0 (about 24k tokens per question) |

- **Mem0 run 1 under-counted Mem0.** This harness's 1,500-token output limit cut off 8.8% of its
  extractions. The **corrected run** (limit 8,000, declared as a protocol amendment before running)
  is the headline. **Do not claim "CEAI beats Mem0 on accuracy".** Claim instead: *"same judged
  accuracy, higher exact-answer F1, zero write-time LLM calls"*.
- **Judge scores become citable only after the human-agreement check;** until then, lead with
  token-F1.
- Not run (setup too heavy for free Colab before the deadline): Zep, LangMem, Letta/MemGPT and A-Mem.
  They are cited only as related work, never as numbers next to ours.

### 12.4 Experiments that were not adopted (honest negatives; the frozen system is unchanged)

| Experiment | How it was evaluated | Outcome |
|---|---|---|
| **v2: hybrid BM25 + dense on every turn** (`docs/v2_hybrid_preregistration.md`) | Pre-registered; gates G1 demo, G2 synthetic val, G3 LoCoMo-Plus dev | LoCoMo dev RAG evidence **+0.052 [+0.018, +0.088]**, but **G3 failed**: LoCoMo-Plus dev −0.040 [−0.070, −0.015]. No test run |
| **MMR ordering** | LoCoMo dev | +0.002 [−0.008, +0.009]: no effect |
| **v3: hybrid for `qa` turns + summarizer facts as RAG observations** (`docs/v3_preregistration.md`) | Pre-registered; G1–G3 plus G4 LoCoMo dev answer accuracy | **G3 failed badly** (LoCoMo-Plus dev 0.134 → 0.020: short observations crowd out the second line of two-line cues). Dev answer accuracy only +0.007 [−0.058, +0.069]. No test run |
| Neighbour turns around RAG hits | LoCoMo dev | Evidence 0.735 vs 0.709, but answer-in-context and multi-hop slightly lower; not adopted |
| Reranker on every turn | LoCoMo dev + demo | +0.17 on LoCoMo dev, but the demo fell to 1/2 (it ranks prose above code). **Adopted with a code-task skip**, which keeps the demo at 2/2 |
| Routing variants (long chat → hybrid, loss → hybrid, qa → hybrid) | Pre-declared dev selection rule across four dev sets | The current routing won (0.645 vs 0.638–0.640); frozen at `low_pressure` 0.9, `min_dwell_turns` 3 |

**Lesson worth presenting:** lexical retrieval helps explicit recall and hurts implicit cues. No
single retrieval setting wins everywhere, which supports adaptivity.

### 12.5 The four components: what to present

| Component | Claim (from §6.5) | Closest work | Evidence | Caveat to prepare |
|---|---|---|---|---|
| 1. Dynamic sliding window (+ conversation manager) | An evaluation claim: light 4-factor scoring beats recency; the ablation picks the weights | Generative Agents (origin of recency + importance + relevance), AFM, LUFY | 59 wins / 0 losses vs recency; 0.719 vs 0.556 | Equal weights are not optimal; weights are runtime config |
| 2. Hierarchical summarization | The live loss score is a **control signal** that triggers a switch | ProMem (post-hoc only); the merge sits next to MemStrata, Mem0 and Zep | Stale-fact leakage 0.00 vs 0.50; signature retention 0.90 vs 0; the demo's renamed-API catch came from loss 0.59 → RAG | Alone, it is weak at detail recall (LoCoMo 0.05); the controller compensates |
| 3. RAG | **LLM-free staleness flagging on raw conversation** (structural for code, calibrated NLI otherwise) | MemStrata (needs triples), Zep (LLM-extracted edges) | P 0.82 / R 0.73; wrongly retired facts 83% → 23%; read path 0.391 → 0.655 | Adaptive chunking withdrawn as a claim; 27% stale-fact leak; v2 / MMR / v3 not adopted |
| 4. ASSE controller (headline) | **Per-turn switching across three paradigms, logged, explainable, overridable, no LLM in the decision** | FluxMem, MemCon, MemGAS, RMM, Self-RAG, MemGPT, MoMA | +0.112 over the best single strategy; +0.060 over always-hybrid with fewer tokens; demo 2/2 vs 0/2; ties RAG on LoCoMo; about 0.1 ms per decision | The largest win is on our own synthetic set; answer with the train/val/test discipline and the deterministic demo |

**One-line message:** *memory systems lock in one strategy; choosing per turn wins on mixed
conversations, costs nothing on uniform ones, and every decision is explainable.*

### 12.6 Findings that narrow the §6 claims

- On pure-recall benchmarks (LoCoMo) adaptive *ties* the best fixed strategy, because the right
  choice is always RAG. Its gains show on mixed workloads. Frame it as **"no regret when one
  strategy is right, a gain when the conversation changes type."**
- Sliding-window equal weights are not optimal; the weights are selected, not defended.
- The NLI model cannot tell code identifiers apart, so code staleness uses an exact AST signature
  diff. NLI scores are bidirectional (minimum of both directions).
- The reranker is a trade-off: it helps conversational recall and hurts code and implicit cues.
- Routing has little room on LoCoMo-style QA: a perfect fresh/late router would reach about 0.769
  vs 0.758 for always-hybrid. The topic-shift flag is a weak signal.
- A 7B judge is usable for grading answers but **not** for the controller's strategy oracle
  (agreement 0.33, kappa 0.11).

### 12.7 Rules adopted during the build

- **Dev/test discipline.**
  - LoCoMo: conversations 1, 3, 5, 7, 9 are dev; 2, 4, 6, 8, 10 are test.
  - LoCoMo-Plus: even item ids are dev, odd are test.
  - Synthetic sets: train / val / test in `splits.json`.
  - The coding demo is a check, never a tuning set.
  - **Test splits were used on 2026-10-15 for the frozen system. Do not tune anything on them.**
- **Pre-registration for any new candidate:**
  - Write `docs/<name>_preregistration.md` (config, gates, test runs, reporting rule) and commit it
    *before* any run.
  - Gates run on dev/val (`eval/v2_gate.py`); the notebook stops itself if a gate fails.
  - Every result is reported whatever its sign.
- **Fair comparisons only:** the same conversations, questions, budget, answering model and judge.
  Never compare with numbers copied from other papers. Correct any handicap to a baseline (as with
  Mem0), declared first.
- **§5 is enforced structurally:** `RuleBasedController.decide()` sees only the `TurnSignal`, and
  escalations apply on the next turn.
- **Non-committing probes:** evaluation questions use `user_turn(..., remember=False)`.
- **Git:**
  - Commits are authored by the student (Manuga Romal), with **no AI attribution lines**.
  - Work happens on `retrieval-augmented`; merge `development` in first, then fast-forward
    `development`.
  - Run `pytest -m "not models"` before every commit.
- **No personal names** in code or docs other than this file's team line.

### 12.8 Open work

1. **Demo package: done 2026-10-17** (`python -m demo.coding_session.present`, static fallback,
   `docs/DEMO_GUIDE.md`). Still to write:
   - Slide text: four component slides per §11, the integration (CAUGHT/MISSED) slide, the Pareto
     and baselines slides, and Q&A answers.
2. **Human-agreement labelling:**
   - The sheets for the test answers are in Colab output `ceai_runs/final/human_agreement/` (local copy:
     `runs/colab3/final/human_agreement/`, which is git-ignored; keep `key.json` private). If
     they are lost, regenerate them from `results/final/locomo_qa_test_questions.jsonl` with
     `eval.human_agreement.make_sheets`.
   - Four annotators, about 20 minutes each.
   - Score with `python -m eval.human_agreement.score --sheets <folder>`.
3. **Merge into `development`:** fast-forward after the latest commits on `retrieval-augmented`.
4. **Later (after the v4 round):**
   - A stronger answering model and judge for every system (needs a free Groq/OpenRouter key from
     the user, set as an environment variable, never pasted in chat).
   - A fix for the held-out demo misses (renamed-to-new-name functions, changed constants,
     non-Python signatures), developed on new dev scenarios and checked on a fresh held-out batch.
   - LangMem / A-Mem baselines.
   - A controller rule for "recent cue → keep the window" (on LoCoMo-Plus, cues fewer than 50 turns
     back are lost to RAG routing).
   - An OpenAI-compatible proxy for a live chat demo.

### 12.9 How to run things

- **Setup:** `python -m venv .venv`, then `.venv/Scripts/pip install -e ".[dev]"`. Fast tests:
  `pytest -m "not models"`.
- **Demo:** `python -m demo.coding_session.run_demo` (frozen system, about 2 minutes on CPU).
  Live dashboard: `python -m dashboard.server --log-dir runs/demo`.
  **Presentation:** `python -m demo.coding_session.present` (see `docs/DEMO_GUIDE.md`).
  Held-out sessions: `python -m demo.coding_session.run_scenarios`.
- **v4:** `CEAI_SYSTEM=v4` on any harness; system gates `python -m eval.v4_gate` (resumes).
  `CEAI_LLM_POLICY=assisted` turns on LLM-written L2/L3 summaries (needs an LLM).
- **Results sheet:** `python scripts/build_results.py --colab <unzipped Colab results folder>`.
  Charts: `python scripts/plot_pareto.py`.
- **Anything needing an LLM or a GPU:**
  1. Edit `RUN` in `scripts/build_notebook.py`.
  2. Run `python scripts/build_notebook.py` and `python scripts/package_for_notebook.py`.
  3. Upload the zip and the notebook to Colab (T4), Run all, and check the `CODE VERSION` line.

### 12.10 Branches

- `development` is the integration branch.
- Component branches: `retrieval-augmented` (where this work happens), `summarization`,
  `sliding-window-conversation-manager` and `runtime-controller`.
- Component work merges into `development`, normally by pull request.

### 12.11 The v4 round (2026-10-17, in progress)

The presentation moved to Wednesday, so the roadmap (`docs/zero_cost_improvement_roadmap.md`) is
being worked through now under the §12.7 rules. Plan and outcomes: `docs/v4_preregistration.md`;
code map: `docs/SYSTEM_OVERVIEW.md` §12. **Until every gate below passes, every number in §12.2
stays the headline and the frozen system is unchanged.**

**Done (each pre-registered, test run once):**

| Item | Result | Status |
|---|---|---|
| 12 held-out coding sessions, 26 traps (`docs/demo_scenarios_preregistration.md`) | Adaptive **16/26**, fixed window **3/26**, always-hybrid 18/26; every duplicate-function trap caught (7/7) | Report as is. Do **not** claim "beats every fixed strategy" here |
| Sliding-window weights chosen on a dev half (relevance 0.5, importance 0.5) | Test recall **1.000** vs equal weights 0.706 vs recency 0.556 | In v4. Resolves the §6.6 inconsistency if v4 passes |
| Staleness ensemble (NLI both directions + similarity + change cue) | Test P **1.00** / R 0.69 / F1 0.81 (was 0.82 / 0.73 / 0.77); wrongly retired facts **0%** (was 23%); leak 0.31 (was 0.27) | In v4 |
| Dev-tuned chunk-boundary weights | Test recall at 400 words **0.399** vs fixed segments 0.376 (hand-set 0.355) | In v4. Granularity returns as an engineering result, not a learned-model claim |
| Learned controller (LR/RF/GBDT, `packages/controller/model_based.py`) | Val hit 0.93 vs rules 0.99: **gate failed** | Not run on test; rules stay |
| `llm_policy` toggle (`strict` default / `assisted` = LLM writes L2/L3 only) | Implemented; the controller sees identical inputs in both modes, and differences come only via logged next-turn loss escalations | Evaluation is a Colab job |
| Live presenter mode + demo guide | 2/2 vs 0/2 live, with override and audience questions | Done |

**Running or waiting:**

| Item | Where | Notes |
|---|---|---|
| v4 system gates G1–G4 (`eval/v4_gate.py`) | laptop | **G1 passed** (2/2, 16/26 = frozen). G2 synthetic val, G3 LoCoMo-Plus dev, G4 LoCoMo dev pending. All pass → v4 test run once and v4 becomes the system of record; any failure → v4 stays dev-only |
| Length test (`eval/synthetic/controller/length.py`) | laptop | Does the adaptive advantage grow with conversation length? New family-C conversations, frozen system |
| BEAM (`eval/beam/`, `docs/beam_preregistration.md`) | laptop | Independent benchmark (other authors), never tuned on; frozen system |
| Mem0 on the coding traps (`docs/mem0_coding_preregistration.md`) | Colab `mem0_coding_traps` | Is a real competitor also caught out by the traps? |
| `llm_policy` strict vs assisted (`docs/llm_policy_preregistration.md`) | Colab `llm_policy_dev` | 20 LoCoMo-Plus dev items (amended from 60 before running, for runtime): a pilot |
| Stronger model and judge (roadmap 1.1/1.2) | later | Needs the user's free API key |

When results arrive: record them in the relevant pre-registration file and here, regenerate
`results/RESULTS.md`, then write the slide text.
