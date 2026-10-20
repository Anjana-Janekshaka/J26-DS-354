# Pre-registration: v5_recall, routing recall requests like questions (controller)

Written **before** any run of the candidate. Plan, gates and test runs are fixed here; every result
is reported whatever its sign.

## Why

The frozen system's BEAM run (`docs/beam_preregistration.md`, 2026-10-17) found a routing failure:

- Probes phrased as requests or statements ("Can you list…", "Could you show me…") are classified
  `chat` or `exploration`, not `qa`.
- Over budget, the long-conversation rule sends them to **summarization**, which scores 0.03
  evidence hit on them against 0.28 for RAG.
- Overall adaptive is **−0.099 [−0.135, −0.065]** below always-RAG on BEAM. The same failure mode was
  seen on LoCoMo-Plus.

The controller only sees the task type, so it cannot tell "chat" from "a request to recall something
said earlier".

## Candidate (`CEAI_SYSTEM=v5_recall`)

The frozen system plus two changes. Retrieval, summarization, the window and every frozen threshold
are unchanged.

1. **Conversation manager: a Tier 0 cue `TurnSignal.recall_request`** (`is_recall_request` in
   `packages/conversation_manager/classifier.py`). It is computed from the user message's phrasing
   only, before any module runs, so §5 holds. It is true when either:
   - the message uses explicit memory phrasing ("remind me", "do you remember", "can you recall"), or
   - it refers back to earlier conversation ("I mentioned", "we discussed", "did you suggest",
     "you told me", "earlier in our conversation", "in our previous chat", "my original plan"…)
     **and** it is a request or a question (ends with "?", or starts with "can/could/would you",
     "list", "tell", "show", "give", "remind", "describe", …).
   - Requests to *summarize* are deliberately not flagged; they stay with summarization.
2. **Controller rule `recall_request`** (`packages/controller/rules.py`, config
   `recall_requests_as_qa=True`). A `chat` or `exploration` turn flagged as a recall request, with
   history over budget, is handled exactly like a `qa` turn, using the frozen `qa_strategy` (RAG).
   - It is a hard rule, placed after the code-task rules and before the long-conversation rule.
   - Under budget the window stays (lossless), and code task types keep their own rules.

**No free parameter is tuned.** The target strategy is the frozen `qa_strategy`; the patterns were
written from general phrasing of memory requests.

**What was seen before writing this:** the BEAM pre-registration's diagnosis quotes two probe openings
("Can you list the order in which I…", "Could you show me how to…"), and the per-category BEAM
summary. **No other BEAM question was read**, and no pattern was fitted to BEAM. BEAM stays a test set.

## Gates (dev/val only; `python -m eval.v4_gate --system v5_recall --out runs/v5_recall_gates`)

The same gates as v4, frozen vs v5_recall under identical conditions. A dev gate fails when the
paired 95% CI of v5_recall − frozen lies entirely below 0.

| Gate | Set | Metric |
|---|---|---|
| G1 | Coding demo + 12 held-out scenarios | original 2/2; held-out catches not below frozen (16/26) |
| G2 | Synthetic controller **val** | adaptive evidence hit |
| G3 | LoCoMo-Plus **dev** (10 warm-up turns) | adaptive cue hit |
| G4 | LoCoMo **dev** (NLI off) | adaptive evidence hit |

The frozen reference runs must reproduce the recorded dev values (0.992, 0.134, 0.709); if they do not,
the environment differs and the comparison is reported as such.

Also reported (no gate): how often the cue fires on each dev set, and the controller's choice
distribution, so a rule that never fires is visible as such.

## Test runs (only if all gates pass; each exactly once)

`python -m eval.v5_test`, frozen and v5_recall back to back on each (the frozen per-question rows
are not on this machine, so frozen is re-run; it must reproduce its recorded summary):

1. **BEAM 100K**: evidence hit and answer in context (primary target of this change).
2. Synthetic controller **test**: evidence hit (the headline result must not regress).
3. LoCoMo **test** (NLI off): evidence hit.
4. LoCoMo-Plus **test** (10 warm-up turns): cue hit.

**Reporting:** v5_recall − frozen with paired conversation-level (item-level for LoCoMo-Plus) 95%
bootstrap CIs, plus adaptive − RAG on BEAM, whatever the sign.

## Decision rule

- **All gates pass and BEAM improves** (CI above 0) with no test split significantly worse: present
  as *"v5_recall, pre-registered: recall requests are routed like questions"*, with the frozen numbers
  next to it.
- **Any gate fails:** no test run; reported as a negative, and the frozen system stays.
- **Gates pass but BEAM does not improve, or another test split is significantly worse:** reported
  as is; not adopted.

## Outcome

(To be filled after the runs.)
