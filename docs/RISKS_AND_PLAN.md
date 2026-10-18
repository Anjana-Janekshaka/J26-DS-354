# CEAI: project plan, progress and risk management

## 1. Plan vs actual (Progress Presentation 1)

The build order is fixed in CLAUDE.md §10; the "80% done" checklist in CLAUDE.md §7 defines what
counts as complete for this milestone (P0 must work, P1 should work, P2 may be a documented stub).

| Step (CLAUDE.md §10) | Planned for PP1 | Status | Evidence |
|---|---|---|---|
| 1. Shared contracts + validation tests | P0 | **Done** | `packages/contracts/`, `tests/test_contracts.py` |
| 2. Conversation manager | P0 + P1 (task-type classifier) | **Done** | `tests/test_conversation_manager.py` |
| 3. Sliding window, summarization, retrieval | P0 + P1 | **Done** (all P0 and P1 items) | Component tests and results (`results/RESULTS.md`) |
| 4. Rule-based controller with rationale and override | P0 | **Done** | `tests/test_controller.py` |
| 5. Decision logger + dashboard | P0 + P1 panels | **Done**, including the P2 override control | `tests/test_logger_dashboard_integration.py` |
| 6. End-to-end integration | P0 | **Done** | `integration/pipeline.py` |
| 7. Coding demo + benchmark suite | P0 | **Done**, plus 12 held-out sessions, external baselines (Mem0 and three others) and an independent benchmark (BEAM) | `results/final/` |
| 8. Learned controller (LR/RF/GBDT) | *After* PP1 | **Started early:** implemented and evaluated; it did not beat the rules, so it is not used | `docs/v4_preregistration.md` §4 |

**Completion:** every P0 and P1 item is real and running; of the P2 items, the override UI is done
and the learned controller is evaluated. **There is no delay against the plan.** The presentation
date moving from 2026-10-19 to 2026-10-21 was used for pre-registered improvements, not to catch up.

### Remaining work after PP1

| Work | Why | How it will be judged |
|---|---|---|
| Fix the request-phrased-recall routing gap (BEAM, LoCoMo-Plus) | The known weakness, confirmed on independent data | Pre-registered, chosen on dev sets; BEAM stays a test set |
| Staleness for renamed functions, changed constants, non-Python code | Most demo misses (`docs/demo_scenarios_preregistration.md`) | New dev scenarios, then a fresh held-out batch |
| Stronger answering model and judge (free 70B tier) | All answer-accuracy numbers so far use a 7B judge | Second judge + human agreement (kappa ≥ 0.6) |
| OpenAI-compatible proxy | Drop-in use in front of any chat app (commercial path) | Demo with an existing chat client |
| Final report / paper | `docs/related_work.md` is most of the literature review | — |

## 2. Risk register

Each risk is one that actually occurred or was identified during the build. "Status" says whether
the mitigation is already executed.

| # | Risk | Likelihood / impact | Mitigation | Status |
|---|---|---|---|---|
| R1 | **Overclaiming novelty**: very recent systems (FluxMem, MemCon, LycheeMemory V2) overlap our claims | High / High | Every claim narrowed against a 22-paper review; one claim withdrawn when the test result did not hold, and later returned only as an engineering result | **Executed** (CLAUDE.md §6.5, `docs/related_work.md`) |
| R2 | **Tuning on the test set** inflates results | Medium / High | Dev/test splits for every dataset; frozen configuration; each test split run once; every new idea pre-registered with gates before running | **Executed** (CLAUDE.md §12.7, `docs/*_preregistration.md`) |
| R3 | **Our best controller result is on our own synthetic data** | High / High | Held-out phrasing family; 12 held-out coding sessions written before running; independent BEAM benchmark; negative BEAM result reported, not hidden | **Executed** |
| R4 | **Unfair baseline comparison** (e.g. a baseline handicapped by our harness) | Medium / High | Identical questions, budget, model and judge; when Mem0 was found to be cut off by our output limit, a correction was declared and the run repeated | **Executed** (`docs/baselines_protocol.md`) |
| R5 | **LLM judge unreliable** | Medium / Medium | Human-agreement sheets with Cohen's kappa; judge numbers cited only after kappa ≥ 0.6; token-F1 reported alongside; a 7B judge was found unusable for strategy labels and dropped there | **In progress** (sheets ready; team labelling) |
| R6 | **No budget for paid APIs or GPUs** | Certain / High | Free Colab T4 + local Ollama; resumable, cached jobs; CPU-only local harnesses | **Executed** |
| R7 | **Long runs interrupted** (Colab disconnects, laptop restarts) | High / Medium | Every harness resumes from where it stopped; per-item disk caches; jobs split into phases | **Executed** |
| R8 | **A component improvement breaks the system** | Medium / High | System-level gates on four dev sets before adoption. This caught v4: sliding-window weights that won alone dropped the system from 0.99 to 0.80, so they were removed | **Executed** (`docs/v4_preregistration.md`) |
| R9 | **Live demo fails on presentation day** | Medium / High | Deterministic, offline demo (no LLM, no internet); static HTML fallback; one-page guide with fixes | **Executed** (`docs/DEMO_GUIDE.md`) |
| R10 | **Four components in one repo conflict** | Medium / Medium | Shared contracts only; automated import-boundary test; branch per component merged through `development` | **Executed** (`tests/test_import_boundaries.py`) |
| R11 | **Known performance gap**: request-phrased recall routed to summarization (BEAM −0.099 vs RAG) | Confirmed / Medium | Diagnosed; fix is planned work, pre-registered on dev sets, with BEAM kept as an untouched test | **Planned** (§1 above) |
