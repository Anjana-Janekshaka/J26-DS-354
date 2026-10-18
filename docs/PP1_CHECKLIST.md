# Progress Presentation 1: mark sheet → evidence

How each criterion on the IT4010 PP1 mark sheet (`docs/PP1 Assessment Criteria.pdf`) is met by
this project, what to show for it, and where the proof is. Marks are given **per student**, so
each member presents their own component against the same structure (§3).

## 1. Criterion by criterion

### LO1 Proven gap / creative solution (10%)

| Sub-criterion | What earns "Excellent" | Our evidence | Show |
|---|---|---|---|
| Problem definition (30%) | Problem clearly presented *referring to the current implementation* | Memory systems lock in one strategy, but conversations change type. Live demo: the fixed window misses both traps (0/2); Mem0 misses both (0/2) | Demo exchanges 16 and 18 (`docs/DEMO_GUIDE.md`) |
| Proof of concept (70%) | Implementation clearly demonstrates the proposed solution | Per-turn switching running end to end: adaptive 2/2 and 16/26 unseen traps; +0.112 over the best single strategy on mixed conversations; advantage over the window grows with length (+0.28 → +0.42) | Live demo + one results slide |

### LO2 Applying knowledge in the stream (25%)

| Sub-criterion | Our evidence | Show |
|---|---|---|
| Key pillars identified and applied (30%) | Information retrieval (dense retrieval, cross-encoder reranking, NDCG/recall), NLP (NLI for contradiction, structured summarization), ML evaluation (dev/test splits, bootstrap CIs, calibration, Cohen's kappa), software architecture (contracts, modularity), all positioned against a 22-paper review (`docs/related_work.md`) | One "knowledge areas" slide |
| Technologies, in depth (70%) | Table in §2 below, with **why each was chosen and what we measured about it** (e.g. the web-QA reranker ranks prose above code, so it is skipped for code turns; NLI cannot tell identifiers apart, so code uses an AST signature diff) | Technology slide; be ready to explain each "why" |

### LO3 Solution implementation (40%)

| Sub-criterion | Our evidence | Where |
|---|---|---|
| Design excellence (20%) | Contract-first architecture; the no-leakage rule enforced structurally (the controller only receives the turn signal); next-turn escalations; append-only logs; hybrid composition | CLAUDE.md §2, §5; `docs/SYSTEM_OVERVIEW.md` §2, §10 |
| Completion (30%) (~50% expected, no delay) | All P0 and P1 items done, plus extras; **no delay** against the plan | `docs/RISKS_AND_PLAN.md` §1 |
| Standards / best practices (20%) | See §4 below: real evidence for each item | `docs/PP1_CHECKLIST.md` §4 |
| User / functional requirements (20%) | 4 user types, 7 user requirements, 15 functional and 8 non-functional requirements, **each traced to code and a test or result** | `docs/REQUIREMENTS.md` |
| Risk mitigation (10%) | 11 real risks, 9 with mitigations already executed (e.g. pre-registration against test tuning; system gates that caught a harmful change) | `docs/RISKS_AND_PLAN.md` §2 |

### LO4 Effective communication (15%)

| Sub-criterion | Plan |
|---|---|
| Structure and Q&A (60%) | Slide order in §3; prepared answers in §5 |
| Presentation skills (40%) | Visual aids: live dashboard, CAUGHT/MISSED table, Pareto chart (`results/figures/pareto_controller.png`), build-time chart (`results/figures/memory_build_time.png`), length chart (`results/figures/length_advantage.png`). Rehearse to time with `present.py --delay 2` |

### LO5 Commercialization (10%)

| What earns "Excellent" | Our evidence |
|---|---|
| Sound evidence of business potential, many achievable user benefits | Zero LLM calls for memory vs ~54 for Mem0, 162× faster memory build, same judged accuracy, fewer coding mistakes, audit trail, offline/private. Segments and offering in `docs/COMMERCIALIZATION.md` |

## 2. Technologies and why (LO2 depth)

| Technology | Used for | Why this one / what we learned |
|---|---|---|
| Python 3, Pydantic v2 | Shared contracts with validation | Schemas reject malformed messages between components (`test_extra_fields_rejected`) |
| sentence-transformers `all-MiniLM-L6-v2` | Embeddings for relevance, topic shift and retrieval | Small and CPU-fast; good enough that retrieval gains came from the read path, not a bigger model |
| FAISS `IndexFlatIP` | Vector index | Exact cosine search; removable ids so superseded chunks can be retired |
| Cross-encoder `ms-marco-MiniLM-L-6-v2` | Reranking retrieved chunks | +0.17 evidence hit on LoCoMo dev, but trained on web QA: it ranks prose above code, so it is **skipped for code turns** (measured on the demo) |
| NLI cross-encoder `nli-deberta-v3-base` | Staleness check for prose | Scored in both directions to remove one-directional false positives; cannot tell code identifiers apart, so code uses an **AST signature diff** |
| Python `ast` | Exact code signatures | Symbol retention 0.90 vs 0 for a naive summarizer |
| tiktoken | Token budgets | Exact budget compliance per context |
| scikit-learn | Learned controller (LR/RF/GBDT), staleness ensemble | The learned controller did not beat the rules on validation; the ensemble cut wrongly retired facts from 23% to 0% |
| Ollama + Qwen2.5-7B on free Colab T4 | Answering and judging during evaluation only | $0 evaluation; the memory path itself uses no LLM |
| `mem0ai` | External baseline | Run locally under identical conditions |
| Standard-library HTTP server + HTML/JS | Live dashboard with override | No framework dependency; works offline |
| pytest, GitHub Actions | Tests and CI | 89 fast tests on every push |

## 3. Slide order (about 10–12 minutes, then Q&A)

1. **Problem** (LO1): one strategy for a whole conversation fails when the conversation changes type.
2. **Gap** (LO1): closest systems (FluxMem, MemCon, Mem0, Zep, MemGPT) and what none of them do (CLAUDE.md §6.5).
3. **Architecture** (LO3 design): the §2 diagram and the no-leakage rule.
4. **Requirements** (LO3): users and the key FR/NFRs, with a pointer to the traced table.
5. **Live demo** (LO1 proof of concept): `python -m demo.coding_session.present`. Traps caught live, rationale per turn, live override.
6. **Each member's component slide** (claim, closest system, one number; CLAUDE.md §11). See the note below.
7. **Results**: mixed-workload gain, coding traps vs Mem0, cost chart, length chart. **One honest limitation** (BEAM).
8. **Technologies** (LO2): the table in §2.
9. **Standards, plan and risks** (LO3): §4, plan vs actual, the top 3 risks.
10. **Commercialization** (LO5): benefits and who would use it.
11. **Next steps.**

**Individual marking:** each member presents their own component slide and answers questions on
it. For example, the RAG owner covers staleness flagging (P 0.82 / R 0.73; the v4b ensemble cut
wrongly retired facts to 0%), dev-tuned chunking, and the reranker/code trade-off.

## 4. Standards and best practices actually applied (LO3 evidence)

| Practice | Evidence |
|---|---|
| Automated testing | 89 fast tests + real-model tests; `pytest -m "not models"` |
| Continuous integration | `.github/workflows/tests.yml` runs the tests on every push and pull request |
| Interface contracts and schema validation | `packages/contracts/` (Pydantic), validated append-only JSONL logs |
| Modular architecture enforced by a test | `tests/test_import_boundaries.py` |
| Version control workflow | Branch per component, merged through `development` into `main` |
| Experimental rigour | Dev/test splits, frozen configuration, each test split run once, pre-registration with gates, 95% bootstrap CIs over conversations, fair baselines with declared corrections (`docs/*_preregistration.md`, `docs/baselines_protocol.md`) |
| Reproducibility | Results generated from committed files; notebook prints the exact code version |
| Measurement validity | Human-agreement check (Cohen's kappa ≥ 0.6) before citing LLM-judge numbers |
| Documentation | CLAUDE.md, `docs/SYSTEM_OVERVIEW.md`, `docs/REQUIREMENTS.md`, `docs/RISKS_AND_PLAN.md`, `docs/DEMO_GUIDE.md` |

## 5. Likely questions and prepared answers

| Question | Answer (with the evidence) |
|---|---|
| "Isn't your best result on data you generated?" | Yes, which is why we added 12 held-out coding sessions written before running, Mem0 on the same traps, and an independent benchmark (BEAM), where we report a loss to always-RAG and its cause |
| "Why not just always use RAG or hybrid?" | On recall-only benchmarks adaptive ties RAG (no regret). When the conversation changes type it wins: +0.112 over RAG and +0.060 over always-hybrid with fewer tokens, and the lead over the window grows with length |
| "How is this different from FluxMem / MemCon?" | They choose memory *structures* at consolidation boundaries or operations within retrieval; we switch between three paradigms every turn, with a logged, explainable, overridable decision and no LLM in the decision |
| "Do you beat Mem0?" | Same judged accuracy (not a significant difference), significantly higher exact-answer F1, zero memory LLM calls vs ~54, and 2/2 vs 0/2 on the coding traps |
| "What doesn't work?" | Request-phrased recall goes to the summarizer (BEAM, LoCoMo-Plus); renamed-to-new-name functions and changed constants can leak. Both are diagnosed, with planned, pre-registered fixes |
| "Why is the controller rule-based, not learned?" | We trained LR/RF/GBDT on recorded decisions; they scored lower on validation (0.93 vs 0.99), so the rules stay, and the rules are explainable |
