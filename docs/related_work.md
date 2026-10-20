# Related work and novelty positioning (reviewed 2026-10-15)

This file reviews the 22 unique papers in the team's reading folder (`RAG model/Papers`; three files
were duplicates). For each paper it records what the paper does, which Syno claim it touches, and
what Syno takes from it. The narrowed claims are in CLAUDE.md §6.5. Numbers quoted are the papers'
own and are not reproduced here. The only exception is MemStrata's staleness metrics, which we
computed on our own data (§3).

## 1. Paper by paper

| Paper | What it does | Touches | Threat | What Syno takes |
|---|---|---|---|---|
| **MemStrata**, Temporal Validity in Retrieval Memory (arXiv 2606.26511) | Deterministic (subject, relation) supersession in a bi-temporal ledger. Reports that cosine separates contradictions from duplicates at AUROC 0.59, and that LLM/NLI judges leak stale facts 25–60% | RAG claim 2; summarization merge | **High** | The stale-fact leak metric, structural checks first, and reporting false supersession. Our version is in §3 |
| **Zep / Graphiti** (arXiv 2501.13956) | Temporal knowledge graph. An LLM compares new edges with similar existing ones and invalidates them. Search mixes cosine, BM25 and BFS, with RRF / MMR / cross-encoder reranking | RAG claim 2; RAG retrieval | **Medium** | A neighbour for two-stage staleness: theirs works on LLM-extracted edges with an LLM verifier. Hybrid lexical + dense retrieval and MMR (v2 options, §4) |
| **MemGAS**, multi-granularity association and selection (arXiv 2505.19549) | Multi-granularity units; an entropy-based router weights granularities per query, training-free | RAG claim 1; controller (adaptive selection) | **Medium** | The closest prior work on adaptive granularity: it selects at *read* time, within retrieval. v2: an entropy router over turn and segment views |
| **SeCom**, memory construction and retrieval (ICLR 2025, arXiv 2502.05589) | Topic segments beat turn, session and summary units. Compression (LLMLingua-2) denoises retrieval | RAG claim 1 | Medium | Explains our test result (fixed segments beat our adaptive chunking at equal budget). Compression denoising is a v2 option |
| **xMemory**, Beyond RAG for Agent Memory (arXiv 2602.02007) | Agent memory is full of near-duplicates. Separate facts from similar history first, then retrieve top-down with uncertainty-gated expansion | RAG retrieval | Low | Redundancy-aware selection (MMR v2 option) |
| **GOAL-MEM** (NeurIPS 2026, arXiv 2605.12213) | Backward chaining: decompose the utterance into sub-goals, retrieve per sub-goal, verify by entailment | RAG (multi-hop, implicit) | Low | v2: sub-goal queries for multi-hop and implicit cues (needs an LLM). Our weakest LoCoMo categories are multi-hop and LoCoMo-Plus |
| **RMM**, Reflective Memory Management (ACL 2025) | Prospective topic memories plus retrospective online RL of a light reranker (residual linear adapter) from the LLM's citations | RAG reranking; summarization | Low | v2: replace the out-of-domain MS MARCO cross-encoder with a small adapter trained on our own train splits |
| **SAGE**, novelty gate (arXiv 2605.30711) | von Mises–Fisher novelty score with an adaptive threshold. ADD / NOOP, and only uncertain cases go to an LLM | RAG write path | Low | v2: an adaptive-threshold gate in front of NLI, to cut NLI calls (our main CPU cost) |
| **MemMA** (arXiv 2603.18718) | Multi-agent memory cycle. Probe-QA verification repairs memory before it is finalised | Summarization | Low | The summary repair loop (§6.3 stretch): a deterministic probe version on top of our anchor-recall loss |
| **LoCoMo** (Maharana et al., arXiv 2402.17753) | The benchmark. RAG over *observations* (assertions about speakers) beats RAG over raw dialogue | Benchmark; RAG | — | Primary benchmark. v2: index L1 facts as retrievable units (observation-style) |
| **Mem0** (arXiv 2504.19413) | LLM extraction with ADD / UPDATE / DELETE / NOOP. On LoCoMo, full context (judge 72.9) beats every memory system; memory systems win on latency and tokens | Controller (framing); summarization merge | Low | Cost–accuracy framing (our Pareto charts). Mem0's UPDATE is an LLM-decided merge, while ours is keyed and deterministic |
| **MemGPT** (arXiv 2310.08560) | OS-style paging. A memory-pressure warning at 70% of context; the LLM itself decides what to page via function calls | Controller | Low | Precedent for our token-pressure signal. Its control is LLM-driven and not logged as explainable decisions, unlike ASSE |
| **Self-RAG** (arXiv 2310.11511) | Reflection tokens decide *whether* to retrieve per segment, with an adjustable threshold | Controller | Low | Adaptive retrieval within one paradigm (retrieve or not), not a choice between paradigms |
| **MoMA**, generalized routing (arXiv 2509.07571) | Routes queries across LLMs and agents for Pareto cost–performance, with a state machine and masking | Controller | Low | Routing as a cost–performance problem, which motivates the Pareto evaluation |
| **Generative Agents** (UIST 2023, arXiv 2304.03442) | Retrieval score = recency + importance + relevance, with LLM-rated importance | Sliding window | Medium (citation) | **Must be cited** as the origin of multi-factor memory scoring; DSW adds a conversation-state factor and rule-based importance |
| **LUFY** (Dialogue & Discourse 2025, arXiv 2409.12524) | Six psychology-based metrics (arousal, surprise, …) with *learned* weights for retrieval and forgetting | Sliding window | Low | Supports dev-selected or learned weights; an arousal feature for importance (v2) |
| **MemoryBank** (arXiv 2305.10250) | Ebbinghaus forgetting curve; memory reinforced on recall | Sliding window | Low | Precedent for freshness decay |
| **Memoria** (arXiv 2512.12686) | Session summaries plus a weighted user knowledge graph | Summarization | Low | A neighbour for persona-level (L3) memory; it uses one fixed strategy |
| **RAG** (Lewis et al., arXiv 2005.11401) | Parametric + non-parametric generation over a dense index | Background | — | Foundational citation |
| **DPR** (EMNLP 2020) | Dense passage retrieval; BM25 + DPR hybrids help keyword-heavy sets | RAG retrieval | — | Hybrid lexical + dense (v2 option) |
| **Survey: Evaluation of RAG** (arXiv 2405.07437) | Retrieval and generation metrics (relevance, accuracy, faithfulness) | Evaluation | — | Metric vocabulary; we report retrieval (evidence hit, NDCG) and generation (judge, token-F1) separately |
| **Survey: Memory mechanisms of LLM agents** (arXiv 2404.13501) | Taxonomy of memory sources, forms and operations (write, manage, read) | Framing | — | Positions Syno as a *read-path* controller over three management strategies |
| **Review: RAG-driven memory architectures** (IEEE Access 2025) | Limits of vector stores; hybrid vector + knowledge graph + finite-state-machine designs | Framing | — | Supports hybrid, orchestrated memory designs |

## 2. What changes in the claims (summary; full text in CLAUDE.md §6.5)

- **Controller (headline): survives.** No paper switches between sliding window, summarization and
  RAG *per turn* with a logged, explainable, overridable decision.
  - MemGAS and RMM adapt *within* retrieval; Self-RAG decides retrieve-or-not; MemGPT lets the LLM
    page memory; MoMA routes models, not memory.
  - Two measured properties are added. The decision path is **LLM-free** (about 0.1 ms per
    decision, no LLM call). It is **Pareto-efficient** on mixed workloads (more accurate and cheaper
    than always-hybrid: `results/figures/pareto_controller.png`).
- **RAG claim 1 (write-time adaptive granularity): withdrawn as a performance claim.** It did not
  beat fixed segments on the test split, and MemGAS and SeCom cover adaptive granularity. It is kept
  as a design element; the v2 direction is a MemGAS-style read-time router.
- **RAG claim 2 (staleness flagging): narrowed** to *extraction-free, LLM-free staleness flagging
  on raw conversation chunks: structural (exact code-signature diff) where a key exists, calibrated
  NLI where none does.*
  - MemStrata needs clean (subject, relation, object) triples. Zep needs LLM-extracted edges and an
    LLM verifier.
  - We report MemStrata's own metrics on our data (§3), including the leak.
- **Summarization:** the live-loss-as-control-signal claim is untouched. The keyed merge is
  presented alongside MemStrata (deterministic keys), Mem0 (LLM UPDATE) and Zep (LLM invalidation).
- **Sliding window:** cite Generative Agents as the origin of multi-factor scoring, plus LUFY and
  MemoryBank. The claim stays evaluation-focused.

## 3. Staleness metrics in MemStrata's form (our test split; `eval/synthetic/retrieval/staleness.py`)

| Flagger (threshold chosen on dev) | Precision | Recall | Stale-fact leak | Current facts wrongly retired |
|---|---|---|---|---|
| Embedding similarity only | 0.64 | 1.00 | 0.00 | **0.83** |
| **NLI stage (ours)** | **0.82** | 0.73 | 0.27 | **0.23** |

- Both flaggers reach about the same F1 (0.78 vs 0.77). NLI's contribution is **precision**:
  similarity alone retires most compatible facts.
- By verifier: structural (signature diff) leaked 0 of 2 code contradictions, and NLI leaked
  28.6%. The structural sample is far too small to claim a rate.
- Ranking quality: cosine AUROC 0.70, NLI AUROC 0.70. That is consistent with MemStrata's point that
  similarity alone cannot tell a contradiction from a compatible restatement.
- **Present the 27% leak plainly.** It is the main motivation for the structural-first direction.

## 4. Improvements derived from the papers

| Change | From | Status |
|---|---|---|
| Pareto (cost vs accuracy) evaluation of the controller | MoMA, Mem0 | Done, from frozen test results |
| Staleness leak and false-supersession metrics | MemStrata | Done (§3) |
| Hybrid BM25 + dense retrieval (RRF) | DPR, Zep | **Mixed on dev:** +0.052 [+0.018, +0.088] on LoCoMo dev, but **−0.040 [−0.070, −0.015] on LoCoMo-Plus dev**. Failed its pre-registered gate, so it was not test-run; off |
| MMR redundancy-aware selection | xMemory, Zep | **No effect on dev:** +0.002 [−0.008, +0.009]. Dropped |
| Read-time entropy granularity router | MemGAS | v2 |
| Trained adapter reranker instead of MS MARCO | RMM | v2 |
| Sub-goal retrieval for multi-hop / implicit cues | GOAL-MEM | v2 (needs an LLM) |
| Novelty gate in front of NLI (speed) | SAGE | v2 |
| Probe-QA summary verification and repair | MemMA | v2 (§6.3 stretch) |
| L1 facts as retrievable units | LoCoMo (observations) | v2 |
| Arousal / emotion feature in importance | LUFY | v2 |

## 5. Dev results for the paper-derived retrieval options (LoCoMo dev split, 2026-10-15)

LoCoMo dev split: 5 conversations, 1,020 questions, budget 1,024 tokens. RAG evidence hit, with
paired differences against the frozen configuration (95% bootstrap intervals over conversations).
The frozen reference was re-run on Colab and reproduced the local value exactly (0.709).
**These are dev results only; the frozen test results in `results/RESULTS.md` are unchanged.**

| Configuration | Evidence hit | Answer in context | Multi-hop | Temporal | Single-hop | vs frozen |
|---|---|---|---|---|---|---|
| Embedding only | 0.542 | 0.355 | 0.19 | 0.54 | 0.66 | −0.167 [−0.210, −0.115] |
| + hybrid BM25 | 0.612 | 0.390 | 0.18 | 0.66 | 0.73 | −0.097 [−0.117, −0.080] |
| + hybrid + MMR | 0.615 | 0.393 | 0.18 | 0.68 | 0.73 | −0.094 [−0.115, −0.075] |
| **Frozen: reranker** | **0.709** | 0.476 | 0.31 | 0.74 | 0.83 | — |
| **Reranker + hybrid BM25** | **0.762** | 0.490 | 0.32 | 0.84 | 0.89 | **+0.052 [+0.018, +0.088]** |
| Reranker + MMR | 0.711 | 0.475 | 0.31 | 0.75 | 0.84 | +0.002 [−0.008, +0.009] |
| Reranker + hybrid + MMR | 0.760 | 0.486 | 0.30 | 0.84 | 0.89 | +0.050 [+0.011, +0.090] |

- **Hybrid lexical + dense retrieval helps**, with or without the reranker. The gain is in temporal
  and single-hop questions, where exact names, dates and numbers matter. Multi-hop does not improve
  (0.31 → 0.32); that is what GOAL-MEM's sub-goal retrieval targets.
- **MMR does not help** here: after reranking, near-duplicate chunks were not what pushed evidence
  out of the budget.
- Before adopting hybrid in a frozen v2 configuration, it should also be checked on synthetic
  controller val and the coding demo (code-task turns skip the reranker but would use hybrid).
