# Pre-registration: aggregate coding-demo scenarios (roadmap 3.2)

Committed **before the first run** of any scenario below. The frozen system is not changed.

## Why

The coding demo has one scripted session (2/2 vs 0/2). One hand-built session invites the question
"was the demo built to work?". This adds 12 more sessions, written without running them, and reports
an aggregate catch rate.

## What is fixed by this commit

- **Scenarios:** `demo/coding_session/scenarios.py`, 12 held-out sessions with 26 traps:
  - 9 Python sessions (one is the control), plus TypeScript, Go and SQL.
  - Trap kinds: duplicate (7), rename (7), signature (4), config (5), decision (3). Kinds are listed
    per trap in the file.
  - Traps deliberately outside what the system was built around:
    - non-Python code (the structural signature check is Python-only);
    - changed constants and project decisions (no function signature to diff);
    - a short control session (`short-utils (control)`), where a plain recent window should succeed.
  - `tests/test_demo_scenarios.py` checks only structure (the evidence is planted where stated, and
    the trap question does not contain the answer).
- **System:** frozen (`CEAI_SYSTEM=frozen`), reranker on with the code-task skip, budget 700
  tokens. These are the same settings as `python -m demo.coding_session.run_demo`.
- **Harness:** `python -m demo.coding_session.run_scenarios`. It uses the same trap check as the
  original demo:
  - The required text must be in the context the model would receive.
  - A stale form, if present, must be marked stale.
- **Arms:** adaptive, a fixed 6-exchange window, and always sliding window / summarization / RAG /
  hybrid, all assembled from the same module outputs.

## Primary number

The catch rate over the **held-out** traps, adaptive vs the fixed 6-exchange window and vs each
always-one-strategy arm. Also reported:

- per trap kind;
- the original scenario separately, because the system was developed against it;
- held out excluding the control session.

## Rules

1. The scenarios and the system are not edited after the first run. If a scenario has a bug, the
   fix is reported as an amendment, and the result is reported both before and after the fix.
2. Every result is reported, including traps adaptive misses, together with the reason for each
   miss.
3. No claim of statistical significance: 26 traps are a stress test, not a benchmark. Present it as
   "caught X of 26 traps in 12 unseen sessions" next to the fixed-window number.

## Outcome (run once, 2026-10-17; `results/final/demo_scenarios/summary.json`)

Original scenario: adaptive 2/2, fixed window 0/2 (unchanged).

**Held-out traps caught (26 traps in 12 unseen sessions):**

| Arm | All | Config | Decision | Duplicate | Rename | Signature |
|---|---|---|---|---|---|---|
| Fixed 6-exchange window | 3 | 0/5 | 0/3 | 0/7 | 1/7 | 2/4 |
| Always sliding window | 9 | 0/5 | 1/3 | 7/7 | 1/7 | 0/4 |
| Always summarization | 11 | 0/5 | 1/3 | 6/7 | 1/7 | 3/4 |
| Always RAG | 16 | 1/5 | 3/3 | 7/7 | 2/7 | 3/4 |
| Always hybrid | **18** | 1/5 | 3/3 | 7/7 | 4/7 | 3/4 |
| **Adaptive** | **16** | 1/5 | 2/3 | 7/7 | 3/7 | 3/4 |

**Reading:**

- Adaptive catches 16 of 26 against 3 of 26 for the fixed window, and **every duplicate-function
  trap (7/7)**.
- It does **not** beat always-hybrid here (16 vs 18). The demo claim is "far better than a fixed
  window", not "better than every fixed strategy".
- Nine of adaptive's ten misses share one cause: **an old version stays in the context unmarked**.
  - Changed constants (`TAX`-style values; 1/5 caught).
  - Functions renamed to a *new name* (the signature diff matches same-name symbols only).
  - Non-Python signatures (TypeScript, Go), which the Python-only AST check does not parse.
  - This includes the control session: every arm carries both versions of `batched` unmarked, so the
    strict check counts it as missed even by the plain window.
- The other miss is a project decision (a chunk-size rule) that adaptive routed to summarization,
  whose rule-based extraction did not keep it.

These are known limits of the structural staleness check, now measured. Any fix is new work. It must
be developed on new dev scenarios and evaluated on a *fresh* held-out batch written before running,
never on these 12.
