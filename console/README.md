/skin [syno|# Syno chat (for everyday users)
/skin [syno|
/skin [syno|A normal AI chat where Syno manages the memory. This is how a person would use Syno day to day.
/skin [syno|
/skin [syno|```
/skin [syno|python -m console.chat              # opens http://127.0.0.1:8800/ (loads the models, about 20 s)
/skin [syno|```
/skin [syno|
/skin [syno|- Chat as usual. Under every reply, one line says which memory was used and which earlier
/skin [syno|  messages it drew on. **Why?** opens the plain reason and exactly what the AI was shown.
/skin [syno|- **Memory** menu next to Send: leave it on *Automatic*, or pick a method for one message (the
/skin [syno|  controller's human override). It goes back to Automatic afterwards.
/skin [syno|- The side panel shows how full memory is, a small track of this chat's memory switches, and
/skin [syno|  whether the AI is connected. **Load a sample conversation** fills in 15 messages of a coding
/skin [syno|  session so you can try the traps yourself (ask for a due-date helper, or to call `get_user_tasks`).
/skin [syno|
/skin [syno|**Where replies come from:**
/skin [syno|
/skin [syno|| Setup | Speed | How |
/skin [syno||---|---|---|
/skin [syno|| Ollama on this computer (default if it is running) | about 1 minute per reply on a laptop CPU | Start Ollama; uses `qwen2.5:7b` (or `CEAI_CHAT_MODEL`) |
/skin [syno|| A free hosted API, e.g. Groq | 1 to 2 seconds | Set `CEAI_LLM_BASE_URL=https://api.groq.com/openai/v1`, `CEAI_LLM_MODEL=llama-3.3-70b-versatile` and `CEAI_LLM_API_KEY` in your terminal (never in a file or chat), then restart |
/skin [syno|| Nothing | instant | Memory-only mode: no answer, but "Why?" shows what the AI would have been shown |
/skin [syno|
/skin [syno|Replies are capped at 400 tokens (`CEAI_CHAT_MAX_TOKENS`). Memory itself never calls an AI.
/skin [syno|
/skin [syno|## In the terminal
/skin [syno|
/skin [syno|The same chat as a terminal app, modelled on the Hermes agent CLI's "modern" layout: a banner,
/skin [syno|a `❯` prompt, glyph rows instead of boxes, streamed replies and a status bar.
/skin [syno|
/skin [syno|```
/skin [syno|python -m console.tui                     # new chat
/skin [syno|python -m console.tui -c                  # continue the most recent chat
/skin [syno|python -m console.tui -r <number|id|title>
/skin [syno|python -m console.tui -q "one question"   # answer once and exit (-q - reads stdin)
/skin [syno|python -m console.tui --model qwen2.5:7b --budget 1000
/skin [syno|```
/skin [syno|
/skin [syno|**On screen.** `◆ memory` row above every reply (method, why, which earlier messages it drew on;
/skin [syno|`┊` rows for the three prepared methods in `/verbose verbose`), `∴ Thought for Ns` for reasoning
/skin [syno|models, `◈` reply, `─` summary line. The status bar shows the AI, memory fill (green / yellow /
/skin [syno|orange / red), the last and next method, queued messages, duration and the chat title, and
/skin [syno|shrinks on narrow terminals.
/skin [syno|
/skin [syno|**Keys.** Enter sends · Alt+Enter, Ctrl+J or a trailing `\` adds a line · Tab completes commands
/skin [syno|and their arguments, or accepts the grey suggestion from earlier inputs · Up/Down earlier inputs
/skin [syno|(kept across runs) · Ctrl+P command list · Ctrl+G write in your editor · Ctrl+S put the input aside
/skin [syno|and bring it back · Ctrl+C stop a reply / clear the input / twice to quit · Ctrl+D quit. Long pastes
/skin [syno|fold into `[pasted N lines #k]` and are sent in full. `!<command>` runs a shell command (not sent
/skin [syno|to the AI).
/skin [syno|
/skin [syno|**Commands** (any unique prefix works; `/h` is `/help`):
/skin [syno|
/skin [syno|| Group | Commands |
/skin [syno||---|---|
/skin [syno|| Session | `/new [title]`, `/clear`, `/history`, `/save [file.md]`, `/retry`, `/undo`, `/title [name]`, `/sessions`, `/resume <n>`, `/branch [name]`, `/btw <question>` (uses memory, not remembered), `/queue <msg>\|list\|rm N\|clear`, `/copy [N]` |
/skin [syno|| Memory | `/memory <auto\|recent\|summary\|search\|both>` (next message only), `/why`, `/context [all]`, `/track`, `/sample`, `/status`, `/usage` |
/skin [syno|| AI and display | `/model [name]`, `/connect`, `/personality [name\|none]`, `/verbose [off\|new\|all\|verbose]`, `/focus`, `/reasoning [show\|hide]`, `/skin [ceai\|ocean\|amber\|mono]`, `/indicator [kaomoji\|emoji\|unicode\|ascii]`, `/statusbar`, `/timestamps`, `/footer`, `/bell`, `/config` |
/skin [syno|| Info | `/help [word]`, `/version`, `/redraw`, `/quit [--delete]` |
/skin [syno|
/skin [syno|`/new`, `/clear`, `/undo` and `/quit --delete` ask first; add `-y` to skip. Chats, settings and
/skin [syno|input history are saved in `~/.ceai` (or `CEAI_HOME`). A saved chat keeps only the messages, the
/skin [syno|replies and your per-message memory choices; resuming rebuilds the memory by replaying them, with
/skin [syno|no AI calls, so the decisions come out the same. Needs `prompt_toolkit` (`pip install -e ".[tui]"`);
/skin [syno|without it, a plain prompt is used.
/skin [syno|
/skin [syno|Left out on purpose, because Syno is a chat with managed memory rather than a tool-using agent:
/skin [syno|tools, skills, MCP, subagents and `/bg`, cron and `/loop`, worktrees, voice, browser, messaging
/skin [syno|platforms, billing, pets. `/compress` is what the memory methods already do every message.
/skin [syno|
/skin [syno|---
/skin [syno|
/skin [syno|# Replay console (for the evaluators)
/skin [syno|
/skin [syno|A browser view of the demo session for the presentation. A session is **recorded once** with the
/skin [syno|real frozen system, then **replayed** turn by turn with no models, no network and no waiting, so
/skin [syno|every presenter can jump straight to their own moment.
/skin [syno|
/skin [syno|## Use
/skin [syno|
/skin [syno|```
/skin [syno|python -m console.record            # record the original session (about 1 minute, loads the models)
/skin [syno|python -m console.record --all      # also the 12 held-out sessions (about 15 minutes)
/skin [syno|python -m http.server 8799          # from the repo root; or open console/viewer.html directly
/skin [syno|```
/skin [syno|
/skin [syno|Then open <http://127.0.0.1:8799/console/viewer.html>. Opening the file directly also works.
/skin [syno|URL options: `?scenario=<slug>&turn=<n>`.
/skin [syno|
/skin [syno|| Key | Action |
/skin [syno||---|---|
/skin [syno|| `→` / `←` (or space) | Next / previous message |
/skin [syno|| `t` | Jump to the next trap |
/skin [syno|| `1` / `2` | System tab / Controller tab |
/skin [syno|| `d` | Show / hide details (files, scores, logged rationale) for Q&A |
/skin [syno|| `a` | Autoplay (4 s per message) |
/skin [syno|| `m` | Light / dark |
/skin [syno|| `Home` / `End` | First / last message |
/skin [syno|
/skin [syno|Click any block in the strategy timeline to jump to that exchange.
/skin [syno|
/skin [syno|## Tabs
/skin [syno|
/skin [syno|- **1 System:** the journey of the current message through `user_turn()`, with the real file for each
/skin [syno|  step: override check, signal, the three candidates, the decision, the prompt, the escalations
/skin [syno|  for the next turn, storing the message and the reply. At a trap, a CAUGHT/MISSED banner shows
/skin [syno|  adaptive against the fixed 6-exchange window and each fixed strategy, all on the same history.
/skin [syno|- **2 Controller (ASSE):** what the controller can and cannot see (Tier 0/1/2), the feature vector,
/skin [syno|  the four decision steps (rule → dwell → escalations → override), the full rule table with the
/skin [syno|  rule that fired, and the rationale exactly as logged.
/skin [syno|
/skin [syno|Each tab ends with its claim, the closest systems and its number.
/skin [syno|
/skin [syno|## Notes
/skin [syno|
/skin [syno|- Recordings live in `console/recordings/` and are committed, so the viewer works offline on stage.
/skin [syno|- `--fast` records without models (hashing embedder). Use it only to check the layout: the viewer
/skin [syno|  shows a warning banner and trap results are not real.
/skin [syno|- Recording writes no decision log and does not touch `runs/`. Nothing under `packages/` changes.
/skin [syno|- The live override is still on the web dashboard (`python -m demo.coding_session.present`).
/skin [syno|  The replay shows where an override would apply (step 4 of the controller tab).
