# Demo guide (Progress Presentation 1)

One page: how to run the live demo, what to say at each step, and what to do if something fails.
Everything runs on a laptop CPU with no internet and no LLM.

## Before the presentation (once, about 5 minutes)

```bash
.venv/Scripts/python -m demo.coding_session.present --delay 0 --no-browser --no-chat --out runs/present_warmup
```

- This downloads and caches the models, and checks that the session still ends 2/2 vs 0/2.
- It also writes the **offline fallback**: `runs/present_warmup/dashboard.html`.
- Open that file once in the browser and leave the tab open.

## Live demo (about 4 minutes)

```bash
.venv/Scripts/python -m demo.coding_session.present
```

1. **Model loading** (about 20 s). The dashboard opens in the browser. Put the terminal and the
   browser side by side.
2. **Press Enter for each exchange.** Each user turn prints the strategy the controller chose, the
   rule that fired and the decision time (about 0.1 ms). The dashboard timeline updates live.
3. **What to point out:**

   | Exchanges | Point out |
   |---|---|
   | 1–4 | The history still fits, so the cheap **sliding window** is used |
   | 5–8 | Debugging: still under budget, but a stale-fact flag from an earlier turn moves it to **hybrid** (read the escalation line) |
   | 9 | The rename: `get_user_tasks(user_id)` → `get_user_tasks(uid)` |
   | 10–15 | The long infrastructure detour. The history no longer fits: the window is held for a few turns (minimum dwell), then **RAG**. Watch **"escalation raised: loss_threshold_exceeded"**: the summarizer measured its own information loss. Per the leakage rule, it only changes the **next** turn's decision |
   | 16 | **Duplicate-function trap.** Build request → **hybrid**. Adaptive: **CAUGHT** (the existing `format_due_date` surfaces). Fixed window: **MISSED** |
   | 18 | **Renamed-API trap.** Refactor → summarization, switched to **RAG** by the loss escalation. Adaptive: **CAUGHT** (`get_user_tasks(uid`). Fixed window: **MISSED** |

4. **Manual override (live):** in the dashboard's *Manual override* card, choose a strategy (e.g.
   `rag`) and *Queue override*. Then press Enter in the terminal: the next decision shows
   `OVERRIDE by presenter`, and the dashboard marks it with a flag.
5. **Audience questions:** after the script, type any message. The controller decides and shows the
   context it would send to the model. Empty line to finish.

Other sessions, if asked "does it only work on this one?":

```bash
.venv/Scripts/python -m demo.coding_session.present --scenario invoice-service --delay 2
```

Also available: `event-pipeline`, `react-dashboard`, `download-cli`, `training-loop`, `django-shop`,
`go-client`, `user-db-migration`, `auth-module`, `async-scraper`, `platformer`,
`short-utils-control`.

## If something goes wrong

| Problem | Fix |
|---|---|
| Port 8765 busy | add `--port 8777` |
| Browser did not open | open `http://127.0.0.1:8765/` |
| Models will not load / no time | open `runs/present_warmup/dashboard.html` (static copy of the same session) and show `results/final/demo_scenarios/summary.json` |
| Want it hands-free | `--delay 3` auto-advances every 3 s |

## The numbers behind the demo (frozen system, run once)

- **Original session:** adaptive **2/2**, fixed 6-exchange window **0/2**.
- **12 unseen sessions (26 traps, pre-registered, written before running):** adaptive **16/26**,
  fixed window **3/26**, always-hybrid 18/26. Every duplicate-function trap was caught (7/7).
  - The misses are mostly changed constants and renamed functions, where the old version stays in
    the context unmarked. These are known limits of the structural staleness check
    (`docs/demo_scenarios_preregistration.md`).
