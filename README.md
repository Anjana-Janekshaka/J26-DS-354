# Syno — Adaptive Memory Middleware for Multi-Turn LLM Applications

A runtime controller (ASSE) picks, **per conversational turn**, between three architecturally
distinct memory strategies — a dynamic sliding window, hierarchical summarization (L1/L2/L3) and
retrieval (RAG) — or a sliding-window + RAG hybrid. It decides from live Tier 0/1 signals only, and
every decision is logged with a human-readable rationale, rendered on a dashboard, and overridable
by a human. Tier 2 quality signals (summary loss, stale-fact flags) can only influence the *next*
turn, never the turn that produced them.

`CLAUDE.md` is the build guide. This file covers how to run things and what the numbers currently are.

## Quick start

```bash
python -m venv .venv && .venv/Scripts/activate        # (Windows; use bin/activate elsewhere)
pip install -e ".[dev]"                                 # + ".[llm]" for the optional Claude backend
pytest -m "not models"                                  # fast suite (deterministic test doubles)
pytest                                                  # + real-model test (downloads MiniLM / DeBERTa NLI)

python -m demo.coding_session.run_demo                  # CAUGHT/MISSED table + runs/demo/dashboard.html
python -m dashboard.server --log-dir runs/demo          # live dashboard at http://127.0.0.1:8765
```

Benchmarks (each writes `results/summary.json` next to it):

```bash
python -m eval.synthetic.retrieval.run        # contradiction-flag P/R/F1 + calibration
python -m eval.synthetic.summarization.run    # structured+merge vs naive, loss / SRR / stale leakage
python -m eval.synthetic.sliding_window.run   # DSW vs recency baselines + 35-point weight ablation
python -m eval.synthetic.controller.tune_rules  # tune rule thresholds on train/val -> frozen_rule_config.json
python -m eval.synthetic.controller.run       # held-out test split: macro-F1 + adaptive vs fixed, 95% CIs
python -m eval.locomo.run [--no-nli]          # primary benchmark (LoCoMo, 10 conversations, 1,986 QA)
```

`eval/locomo/data/locomo10.json` is the original LoCoMo release; `eval/locomo/loader.py` prints the
download command if it is missing. `python -m eval.locomo_plus.run` runs the supplementary
LoCoMo-Plus set (data from [xjtuleeyf/Locomo-Plus](https://github.com/xjtuleeyf/Locomo-Plus); the repo
ships no LICENSE file, and the base LoCoMo data is CC BY-NC 4.0).

### LLM-backed evaluations for free (open models)

QA answers, LLM-written summaries and LLM judges work with any OpenAI-compatible endpoint, such as
Ollama/vLLM on a free Kaggle or Colab GPU, or a free API tier. Every call is cached to disk.

```bash
export CEAI_LLM_BASE_URL=http://localhost:11434/v1     # Ollama
export CEAI_LLM_MODEL=qwen2.5:7b-instruct               # answers questions / writes summaries
export CEAI_JUDGE_MODEL=qwen2.5:14b-instruct            # grades answers (keep it larger)
python -m eval.locomo.run --conversations 3 --max-questions 100 --no-nli --llm --judge-answers
python -m eval.synthetic.controller.run --judge
```

On a free GPU, use `notebooks/free_gpu_eval.ipynb`: run `python scripts/package_for_notebook.py`,
upload `dist/ceai-memory-middleware.zip`, and run all cells. Without `CEAI_LLM_BASE_URL`, Claude is
used if Anthropic credentials exist; otherwise these paths report "not run".

**Checking the free judge against humans** (`eval/human_agreement`):
1. `python -m eval.human_agreement.make_sheets --questions <run>/questions.jsonl` writes blind
   sheets: 4 annotators × (12 shared + 12 own) answers, stratified over the judge's grades.
2. Each annotator follows `eval/human_agreement/LABELLING_GUIDE.md` (about 20 minutes).
3. `python -m eval.human_agreement.score` reports judge-vs-human Cohen's kappa and human-vs-human
   Fleiss' kappa. Cite the judge's scores only if kappa ≥ 0.6.

## Layout

| Path | What it is |
|---|---|
| `packages/contracts` | Pydantic contracts from build guide §4 (`TurnSignal`, `ControllerFeatureVector`, `StrategyModuleOutput`, `ControllerDecision`, `DecisionLogRecord`) + additive `EscalationEvent`, `OverrideRequest`, `ConversationTurn`; shared token counter and text conventions |
| `packages/conversation_manager` | turn counter, token-budget tracker, rule-based task-type classifier, topic-shift detector, `TurnSignal` bus |
| `packages/sliding_window` | DSW: relevance + freshness + importance + state composite, runtime-config weights, binary include/exclude, chronological restore; recency-only and fixed-token baselines |
| `packages/summarization` | structured L1/L2/L3 records, three tier prompts (LLM backend) + deterministic rule-based generator, contradiction-resolving merge (eager, cross-tier), live anchor-recall loss score on a background worker, Symbol Retention Rate, naive baseline |
| `packages/retrieval` | FAISS `IndexFlatIP` + MiniLM embeddings, write-time turn/segment granularity decision, two-stage staleness check (prefilter → bidirectional DeBERTa NLI; AST signature diff for code) |
| `packages/controller` | rule-based ASSE with rationale, dwell hysteresis, next-turn escalations, manual override; LR/RF/GBDT variants are explicit `TODO: v2` stubs |
| `packages/decision_logger` | append-only, fsync'd, validated JSONL for decisions, escalations and overrides |
| `packages/dashboard` | dependency-free live dashboard (strategy timeline, loss line, rationale, feature vector, per-module panels, override form) + static export |
| `integration` | the end-to-end turn loop and LLM interface (prompt assembly, hybrid composition, optional Claude client) |
| `demo/coding_session` | 18-exchange scripted session with a duplicate-function trap and a renamed-API trap |
| `eval/` | LoCoMo harness and the four per-component synthetic ground-truth sets |

Hard rule enforced by `tests/test_import_boundaries.py`: a package under `packages/*` imports only
`contracts` and itself. Leakage-freedom of the controller is structural: `RuleBasedController.decide`
receives only the `TurnSignal` (`tests/test_controller.py::test_decide_signature_has_no_access_to_module_outputs`).

## Final results (2026-10-15): see [`results/RESULTS.md`](results/RESULTS.md)

The configuration was frozen on dev data, then each test split was run once. The sheet is
generated from `results/final/*.json` by `python scripts/build_results.py --colab <results folder>`.

| headline (test split) | result |
|---|---|
| Controller, mixed-workload switch set | adaptive **0.986** evidence hit vs best single strategy 0.874 (**+0.112**, 95% CI [+0.093, +0.129]); vs always-hybrid **+0.060** with fewer tokens |
| Coding demo | adaptive **2/2** traps caught vs fixed window **0/2** |
| LoCoMo (966 questions) | adaptive ties the best strategy (RAG): 0.654 vs 0.656. The RAG read path went from 0.391 to **0.655** on the same conversations |
| Summarization | stale-fact leakage **0.00** vs 0.50 naive; signature retention 0.90 vs 0 |
| Contradiction flags | precision 0.82, recall 0.73 |
| Sliding window | 59 wins / 0 losses vs recency-only |

## Earlier results (2026-10-06, CPU, no LLM credentials; development history)

These were the first numbers, from before the RAG read-path changes and the frozen controller
configuration. They are kept for history; the results above supersede them.

### Integration — coding-session demo (`python -m demo.coding_session.run_demo`, budget 700 tokens)

| strategy | duplicate-function trap | renamed-API trap | score |
|---|---|---|---|
| fixed 6-exchange window (original scaffold baseline) | MISSED | MISSED | **0/2** |
| always sliding window (DSW) | MISSED | CAUGHT | 1/2 |
| always summarization | CAUGHT | CAUGHT | 2/2 |
| always RAG | CAUGHT | CAUGHT | 2/2 |
| always hybrid (window + RAG) | CAUGHT | CAUGHT | 2/2 |
| **adaptive (ASSE)** | **CAUGHT** (hybrid; definition from exchange 2) | **CAUGHT** (summary loss 0.59 > 0.15 at the previous turn → RAG; new signature from exchange 9, old one flagged stale) | **2/2** |

### ASSE controller (headline claim)

| set | adaptive | best single fixed paradigm | Δ | always-hybrid | selection macro-F1 / acceptable-choice acc. |
|---|---|---|---|---|---|
| synthetic strategy-switch (180 probes, budget 400) | **1.000** evidence hit | RAG 0.900 | **+0.100** | 1.000 | 0.354 / 1.000 |
| LoCoMo (1,986 QA, budget 1024, NLI off) | 0.443 | RAG 0.444 | −0.001 | 0.358 | 0.207 / 0.908 |

Reading this honestly: the adaptive gain over the best single paradigm comes from turns where
that paradigm is structurally wrong (implicit follow-ups: RAG 0.40 vs adaptive 1.00; late recall:
window 0.20). LoCoMo is pure long-range QA, so the controller (correctly) routes 1,979 / 1,986
questions to RAG and ties it. An always-on hybrid ties adaptive on the synthetic set but is
−0.085 below it on LoCoMo. Macro-F1 is against the *cheapest* hitting strategy; the controller
always picks *a* hitting strategy on the synthetic set but often not the cheapest one. The LLM-judge
half of the dual-source oracle has not been run (needs `--judge` + credentials).

### Controller evaluation protocol (Phase 1, 2026-10-12)

The table above comes from the original 30-conversation set, whose wording the rules were written
against, with no train/test split. It is kept reproducible as `run --split legacy`. The protocol now
used for reporting:

- **Phrasing families** (`eval/synthetic/controller/families.py`) share one conversation structure
  and the same objective evidence. Their user wording differs:
  - **A:** the canonical wording the rules were written against.
  - **B:** paraphrases.
  - **C:** held-out paraphrases.
- **Varied structure**: 0–3 early exchanges and a 2–12 exchange detour, so turn count and token
  pressure vary between conversations.
- **Fixed split** (`splits.json`, owned by the controller component):
  - **train:** A (60) + B (50)
  - **val:** B (20)
  - **test:** C (70), never used for tuning.
- **Rule thresholds** are tuned on train/val only (`tune_rules.py`) and frozen before the test split
  is run.
- **Record once, replay many** (`trace.py`): the pipeline runs once per conversation. Any controller
  is then evaluated by replaying the trace. `tests/test_controller_eval.py` checks that replay
  equals a live run.
- **Baselines:** each fixed strategy, always-hybrid, random, majority class (from train), and the
  oracle upper bound. Every comparison carries a 95% CI that resamples whole conversations.

Held-out numbers: _to be filled from `results/test/summary.json` after running with the real models._
`--offline` (hashing embedder, no NLI) only checks that the code runs; its numbers are not results.
Controller results produced with NLI enabled before the 2026-10-12 probe fix (probes no longer mark
contradiction flags as reported, `integration/pipeline.py`) should be re-run.

### Component 1 — Dynamic Sliding Window (40 topic-shift conversations, 360 probes)

| budget | DSW (equal weights) | recency-only (k=8) | fixed-token window | DSW vs recency win / tie / loss |
|---|---|---|---|---|
| 220 tok | **0.989** gold-turn recall | 0.556 | 0.803 | 156 / 204 / 0 |
| 100 tok | **0.719** | 0.556 | 0.567 | 59 / 301 / 0 |

Ablation (35-point weight simplex): **equal weights are not optimal** — they rank #12 (budget 220)
and #15 (budget 100); configurations with relevance ≥ 0.5 reach 1.000. Removing relevance is the only
single-factor drop that hurts (best recall without it: 0.831 / 0.631). That is the case for keeping
weights as runtime config rather than a claim that equal weighting is justified. The conversation
manager's embedding-based shift detector scores P 0.45 / R 0.69 against the shift labels.

### Component 2 — Hierarchical Summarization (30 degradation-injected developer traces)

| system @ budget | loss score ↓ | symbol retention ↑ | current-fact recall ↑ | stale-fact leakage ↓ |
|---|---|---|---|---|
| **structured + merge @1000** | **0.063** | **0.90** | **1.00** | **0.00** |
| structured, no merge @1000 | 0.002 | 1.00 | 1.00 | 0.75 |
| naive single-pass @1000 | 0.374 | 0.00 | 0.43 | 0.50 |
| **structured + merge @500** | **0.254** | **0.49** | **0.69** | **0.00** |
| naive @500 | 0.591 | 0.00 | 0.30 | 0.04 |

Loss-monitor sanity: deleting a growing fraction of a summary raises the live loss score
monotonically (Spearman 0.83). The no-merge ablation shows why the loss score alone is not enough:
it keeps every old value (lowest loss) and leaks 75% of superseded facts.

### Component 3 — RAG

Contradiction / staleness flags (184 templated pairs incl. hard negatives; threshold chosen on dev):
**test P 0.82 / R 0.73 / F1 0.77**; prefilter recall 0.74; raw NLI score Brier 0.14, ECE 0.15.
False positives concentrate in same-topic-but-compatible pairs (different events, another
service's port). Code-symbol staleness uses an exact AST signature diff, because the NLI model scores
`create_task(title, due)` vs `create_task(title, due_date)` at 0.00 contradiction.

Granularity on LoCoMo (1,986 QA): NDCG@10 turn 0.207 / segment 0.446 / adaptive 0.275, but segments
return 4.6× more text. At an **equal 400-word budget, recall is turn 0.381 / segment 0.421 /
adaptive 0.428**.

### Supplementary — LoCoMo-Plus (401 implicit-constraint items, budget 1024, deterministic, no LLM)

Did the cue dialogue (the implicit constraint) reach the context when its trigger arrived?

| strategy | cue hit | cue hit, cue < 50 turns back | cue hit, cue > 200 turns back |
|---|---|---|---|
| sliding window | 0.090 | 0.69 | 0.00 |
| summarization (structured + merge) | 0.085 | 0.63 | 0.00 |
| naive summary | 0.185 | 1.00 | 0.00 |
| RAG | 0.167 | 0.06 | 0.17 |
| hybrid | **0.185** | 0.65 | 0.10 |
| **adaptive** | **0.087** (−0.080 vs RAG) | 0.63 | 0.01 |

This is a **negative result for the controller, reported as such**:
- **Misrouting:** triggers are statements ("I ended up volunteering… now I'm overwhelmed"), so they're
  classified `chat` and routed to summarization (391 / 401).
- **Weak implicit-cue retention:** the structured L1 extractor keeps few implicit first-person
  state, goal and value statements, so it trails the naive summarizer here.
- **No escalation history:** this harness ingests history without decision turns, so the controller
  has no prior escalations to react to.

Oracle labels come from our own objective protocol: 297 / 401 items are answerable by no strategy
at this budget, and macro-F1 is 0.02.

## What is real and what is stubbed (build guide §7)

| component | P0 | P1 | P2 |
|---|---|---|---|
| Conversation Manager | real | real (phrasing + known-entity + topic-similarity shift) | — |
| Sliding Window | real | real (ablation above) | — |
| Summarization | real (rule-based L1 + merge; LLM generator implemented, not run) | real (L2/L3, async Method-1 loss worker) | `TODO: v2` — Dual Q&A consistency (Method 2), repair re-prompt loop |
| RAG | real | real (adaptive granularity, NLI stage) | partial — dev/test threshold sweep + Brier/ECE; no full calibration study |
| ASSE Controller | real (rules, rationale, override, next-turn escalations) | — | `TODO: v2` — LR/RF/GBDT (`ModelBasedController` raises) |
| Decision Logger | real | — | — |
| Dashboard | real (live + static) | real (per-module panels) | real (override form → `overrides.jsonl` → controller) |
| Coding demo | real, on the real pipeline | — | — |

Notes for Q&A: the original `ceai-demo/` scaffold was not available, so `demo/coding_session` was
rebuilt from the §9 description; the trap checks are deterministic string checks on the context that
would reach the model, never on model output.
