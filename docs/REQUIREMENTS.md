# CEAI: user and functional requirements

Every requirement below is traced to the code that implements it and to the test or result that
shows it works. "Test" names are in `tests/`; "Result" paths are in `results/final/`.

## 1. Users

| User | Who | What they need from a memory layer |
|---|---|---|
| **U1 Application developer** (primary) | Builds a chatbot, coding assistant or agent on an LLM with a limited context window | Long conversations that keep working without a hand-built memory strategy, at no extra LLM cost, as a library or a proxy in front of an existing model |
| **U2 End user** of that application | Talks to the assistant for a long, mixed session (chat, debugging, questions, refactoring) | The assistant remembers the right things: the function written an hour ago, the parameter that was renamed, a fact said in the first session. And it never reuses a stale version |
| **U3 Operator / auditor** | Runs or reviews the deployed assistant | To see *why* memory behaved as it did on any turn, and to correct it live |
| **U4 Researcher / evaluator** | Compares memory strategies | Reproducible, fair numbers with uncertainty, and protection against tuning on the test data |

## 2. User requirements

| ID | Requirement | User |
|---|---|---|
| UR1 | Memory adapts as the conversation changes type (chat → debugging → recall → coding) instead of using one fixed strategy | U1, U2 |
| UR2 | The assistant is not given outdated facts or code as if they were current | U2 |
| UR3 | Existing code is surfaced before the assistant writes a duplicate | U2 |
| UR4 | Memory costs no extra LLM calls and adds negligible latency | U1 |
| UR5 | Every memory decision is explained and can be overridden by a person | U3 |
| UR6 | Works within any token budget the developer sets | U1 |
| UR7 | Results are reproducible and compared fairly with existing systems | U4 |

## 3. Functional requirements

| ID | The system shall… | Implemented in | Verified by |
|---|---|---|---|
| **FR1** | Track every turn and publish a per-turn signal: turn count, task type, token usage, topic-shift state | `packages/conversation_manager/` | Tests `test_turn_counter_tokens_and_bus`, `test_task_type_patterns`, `test_task_type_carries_over_and_shift_detected` |
| **FR2** | Build a sliding-window context by scoring past turns on relevance, freshness, importance and state, with weights set at runtime, in chronological order, within the budget | `packages/sliding_window/` | Tests `test_weights_are_runtime_config`, `test_output_contract_and_chronological_order`, `test_budget_respected`. Result: 59 wins / 0 losses vs recency-only |
| **FR3** | Summarize older turns into three structured tiers (L1 facts, L2 intent, L3 profile), keeping exact code signatures | `packages/summarization/` | Tests `test_l1_extracts_exact_signatures_verbatim`, `test_tiers_and_structured_records`. Result: signature retention 0.90 vs 0 |
| **FR4** | Supersede an old fact when a new fact with the same key arrives, with a timestamp, instead of keeping both | `summarization/merge.py` | Tests `test_contradiction_merge_supersedes_with_timestamp`, `test_rename_retires_old_symbol`. Result: stale-fact leakage 0.00 vs 0.50 |
| **FR5** | Compute a live information-loss score for every summary and raise an escalation when it exceeds 0.15 | `summarization/loss.py` | Tests `test_loss_score_detects_injected_degradation`, `test_escalations_logged_and_consumed_next_turn`. Result: Spearman 0.91 with actual loss |
| **FR6** | Index turns in a vector store, choose chunk granularity at write time, and retrieve top-k chunks within the budget | `packages/retrieval/` | Tests `test_faiss_index_add_search_remove`, `test_granularity_modes`, `test_boundary_score_monotone_in_semantic_drop` |
| **FR7** | Flag stale chunks at write time (exact signature diff for code, NLI for prose), mark them `[!] stale` and pull in the newer chunk | `retrieval/contradiction.py` | Tests `test_signature_diff_flags_stale_code_and_pulls_superseder`, `test_nli_stage_flags_prose_contradiction`, `test_prefilter_skips_unrelated_pairs`. Result: precision 0.82 / recall 0.73 |
| **FR8** | Choose one strategy per turn (window, summarization, RAG or hybrid) from the turn signal and its own history only | `packages/controller/` | Tests `test_rules`, `test_decide_signature_has_no_access_to_module_outputs`. Result: +0.112 over the best single strategy |
| **FR9** | Apply module escalations to the *next* turn only, never the turn that raised them | `controller/controller.py` | Tests `test_escalation_applies_to_next_turn_only`, `test_escalation_from_same_turn_is_not_used` |
| **FR10** | Give every decision a human-readable rationale | `controller/controller.py` | Test `test_end_to_end_logs_exact_records`; the live demo prints it per turn |
| **FR11** | Accept a manual override (next turn or persistent) from the dashboard and mark it in the log | `controller/`, `dashboard/server.py` | Tests `test_override_and_scope`, `test_override_inbox_reaches_controller`; verified live (CLAUDE.md §6.6) |
| **FR12** | Append every decision, feature vector and module output to a validated, append-only log | `packages/decision_logger/` | Tests `test_decision_log_record_roundtrip_and_consistency`, `test_logger_rejects_corrupt_lines` |
| **FR13** | Show decisions live (timeline, rationale, per-module panels) and export a static copy | `packages/dashboard/` | Test `test_dashboard_static_and_live` |
| **FR14** | Assemble the final prompt from the chosen strategy's context | `integration/llm_interface.py` | Test `test_replay_matches_live_pipeline` |
| **FR15** | Let evaluation questions query memory without changing it | `integration/pipeline.py` (`remember=False`) | Tests `test_probe_turn_not_remembered`, `test_probe_decision_does_not_commit` |

## 4. Non-functional requirements

| ID | Requirement | Measured |
|---|---|---|
| **NFR1 Cost** | No generative LLM call anywhere in the memory path by default (`llm_policy="strict"`) | 0 LLM calls to build memory vs ~54 for Mem0 per conversation (`results/final/cost_latency.json`); test `test_strict_is_default_and_makes_no_calls` |
| **NFR2 Latency** | Strategy decision fast enough to be invisible | ~0.1 ms per decision; memory for a LoCoMo conversation built in ~6 s vs ~972 s for Mem0 |
| **NFR3 Explainability** | Every decision carries its rule, features and any escalation or override | Decision log records (§4.5 contract) |
| **NFR4 No leakage** | The controller never sees a module's same-turn quality signals | Structural: `decide()` receives only the `TurnSignal` (test above) |
| **NFR5 Modularity** | Components interact only through shared contracts | Tests `test_no_cross_component_imports`, `test_contracts_imports_nothing_internal` |
| **NFR6 Privacy / local** | Runs fully offline on a laptop CPU; no data leaves the machine | All models are local (MiniLM, DeBERTa NLI, MS MARCO reranker) |
| **NFR7 Reproducibility** | Every reported number regenerates from committed files and code version | `scripts/build_results.py`, frozen config, notebook `CODE VERSION` stamp |
| **NFR8 Budget compliance** | Context never exceeds the configured token budget | Test `test_budget_respected`; every harness records tokens per context |

## 5. Out of scope for this phase (documented, not hidden)

- The learned (LR/RF/GBDT) controller is implemented but did not beat the rules on validation, so
  the rule-based controller is used (`docs/v4_preregistration.md` §4).
- Mid-turn repair (re-running a turn with another strategy) is deliberately excluded by the
  no-leakage rule (CLAUDE.md §5).
- An OpenAI-compatible proxy for drop-in use is planned (`docs/RISKS_AND_PLAN.md`).
