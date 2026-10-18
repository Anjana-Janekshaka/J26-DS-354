# Pre-registration: coding traps on Mem0 (roadmap 3.1)

Committed **before** any Mem0 coding run.

## Why

The demo currently compares CEAI with a fixed window. The question here: does a memory system people
actually use (Mem0) carry the trap evidence?

## Protocol

- **Scenarios:** the original session plus the 12 held-out sessions in
  `demo/coding_session/scenarios.py`, unchanged (26 held-out traps).
- **Mem0 setup:** `mem0ai` with the same local setup as the LoCoMo baseline: Qwen2.5-7B via Ollama,
  MiniLM embeddings, FAISS, and the corrected 8,000-token extraction limit
  (`docs/baselines_protocol.md`, amendment).
  - One `add()` per completed exchange (user message plus reply), which is how a chat app feeds it.
- **Two Mem0 arms**, both under the same 700-token budget as the CEAI demo:
  1. `mem0`: retrieved memories only.
  2. `mem0_plus_window`: retrieved memories plus the last 6 exchanges.
- **Check:** the same trap check as the CEAI arms (`check_trap` in `run_demo.py`).
- **Reference:** CEAI's numbers are the frozen-system run already recorded in
  `results/final/demo_scenarios/summary.json`. CEAI is not re-run.

## Reporting

- Report traps caught per arm and per trap kind, the number of Mem0 LLM calls, and any add failures,
  whatever the result.
- **Known limitation, stated in advance:** the check looks for exact text, for example
  `def compute_line_total(`. Mem0 stores rewritten memories, so a memory that keeps the *meaning*
  but not the exact signature counts as a miss. That is the point of the traps: the model needs the
  exact existing definition. Still, the first 15 retrieved memories of every trap are saved
  (`rows.jsonl`) so a reader can judge them.

## Outcome

Run once on Colab, 2026-10-18 (`results/final/demo_mem0/`). Mem0 worked normally: 3–14 LLM
calls per session and 0 failed `add()` calls.

| Arm | Original session | Held-out traps (26) | Duplicate | Rename | Signature | Config | Decision |
|---|---|---|---|---|---|---|---|
| **CEAI adaptive (frozen)** | **2/2** | **16** | 7/7 | 3/7 | 3/4 | 1/5 | 2/3 |
| Mem0 | 0/2 | 5 | 1/7 | 0/7 | 0/4 | 1/5 | **3/3** |
| Mem0 + last 6 exchanges | 0/2 | 6 | 1/7 | 1/7 | 0/4 | 1/5 | 3/3 |
| Fixed 6-exchange window | 0/2 | 3 | 0/7 | 1/7 | 2/4 | 0/5 | 0/3 |

**Reading:**

- Mem0 misses both original traps and catches 5 of 26 held-out traps; CEAI catches 2/2 and 16/26.
- **Why Mem0 misses, from its own memories:** it keeps *that* something exists but not the exact
  code. For the duplicate-function trap its top memory is "Helpers were added to
  `app/services/tasks.py`: `get_user_tasks` and `format_due_date`". It has the name, without the
  signature the model needs to reuse the function correctly.
- Mem0 is **better on project decisions** (3/3 vs 2/3): rewriting a rule as a short memory is
  exactly what it is built for.
- **Stated in advance, and holding:** the check needs exact text, which favours systems that keep
  the original turns. That is the property the traps test, but say it when presenting this.
