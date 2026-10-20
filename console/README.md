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

## In the terminal

The same chat as a terminal app, modelled on the Hermes agent CLI's "modern" layout: a banner,
a `❯` prompt, glyph rows instead of boxes, streamed replies and a status bar.

```
python -m console.tui                     # new chat
python -m console.tui -c                  # continue the most recent chat
python -m console.tui -r <number|id|title>
python -m console.tui -q "one question"   # answer once and exit (-q - reads stdin)
python -m console.tui --model qwen2.5:7b --budget 1000
```

**On screen.** `◆ memory` row above every reply (method, why, which earlier messages it drew on;
`┊` rows for the three prepared methods in `/verbose verbose`), `∴ Thought for Ns` for reasoning
models, `◈` reply, `─` summary line. The status bar shows the AI, memory fill (green / yellow /
orange / red), the last and next method, queued messages, duration and the chat title, and
shrinks on narrow terminals.

**Keys.** Enter sends · Alt+Enter, Ctrl+J or a trailing `\` adds a line · Tab completes commands
and their arguments, or accepts the grey suggestion from earlier inputs · Up/Down earlier inputs
(kept across runs) · Ctrl+P command list · Ctrl+G write in your editor · Ctrl+S put the input aside
and bring it back · Ctrl+C stop a reply / clear the input / twice to quit · Ctrl+D quit. Long pastes
fold into `[pasted N lines #k]` and are sent in full. `!<command>` runs a shell command (not sent
to the AI).

**Commands** (any unique prefix works; `/h` is `/help`):

| Group | Commands |
|---|---|
| Session | `/new [title]`, `/clear`, `/history`, `/save [file.md]`, `/retry`, `/undo`, `/title [name]`, `/sessions`, `/resume <n>`, `/branch [name]`, `/btw <question>` (uses memory, not remembered), `/queue <msg>\|list\|rm N\|clear`, `/copy [N]` |
| Memory | `/memory <auto\|recent\|summary\|search\|both>` (next message only), `/why`, `/context [all]`, `/track`, `/sample`, `/status`, `/usage` |
| AI and display | `/model [name]`, `/connect`, `/personality [name\|none]`, `/verbose [off\|new\|all\|verbose]`, `/focus`, `/reasoning [show\|hide]`, `/skin [ceai\|ocean\|amber\|mono]`, `/indicator [kaomoji\|emoji\|unicode\|ascii]`, `/statusbar`, `/timestamps`, `/footer`, `/bell`, `/config` |
| Info | `/help [word]`, `/version`, `/redraw`, `/quit [--delete]` |

`/new`, `/clear`, `/undo` and `/quit --delete` ask first; add `-y` to skip. Chats, settings and
input history are saved in `~/.ceai` (or `CEAI_HOME`). A saved chat keeps only the messages, the
replies and your per-message memory choices; resuming rebuilds the memory by replaying them, with
no AI calls, so the decisions come out the same. Needs `prompt_toolkit` (`pip install -e ".[tui]"`);
without it, a plain prompt is used.

Left out on purpose, because CEAI is a chat with managed memory rather than a tool-using agent:
tools, skills, MCP, subagents and `/bg`, cron and `/loop`, worktrees, voice, browser, messaging
platforms, billing, pets. `/compress` is what the memory methods already do every message.

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
