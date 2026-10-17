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

To be filled in after the run (Colab notebook job `mem0_coding_traps`).
