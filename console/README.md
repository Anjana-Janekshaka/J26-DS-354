# CEAI chat (for everyday users)

A normal AI chat where CEAI manages the memory. This is how a person would use CEAI day to day.

```
python -m console.chat              # opens http://127.0.0.1:8800/ (loads the models, about 20 s)
```

- Chat as usual. Under every reply, one line says which memory was used and which earlier
  messages it drew on. **Why?** opens the plain reason and exactly what the AI was shown.
- **Memory** menu next to Send: leave it on *Automatic*, or pick a method for one message (the
  controller's human override). It goes back to Automatic afterwards.
- The side panel shows how full memory is, a small track of this chat's memory switches, and
  whether the AI is connected. **Load a sample conversation** fills in 15 messages of a coding
  session so you can try the traps yourself (ask for a due-date helper, or to call `get_user_tasks`).

**Where replies come from:**

| Setup | Speed | How |
|---|---|---|
| Ollama on this computer (default if it is running) | about 1 minute per reply on a laptop CPU | Start Ollama; uses `qwen2.5:7b` (or `CEAI_CHAT_MODEL`) |
| A free hosted API, e.g. Groq | 1 to 2 seconds | Set `CEAI_LLM_BASE_URL=https://api.groq.com/openai/v1`, `CEAI_LLM_MODEL=llama-3.3-70b-versatile` and `CEAI_LLM_API_KEY` in your terminal (never in a file or chat), then restart |
| Nothing | instant | Memory-only mode: no answer, but "Why?" shows what the AI would have been shown |

Replies are capped at 400 tokens (`CEAI_CHAT_MAX_TOKENS`). Memory itself never calls an AI.

---

# Replay console (for the evaluators)

A browser view of the demo session for the presentation. A session is **recorded once** with the
real frozen system, then **replayed** turn by turn with no models, no network and no waiting, so
every presenter can jump straight to their own moment.

## Use

```
python -m console.record            # record the original session (about 1 minute, loads the models)
python -m console.record --all      # also the 12 held-out sessions (about 15 minutes)
python -m http.server 8799          # from the repo root; or open console/viewer.html directly
```

Then open <http://127.0.0.1:8799/console/viewer.html>. Opening the file directly also works.
URL options: `?scenario=<slug>&turn=<n>`.

| Key | Action |
|---|---|
| `→` / `←` (or space) | Next / previous message |
| `t` | Jump to the next trap |
| `1` / `2` | System tab / Controller tab |
| `d` | Show / hide details (files, scores, logged rationale) for Q&A |
| `a` | Autoplay (4 s per message) |
| `m` | Light / dark |
| `Home` / `End` | First / last message |

Click any block in the strategy timeline to jump to that exchange.

## Tabs

- **1 System:** the journey of the current message through `user_turn()`, with the real file for each
  step: override check, signal, the three candidates, the decision, the prompt, the escalations
  for the next turn, storing the message and the reply. At a trap, a CAUGHT/MISSED banner shows
  adaptive against the fixed 6-exchange window and each fixed strategy, all on the same history.
- **2 Controller (ASSE):** what the controller can and cannot see (Tier 0/1/2), the feature vector,
  the four decision steps (rule → dwell → escalations → override), the full rule table with the
  rule that fired, and the rationale exactly as logged.

Each tab ends with its claim, the closest systems and its number.

## Notes

- Recordings live in `console/recordings/` and are committed, so the viewer works offline on stage.
- `--fast` records without models (hashing embedder). Use it only to check the layout: the viewer
  shows a warning banner and trap results are not real.
- Recording writes no decision log and does not touch `runs/`. Nothing under `packages/` changes.
- The live override is still on the web dashboard (`python -m demo.coding_session.present`).
  The replay shows where an override would apply (step 4 of the controller tab).
