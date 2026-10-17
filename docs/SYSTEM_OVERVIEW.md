# CEAI Adaptive Memory Middleware: system overview

**What this document is:** how the system is built, what every directory and file does, the main
ideas in the code, and how the project changed between 2026-10-06 and 2026-10-17.

**Work in progress (2026-10-17):** the v4 round. See §12 at the end of this file for what is being
done now, what has finished and what is still running.

**How it relates to the other documents:**
- `CLAUDE.md` is the build plan and the current status (read its §12.0 for the snapshot).
- `results/RESULTS.md` holds the numbers.
- `docs/related_work.md` holds the literature positioning.

This file explains the *code*.

---

## 1. The idea in one paragraph

A chat assistant can only show the model a limited amount of earlier conversation. Existing memory
systems pick **one** way of choosing that context at design time:
- keep the most recent messages (**sliding window**),
- compress the history (**summarization**), or
- search the history for relevant pieces (**retrieval, RAG**).

Conversations change character as they go: a coding session moves between debugging, building
something new and chatting. **CEAI decides, at every turn, which of the three strategies (or a
window + RAG hybrid) to use.** It decides from cheap signals available before any strategy runs,
and every decision is logged with a human-readable reason and can be overridden by a person. No
LLM is involved in the decision.

---

## 2. How one turn flows through the system

```
user message
    │
    ▼
Conversation Manager ── counts turns and tokens, classifies the task type
    │                   (chat / qa / debugging / code_generation / code_refactor /
    │                   exploration), detects topic shifts
    │ publishes a TurnSignal on the bus
    ▼
┌───────────────────────┬───────────────────────┬───────────────────────┐
│ Sliding window        │ Summarization          │ Retrieval (RAG)       │  all three build a
│ scores and picks      │ L1/L2/L3 summary +     │ reranked search over  │  candidate context
│ recent turns          │ live loss score        │ past chunks + stale   │  in parallel
│                       │                        │ flags                 │
└───────────┬───────────┴───────────┬────────────┴───────────┬───────────┘
            │ StrategyModuleOutput  │                        │
            ▼                       ▼                        ▼
ASSE controller ── decides from the TurnSignal ONLY (never from this turn's
    │              module outputs: the "§5 rule")
    │ ControllerDecision (strategy + rationale + override info)
    ├──► LLM interface: builds the prompt from the chosen strategy's context
    ├──► Decision logger: append-only JSONL record
    └──► Dashboard: timeline, rationale, per-module panels
after the turn: Tier 2 signals (summary loss too high, stale facts flagged)
    → escalation events → considered by the controller on the NEXT turn
```

**The rule that makes the controller trustworthy (§5 of CLAUDE.md):** a module's quality signal
(for example "the summary lost too much") only exists *after* that module ran for the turn. Using it
to choose that same turn's strategy would be circular. So the controller sees only pre-decision
signals, and quality signals become **escalations for the next turn**. This is enforced in the code
itself: `RuleBasedController.decide()` receives only a `TurnSignal`.

---

## 3. Project structure

```
middleware/
├── CLAUDE.md                  build plan + current status (start at §12.0)
├── README.md                  short summary, how to run, headline results
├── pyproject.toml             package definition; packages live under packages/
├── packages/                  the system itself: one folder per component
│   ├── contracts/             shared data types every component uses
│   ├── conversation_manager/  turn tracking, task-type classifier, signal bus
│   ├── sliding_window/        component 1: Dynamic Sliding Window
│   ├── summarization/         component 2: hierarchical summarization
│   ├── retrieval/             component 3: RAG with staleness flagging
│   ├── controller/            component 4: ASSE, the per-turn strategy selector
│   ├── decision_logger/       append-only decision log
│   └── dashboard/             live and static dashboard
├── integration/               wires the packages into one turn loop + LLM access
├── demo/coding_session/       the scripted coding session, 12 held-out sessions, live presenter mode
├── eval/                      every benchmark harness and metric
├── scripts/                   notebook builder, packaging, results sheet, charts
├── notebooks/                 generated Colab/Kaggle notebook (free GPU runs)
├── results/                   final, frozen results + figures (committed)
├── docs/                      related work, protocols, pre-registrations, this file
├── tests/                     89 fast tests + 1 real-model test
└── runs/                      local scratch outputs (git-ignored)
```

**Hard rule of the layout:** a package under `packages/` may import only `contracts` and its own
code. `tests/test_import_boundaries.py` checks this. Only `integration/` connects components to
each other, which is what lets four components (and four owners) live in one repo without
tangling.

---

## 4. The packages, file by file

### 4.1 `packages/contracts/`: the shared language

| File | What it does |
|---|---|
| `schemas.py` | Pydantic models for every message passed between components: `TurnSignal`, `ControllerFeatureVector`, `StrategyModuleOutput` (with per-module quality blocks), `ControllerDecision`, `DecisionLogRecord`, plus `ConversationTurn`, `EscalationEvent` and `OverrideRequest`. Validators enforce the contract (for example `loss_threshold_exceeded` must equal `loss_score > 0.15`) |
| `protocols.py` | The `StrategyModule` interface (`observe_signal`, `ingest`, `build_context`) that all three strategies implement |
| `text.py` | Shared text helpers (words, sentences, identifiers, code signatures via `ast`), the `Embedder` interface, and a dependency-free `HashingEmbedder` for tests |
| `tokens.py` | One token counter (tiktoken cl100k), so every budget is measured the same way |

### 4.2 `packages/conversation_manager/`

| File | What it does |
|---|---|
| `manager.py` | Registers each message, counts turns and tokens, and publishes a `TurnSignal`. `probe()` asks an evaluation question *without* changing the conversation state |
| `classifier.py` | Rule-based task-type classifier (phrasing patterns plus questions about known entities) and a topic-shift detector (embedding similarity drop) |
| `bus.py` | A tiny in-process publish/subscribe bus that broadcasts each `TurnSignal` to the modules |

### 4.3 `packages/sliding_window/`: component 1

| File | What it does |
|---|---|
| `scoring.py` | The four cheap scores per past turn: **relevance** (embedding similarity to the current message), **freshness** (recency decay, half-life in turns), **importance** (rule-based cues: definitions, decisions, constraints, errors, numbers; zero for "ok/thanks") and **state** (same topic segment as now) |
| `window.py` | Combines the four scores with configurable weights and keeps the best turns until the token budget is full, then restores chronological order |
| `config.py` | Runtime configuration: weights, half-life, budget behaviour. Weights can also come from `CEAI_SW_WEIGHTS` (the v4 system sets relevance 0.5 / importance 0.5) |
| `baselines.py` | Recency-only and fixed-token-window baselines for comparison |

### 4.4 `packages/summarization/`: component 2

| File | What it does |
|---|---|
| `records.py` | Structured records for three tiers: **L1** facts (verbatim), **L2** intent and decisions, **L3** profile. Fact kinds include code signatures, renames, attributes, constraints, decisions, requests, `user_state` (habits, feelings, goals) and statements |
| `extract.py` | Rule-based extraction: exact code signatures via `ast`, keyed attributes ("user.location"), renames, constraints, decisions, user states and the most informative statements per turn |
| `merge.py` | **Contradiction-resolving merge:** a new fact with the same key as an old one *supersedes* it (timestamped) instead of both staying. This is what keeps stale facts out of the summary |
| `engine.py` | The strategy module: rolls old turns into L1 records, groups them into L2, rebuilds L3, emits the most detailed tier that fits the budget, and computes the **live loss score** |
| `loss.py` | Loss score = how many "anchors" (identifiers, names, numbers, signatures) of the summarized turns are missing from the summary; plus Symbol Retention Rate for code |
| `generators.py`, `prompts.py` | An optional LLM-written tier generator with three distinct prompts (verbatim / intent / profile); falls back to the rule-based generator on bad output. `AssistedGenerator` is the `llm_policy="assisted"` mode: L1 stays rule-based, only L2/L3 are LLM-written, and it counts its calls |
| `naive.py` | A single-prompt naive summarizer baseline |

### 4.5 `packages/retrieval/`: component 3 (RAG)

| File | What it does |
|---|---|
| `engine.py` | The strategy module. **Write path:** embed each turn, decide the chunk boundary, index it, run the staleness check. **Read path:** search, rerank (skipped for code tasks), then pack chunks into the budget with compact `[turns: t0012]` headers. A stale chunk is never dropped silently: it is marked `[!] stale` and the newer chunk is pulled in next to it |
| `index.py` | FAISS `IndexFlatIP` (cosine on normalised vectors) with removable ids |
| `embedder.py` | Sentence-transformers `all-MiniLM-L6-v2` (uses the GPU when present) |
| `chunking.py` | Write-time granularity decision (turn vs multi-turn segment) from a boundary score. The v4 system uses boundary weights tuned on LoCoMo dev |
| `contradiction.py` | **Two-stage staleness check:** (1) a cheap similarity prefilter finds candidate older chunks; (2) an exact code-signature diff for code, otherwise a pretrained NLI cross-encoder scored in both directions and flagged above a dev-chosen threshold. Optional `ensemble` (v4): a logistic regression over both NLI directions, chunk similarity and a change cue ("moved", "now", "no longer"), fitted on the dev pairs |
| `nli.py` | The NLI scorer (`cross-encoder/nli-deberta-v3-base`) |
| `rerank.py` | The cross-encoder reranker (`ms-marco-MiniLM-L-6-v2`) |
| `lexical.py` | BM25 keyword index and reciprocal rank fusion. Used only by experimental options (off in the frozen system) |

### 4.6 `packages/controller/`: component 4 (ASSE)

| File | What it does |
|---|---|
| `rules.py` | The rule table, checked in order. **history fits** → sliding window; **question (qa)** → RAG; **build request** → hybrid (find existing definitions before writing new code); **refactor** → summarization (it holds current signatures and renames); **debugging** → sliding window; **long open chat** → summarization. Plus `apply_escalations`: a summary-loss escalation moves summarization to RAG; a stale-fact escalation moves the window to hybrid |
| `controller.py` | Builds the feature vector from the `TurnSignal` and its own history (prior strategy, turns since the last switch), applies the rules, a dwell time against flapping, next-turn escalations and human overrides, and writes the rationale string |
| `model_based.py` | The learned LR/RF/GBDT controller (scikit-learn). Implemented and trained on the frozen system's recorded traces, but it **failed its val gate** (0.93 vs 0.99 for the rules), so the rules stay. It refuses to decide until trained |

### 4.7 `packages/decision_logger/` and `packages/dashboard/`

| File | What it does |
|---|---|
| `decision_logger/logger.py` | Append-only, validated JSONL for decisions, escalations and override requests |
| `dashboard/server.py` | A dependency-free live web dashboard that tails the log and accepts manual overrides |
| `dashboard/render.py` | The same dashboard as a single static HTML file (the presentation fallback) |
| `dashboard/static/index.html` | The dashboard page: strategy timeline, loss chart, rationale, feature vector, per-module panels and the override form |

---

## 5. `integration/`: putting it together

| File | What it does |
|---|---|
| `pipeline.py` | `MemoryPipeline`: the end-to-end turn loop from §2. It runs the three modules in parallel threads, asks the controller (signal only), logs, raises escalations for the next turn, and ingests the turn into every module. `user_turn(..., remember=False)` makes non-committing evaluation probes. It can also feed summarizer facts into RAG as "observations" (an experimental option, off in the frozen system). `llm_policy="strict"` (default, no LLM in the memory path) or `"assisted"` (the LLM writes the L2/L3 summary tiers only) |
| `llm_interface.py` | Builds the final prompt from the chosen strategy, including the hybrid composition (retrieved blocks plus recent turns, without duplicates) |
| `llm_client.py` | LLM access: any OpenAI-compatible endpoint (Ollama, vLLM, LM Studio, Groq, OpenRouter, DeepInfra) or Claude, with a disk cache so interrupted runs resume. Only evaluation uses it; the memory system itself makes no LLM calls |

---

## 6. `demo/coding_session/`: the visible proof

- **`script.py`:** an 18-exchange coding session (exploration → debugging → long detour) with two
  objective traps:
  - **Duplicate function:** the user asks for a helper that already exists.
  - **Renamed API:** a function parameter was renamed earlier.
- **`run_demo.py`:** runs the session through the real pipeline and checks, deterministically,
  whether each trap's evidence reaches the model's context. It does this for adaptive CEAI, each
  fixed strategy and a fixed 6-exchange window.
  - Output: a CAUGHT/MISSED table, the decision log and a dashboard HTML.
  - **Result: adaptive 2/2, fixed window 0/2.**
- **`scenarios.py` + `run_scenarios.py`:** 12 more sessions (26 traps) in Python, TypeScript, Go
  and SQL, written and pre-registered before any run. Trap kinds: duplicate function, rename,
  signature change, changed constant, project decision.
  - **Result: adaptive 16/26, fixed window 3/26, always-hybrid 18/26.**
  - Most misses are changed constants and functions renamed to a new name, where the old version
    stays in the context unmarked.
- **`present.py`:** live presenter mode for the presentation. It plays a session one exchange at a
  time (Enter or `--delay`), with the dashboard open and live overrides, prints CAUGHT/MISSED at
  each trap, then accepts audience questions. See `docs/DEMO_GUIDE.md`.
- **`run_mem0.py`:** the same traps on Mem0 (needs an LLM; a Colab job).

---

## 7. `eval/`: how everything is measured

| Path | Purpose |
|---|---|
| `metrics.py` | Shared metrics: evidence hit/coverage, token-F1, NDCG, macro-F1, an objective strategy oracle, and **conversation-level bootstrap confidence intervals** |
| `frozen.py` | Loads the **frozen** controller configuration. `CEAI_SYSTEM` selects `frozen` (default), `v2_hybrid`, `v3_qa_hybrid_obs` or `v4`, and every result file records which one ran. `CEAI_LLM_POLICY` selects `strict` (default) or `assisted` |
| `judge.py` | LLM answer judge (correct 1 / partial 0.5 / wrong 0) |
| `human_agreement/` | Blind labelling sheets plus scoring (Cohen's kappa) that check the LLM judge against people |
| `locomo/` | **Primary benchmark** (LoCoMo, 10 long conversations): `loader.py`, `run.py` (evidence, chunking, answer accuracy; `--split dev/test`), `stream.py` (questions asked *during* the conversation) |
| `locomo_plus/` | Supplementary benchmark: implicit cues ("I've been nervous about public speaking" … much later "I keep skipping all-staff meetings") |
| `synthetic/controller/` | Strategy-switch conversations (train/val/test). `generate.py` and `families.py` vary the phrasing; `trace.py` records once and replays many controller settings; `tune_rules.py` tunes on train + val and writes the frozen config; `run.py` evaluates on test with intervals |
| `synthetic/sliding_window/` | Topic-shift workloads, DSW vs recency baselines, and a 35-point weight ablation |
| `synthetic/summarization/` | Degradation-injected developer traces: loss, symbol retention, stale-fact leakage |
| `synthetic/retrieval/` | Contradiction pairs: flag precision/recall with a dev-chosen threshold, plus calibration. `staleness.py` gives MemStrata-style leak / false-supersession rates |
| `baselines/` | **External baselines under identical conditions:** fixed-chunk RAG, a LangChain-style summary buffer, Mem0 (the real `mem0ai` library, run locally) and full context |
| `v2_gate.py` | Gate checker for pre-registered experiments: "is the candidate significantly worse than frozen on this dev set?" |
| `v4_gate.py` | Runs frozen and v4 back to back on each gate (G1 coding scenarios, G2 synthetic val, G3 LoCoMo-Plus dev, G4 LoCoMo dev) and stops at the first failure. Resumes if interrupted |
| `beam/` | **BEAM** (arXiv 2510.27246), an independent benchmark built by other researchers: 20 conversations of about 200 turns, coding and general topics. `download.py` fetches it; `run.py` measures evidence hit and answer-in-context. Never tuned on |
| `synthetic/sliding_window/select_weights.py` | Splits the topic-shift workloads into dev/test, picks the weights on dev, reports test once |
| `synthetic/retrieval/staleness_v2.py` | Fits the staleness ensemble on the dev contradiction pairs, reports test once |
| `synthetic/controller/learned.py`, `length.py` | The learned-controller evaluation (val gate), and the conversation-length test (does the advantage grow with length?) |
| `locomo/chunking_search.py` | Searches chunk-boundary weights on LoCoMo dev, reports test once |

---

## 8. `scripts/`, `notebooks/`, `results/`

- **`scripts/build_notebook.py`** generates `notebooks/free_gpu_eval.ipynb`, which runs the GPU and
  LLM jobs on free Colab/Kaggle. Jobs are switched in its `RUN` dict. It installs Ollama, checks
  the GPU, and can restart the server with different settings.
- **`scripts/package_for_notebook.py`** zips the code plus data with a build stamp; the notebook
  prints that stamp, so you always know which code ran.
- **`scripts/build_results.py`** builds `results/RESULTS.md` from `results/final/*` (no number is
  typed by hand). **`scripts/plot_pareto.py`** draws the cost-vs-accuracy charts in
  `results/figures/`.
- **`results/final/`** holds the frozen test outputs and the baseline outputs. They are committed,
  so every slide number can be traced to a file.

---

## 9. What changed during the build (timeline)

| Date | Change | Why |
|---|---|---|
| 10-06 → 10-07 | Contracts, all four components, controller, logger, dashboard, integration, the coding demo and the first harnesses | Build every §7 P0/P1 item. The original `ceai-demo/` scaffold was missing, so the demo was rebuilt from the plan |
| 10-07 → 10-09 | LoCoMo-Plus harness; `user_state` facts in the summarizer; dev/test splits | LoCoMo-Plus exposed implicit cues being lost |
| 10-10 → 10-12 | Free-LLM workflow (OpenAI-compatible client, Colab notebook, judge, human-agreement sheets); parallel calls and caching | Answer accuracy without paid APIs. The first Colab run took 7 hours, which drove the speed fixes |
| 10-12 | The controller owner's work merged (phrasing families, trace replay, rule tuning) | A held-out controller evaluation with confidence intervals |
| 10-13 | **RAG read path:** compact headers + cross-encoder reranker (LoCoMo dev 0.496 → 0.709); in-stream LoCoMo; routing options; controller tuning on Colab | Better retrieval; a benchmark where the right strategy changes mid-conversation |
| 10-13 | **Reranker skipped for code tasks** | Applied to every turn, it ranked prose above code and broke the demo (2/2 → 1/2) |
| 10-13 | **Configuration frozen** by a selection rule declared before the dev results | So the test numbers cannot be tuned |
| 10-14 → 10-15 | Final run: a val gate, then every test split **once**; results builder | The numbers for slides (`results/RESULTS.md`) |
| 10-15 | 22-paper literature review; narrowed claims (CLAUDE.md §6.5); Pareto charts; MemStrata-style staleness metrics | Defensible novelty. Adaptive chunking was withdrawn as a claim (it did not beat segments on test) |
| 10-15 | **v2 (hybrid BM25)**, pre-registered with gates | It helped LoCoMo dev (+0.052) but failed the LoCoMo-Plus gate (−0.040), so it was not adopted |
| 10-15 → 10-16 | **External baselines:** fixed-chunk RAG, summary buffer, Mem0, full context | A fair comparison with existing memory systems |
| 10-16 | **Corrected Mem0 run**, declared before running | Run 1 had cut off 8.8% of Mem0's extractions (our output limit). Corrected, Mem0 ties CEAI on judged accuracy |
| 10-16 | **v3 (hybrid for questions + summarizer facts as observations)**, pre-registered | It failed the LoCoMo-Plus gate (0.134 → 0.020), and the dev answer gain was within noise, so it was not adopted |
| 10-17 | CLAUDE.md §12 rewritten as a self-contained status; this overview | Handover and closure |
| 10-17 | Roadmap items: manual override verified live; cost/latency chart (CEAI 6 s / 0 LLM calls vs Mem0 972 s / 54 per conversation); presentation framing (CLAUDE.md §6.6) | `docs/zero_cost_improvement_roadmap.md` |
| 10-17 | **12 held-out coding sessions**, pre-registered | One hand-built demo invites "was it built to pass?". Result 16/26 vs 3/26 |
| 10-17 | **v4 candidates**, pre-registered (`docs/v4_preregistration.md`): sliding-window weights, staleness ensemble, dev-tuned chunking, learned controller | Fix the known weak points. Three passed dev and test; the learned controller failed its gate |
| 10-17 | **v4 system gates** started; `llm_policy` toggle; BEAM; presenter mode; Mem0 coding traps | Still running (see §12) |

---

## 10. The main ideas in the code (why it is built this way)

1. **Contracts first.** Every component talks through `contracts/schemas.py`. Changing an interface
   is a deliberate, reviewed act, and components cannot reach into each other's internals.
2. **Decide from cheap, early signals; learn from late ones on the next turn.** That is the §5
   rule. It keeps the controller fast (about 0.1 ms), explainable and free of leakage.
3. **Never hide staleness.** The summarizer supersedes old keyed facts; RAG marks stale chunks and
   pulls in the newer one. Code uses exact signature comparison, because NLI cannot tell
   identifiers apart.
4. **No LLM in the memory path.** Summaries, staleness flags and routing are rule-based or small
   pretrained models. LLMs are used only to *evaluate* (answering and judging). That is CEAI's
   cost advantage over Mem0 (0 vs about 54 write-time LLM calls per conversation).
5. **Evaluation discipline is part of the system.**
   - Dev/test splits, and a frozen configuration.
   - A val gate before testing, and each test split run once.
   - Pre-registered gates for any new idea.
   - Confidence intervals over conversations.
   - Baselines under identical conditions, and corrections declared before rerunning.
6. **Reproducible from files.**
   - Results are generated from committed JSON.
   - The Colab notebook is generated from a script and prints the exact code version it ran.

---

## 11. Quick start

```bash
python -m venv .venv && .venv/Scripts/pip install -e ".[dev]"
pytest -m "not models"                                  # 89 fast tests
python -m demo.coding_session.run_demo                  # CAUGHT/MISSED table + runs/demo/dashboard.html
python -m dashboard.server --log-dir runs/demo          # live dashboard
python -m demo.coding_session.present                   # live presenter mode (docs/DEMO_GUIDE.md)
python -m demo.coding_session.run_scenarios             # 12 held-out sessions
python scripts/build_results.py --colab <results dir>   # rebuild results/RESULTS.md
```

GPU or LLM jobs: edit `RUN` in `scripts/build_notebook.py`, then run
`python scripts/build_notebook.py` and `python scripts/package_for_notebook.py`. Upload the zip and
the notebook to Colab, choose a T4, Run all, and check the `CODE VERSION` line.

---

## 12. Current work: the v4 round (2026-10-17, in progress)

The presentation moved to **Wednesday 2026-10-21**, so the roadmap items
(`docs/zero_cost_improvement_roadmap.md`) are being done now. Every change follows the same rules:
pre-register, gate on dev, run test once, report whatever the sign. **The frozen system stays the
system of record until v4 passes all its gates.**

### What "v4" is

v4 = the frozen system plus the three component changes that passed their own dev and test checks:

| Change | Where | Result (test, run once) |
|---|---|---|
| Sliding-window weights chosen on dev (relevance 0.5, importance 0.5) | `eval/frozen.py` → `CEAI_SW_WEIGHTS` | Recall 1.000 vs 0.706 with equal weights |
| Staleness ensemble | `ContradictionConfig.ensemble` | Precision 1.00 / recall 0.69 (was 0.82 / 0.73). Wrongly retired current facts 0% (was 23%). Stale-fact leak 0.31 (was 0.27) |
| Dev-tuned chunk boundaries | `BoundaryConfig` | Recall at 400 words 0.399 vs fixed segments 0.376 (hand-set was 0.355) |

Not in v4: the **learned controller** (failed its val gate: 0.93 vs 0.99 for the rules).

### Status of each piece

| Piece | Where it runs | Status |
|---|---|---|
| 12 held-out coding sessions | laptop | **Done:** adaptive 16/26, fixed window 3/26, always-hybrid 18/26 |
| v4 component checks (above) | laptop | **Done** |
| v4 system gates G1–G4 | laptop (`eval.v4_gate`) | **Running.** G1 passed (2/2 and 16/26, same as frozen). G2–G4 pending |
| Length test | laptop (`eval.synthetic.controller.length`) | **Running** |
| BEAM (independent benchmark) | laptop (`eval.beam.run`) | **Running** |
| Mem0 on the coding traps | Colab (`mem0_coding_traps`) | Ready to run |
| `llm_policy` strict vs assisted (20 LoCoMo-Plus dev items, a pilot) | Colab (`llm_policy_dev`) | Ready to run |
| Stronger free model and judge (Groq/OpenRouter) | later | Needs a free API key from the user |
| Human-agreement labelling | team | Sheets ready |
| Live presenter mode + `docs/DEMO_GUIDE.md` | laptop | **Done** |

### What happens next

- If **all v4 gates pass**, v4 is run once on the test splits and becomes the new system of record.
  Otherwise v4 stays dev-only, and the component results above are reported as component findings.
- BEAM, the length test and the Colab jobs are reported whatever they show.
- Then the slide text is written from the final numbers.
