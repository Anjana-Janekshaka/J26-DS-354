# CEAI explained from zero (for a panel with no background)

Read top to bottom: it is written as something you can say aloud. Every technical word is explained
the first time it appears, and again in the glossary at the end.

---

## Part 1: The background, in everyday terms

**An LLM** (Large Language Model) is the kind of AI behind ChatGPT or Claude. You type a message,
it writes a reply.

**The model has no memory of its own.** Every time you send a message, the application must send the
model *everything it should know*: your new message, plus the earlier parts of the conversation it
needs. That bundle of text is called the **context**.

**The context has a size limit**, called the **context window**. Size is measured in **tokens**. A
token is a piece of a word, roughly three-quarters of a word on average. If a conversation runs
for hours, it no longer fits. Even when it does fit, sending more text costs more money and takes
longer.

So every chat application has to answer one question on every message: **"Of everything said so
far, what do we send to the model this time?"** The part of the software that answers it is called
the **memory system**. Each message in a conversation is a **turn**.

## Part 2: The three common ways to remember

There are three main approaches. A simple analogy is a person helping you with a long task.

1. **Sliding window: "remember only the last few minutes."** Send the most recent turns and drop
   the rest. Cheap and perfect for the thing you are doing right now. But anything said earlier is
   simply gone.
2. **Summarization: "keep meeting minutes."** Older parts of the conversation are condensed into a
   short summary. It keeps the gist of a long conversation in little space, but details (an exact
   number, the exact name of a function) get lost.
3. **RAG (Retrieval-Augmented Generation): "a filing cabinet with a search."** Every past turn is
   stored. When a new message arrives, the system searches the store for the passages most related
   to it and sends only those. Excellent for "what did I say about X weeks ago?", but it can miss
   the immediate recent flow of the conversation.

A fourth option is **hybrid**: half the space for recent turns, half for searched passages.

## Part 3: The problem we solve

**Every existing memory product picks one of these approaches when it is built, and uses it for the
whole conversation.** Products like Mem0, Zep, Letta and LangChain each lock in one strategy.

But real conversations **change type** as they go. In one session, a programmer with an AI coding
assistant might:

- chat about the project (the recent flow matters → sliding window);
- debug an error (the last few messages matter → sliding window);
- go off on a long side topic (the gist matters → summary);
- ask "what was that function I wrote earlier?" (a specific old detail matters → search/RAG).

**No single strategy is right for all of those.** Using the wrong one causes real mistakes. Two
examples we demonstrate live:

- **Duplicate-function trap:** an hour ago the assistant wrote a helper called `format_due_date`.
  Now you ask for "a helper that formats due dates". A memory that only keeps recent messages has
  forgotten it exists, so the assistant writes a second, duplicate one.
- **Renamed-API trap:** earlier you renamed a function's input from `user_id` to `uid`. Later you
  ask to use that function. If the memory gives the model the *old* version, the model writes code
  that breaks.

## Part 4: Our solution, CEAI

**CEAI is a memory system that chooses the right strategy for every single message, automatically,
and explains each choice.** It sits between the chat application and the AI model, as
**middleware**: software that sits in the middle.

On every turn, five steps happen:

1. **The Conversation Manager** looks at the new message and produces a short **signal**: how many
   turns so far; how full the context budget is; what *type* of message this is (chat, debugging,
   a question about the past, a request to write code, a request to change existing code); and
   whether the topic just changed.
2. **All three memory strategies prepare their version** of the context in parallel: the recent
   window, the summary, and the search results.
3. **The Controller** (we call it **ASSE**, the Adaptive Strategy Selection Engine) picks one
   version, using simple, readable rules. For example: "this is a request to write new code, so use
   hybrid, which brings back existing code before writing more"; "this is a question about the
   past, so use search".
4. **The decision is recorded** in a log, with a plain-English reason, and shown live on a
   **dashboard** (a web page). A person can **override** it, meaning force a different choice.
5. The chosen context is sent to the AI model with the user's message.

**Three design principles that make it trustworthy:**

- **It decides only from information available *before* the decision.** The strategies also report
  how good their own output is. For example, the summary reports how much information it lost. We
  deliberately do **not** let the controller use that report for the same message, because that
  would be circular (judging a choice by the result of having made it). Instead, the report acts as
  a **warning (an "escalation") that changes the *next* message's decision.** This keeps the system
  honest, simple and fast.
- **No AI inside the memory itself.** Every part of the memory (choosing, summarizing, searching,
  checking for outdated facts) uses fast rules and small, specialised models, never a large
  chat-style AI. Competitors call a large AI model dozens of times per conversation just to
  maintain memory.
- **Everything is explainable and correctable**: every decision has a written reason and can be
  overridden live.

## Part 5: The four components, simply

The project has four components, one per team member.

### Component 1: Dynamic Sliding Window (with the Conversation Manager)

Instead of blindly keeping "the last N messages", it **scores each past message** on four things
and keeps the best ones that fit:

- **Relevance:** how related the message is in meaning to the current one. Measured with
  **embeddings**: each piece of text is turned into a list of numbers that captures its meaning, so
  texts with similar meaning get similar numbers.
- **Freshness:** how recent the message is.
- **Importance:** whether it contains a decision, a definition, an error, a number (and not just
  "ok, thanks").
- **State:** whether it belongs to the current topic.

**Result:** it found the right earlier message far more often than "just keep the latest": better
in 59 cases and worse in 0 (recall 0.719 vs 0.556; *recall* = how often the needed message was
kept).

### Component 2: Hierarchical Summarization

Older conversation is condensed at **three levels** ("tiers"):

- **L1:** exact facts, word for word, including the exact definition of any code;
- **L2:** what the user was trying to do and what was decided;
- **L3:** a profile of who the user is and their overall goal.

Two special features:

- **Contradiction-resolving merge:** when a new fact replaces an old one ("I moved from Madrid to
  Berlin", or a renamed function), the old one is marked **superseded** (replaced), so the summary
  never contains both as if both were true.
- **A live "loss score":** every time it summarizes, it measures how much important information
  (names, numbers, code identifiers) it just dropped. If too much was lost, it raises the warning
  that makes the controller switch to search on the next message.

**Results:** outdated facts leaking into the summary: **0% vs 50%** for a simple summarizer. Exact
code definitions kept: **90% vs 0%**. The loss score closely tracks real information loss (a
**correlation** of 0.91, where 1.0 would mean perfectly in step).

### Component 3: Retrieval / RAG (search memory)

Every turn is stored in a **vector database**: a store that finds text by meaning, using the
embeddings described above. We use **FAISS**, a fast open-source library for this.

- **Chunking:** deciding whether to store each turn separately or group neighbouring turns into one
  "chunk".
- **Reranking:** after a fast first search, a second, more careful model (a **reranker**) re-orders
  the results. Because that model was trained on web text and ranks prose above code, we
  **switch it off for coding messages**. We found this by measuring it.
- **Staleness checking:** this is the novel part. When a new message arrives, the system checks
  whether it *contradicts* something stored earlier. "I moved to Berlin" makes "I live in Madrid"
  **stale** (out of date).
  - For ordinary text it uses an **NLI model** (Natural Language Inference: a small model trained
    to tell whether one sentence contradicts another).
  - For code it compares the exact function definitions using Python's own code parser (**AST**,
    the Abstract Syntax Tree: the parser's structured view of code), because the NLI model cannot
    tell `user_id` from `uid`.
  - Stale passages are **marked as outdated, never silently hidden**, and the newer passage is
    brought in next to them.
  - It does this **without any large AI model**. Competing systems need a large model, or neatly
    structured facts, to do it.

**Results:**

- When it flags something as stale, it is right **82%** of the time (**precision**), and it catches
  **73%** of the real contradictions (**recall**).
- An improved version (the **v4b** version below) is right **100%** of the time and never wrongly
  retires a current fact (0%, down from 23%). It catches slightly fewer contradictions (69%).
- Improvements to how results are read and ranked raised the share of questions where the needed
  evidence was found from **39% to 66%**.

### Component 4: The Controller (ASSE), the headline contribution

It picks the strategy for each message, using readable rules, in about **0.1 milliseconds**.

**Results:**

- On conversations that change type, it found the needed information **98.6%** of the time, against
  **87.4%** for the best single fixed strategy: **+11.2 points**. It also beat "always hybrid" by
  6 points, while sending less text.
- On a benchmark where the right answer is always "search", it **ties** search. It loses nothing by
  being adaptive.
- We also tried a **machine-learned** controller (learning the choices from recorded examples). It
  did worse (93% vs 99%), so we kept the readable rules.

## Part 6: How we tested it, and why you can trust the numbers

**A benchmark** is a standard test set that many researchers use, so results can be compared. We
used:

- **LoCoMo:** very long conversations (about 600 messages each) with questions about earlier
  parts. This is our main benchmark.
- **LoCoMo-Plus:** questions where the clue was implied, not stated directly.
- **BEAM:** a benchmark made by **other researchers**, with coding and general conversations. We
  never adjusted anything for it, so it is an independent check.
- **Our own test sets** for each component. For example, conversations that deliberately change
  type, and coding sessions with traps.

**Main measures:**

- **Evidence hit:** did the information needed to answer actually reach the model? It is
  objective and checkable.
- **Answer accuracy:** we let an AI model answer the question from the memory provided, and another
  AI model (the **judge**) mark it correct, partly correct or wrong. Because AI judges can be
  wrong, we also check a sample against human marking.
- **F1 score:** a standard score of how closely the answer's words match the correct answer.

**Fair testing rules we followed:**

- **Dev/test split:** we divide each dataset in two. We adjust the system only on the "dev" half
  and report results on the "test" half, which the system never saw. Testing on what you tuned on
  is like grading a student on the exact questions they practised.
- **Frozen system:** once settings were chosen, we locked them, and ran each test set **once**.
- **Pre-registration:** before trying any new improvement, we wrote down in advance what we would
  test and what result would count as success. Then we reported the outcome whatever it was.
  This prevents quietly keeping only the experiments that worked.
- **Confidence intervals:** every comparison comes with a range, for example "+0.112, between +0.093
  and +0.129". If the whole range is above zero, the difference is **statistically significant**:
  very unlikely to be luck.
- **Baselines:** we compared against other systems under identical conditions: same questions, same
  amount of memory space, same AI model, same judge.

## Part 7: How we compare with existing systems

**Mem0** is a popular commercial and open-source memory product. We ran the real Mem0 software on
the same tests.

| | CEAI | Mem0 |
|---|---|---|
| Answer accuracy (judged) | 50.7% | 46.7% (the difference is not significant, so we call it equal) |
| Exact-answer match (F1) | **0.406** | 0.278 (significantly better for CEAI) |
| AI-model calls needed to build memory, per conversation | **0** | about 54 |
| Time to build memory for one long conversation | **about 6 seconds** | about 16 minutes (162× slower) |
| Coding traps, original demo | **2 of 2 caught** | 0 of 2 |
| Coding traps, 12 new sessions | **16 of 26** | 5 of 26 |

Why Mem0 misses the coding traps: it rewrites what it remembers into short notes. It remembers
"a helper called `format_due_date` was added", but not the exact code, which is what the assistant
needs to reuse it correctly.

**Does it get better as conversations get longer?** Yes, compared with a simple window. CEAI stays
at 96–100% at every length, while the simple window gets worse: CEAI's advantage grows from +28
points in short conversations to +42 points in long ones.

## Part 8: What does not work yet (say this openly)

- **On the independent BEAM benchmark, CEAI scored below "always search"** (34.6% vs 44.5%).
  - The cause is found: many BEAM questions are phrased as requests ("Could you show me how…").
    The system mistakes them for casual chat and uses the summary, which lacks the detail.
  - The fix is the first item of future work.
- **In the 12 new coding sessions, "always hybrid" caught slightly more traps (18 vs 16).** The
  misses are mostly changed settings and functions renamed to a completely new name, which the
  staleness check does not yet recognise.
- **Making the summaries with a small AI model did not help.** So the default stays "no AI calls
  in memory".

Showing what does not work, and why, is part of doing research properly.

## Part 9: Improvements made this week

We tested three improvements, each first on its own:

- better scoring weights for the window;
- the improved staleness check;
- better chunking.

All three together (**v4**) broke something: the new window weights dropped messages even when
everything fitted. Our safety checks caught it, so it was not adopted. The version without the
window change (**v4b**) passed every check. It nearly doubled the score on the implied-clue
benchmark (0.134 → 0.264) and raised the main benchmark from 0.709 to 0.785 on the dev data. Its
final test runs are being completed. The official numbers remain those of the locked system.

## Part 10: Why it matters (who would use it)

- **Cheaper:** no extra AI bill for memory.
- **Faster:** memory is built in seconds instead of minutes.
- **Safer for coding assistants:** fewer duplicate or broken functions.
- **Private:** runs entirely on an ordinary laptop, offline. No conversation data leaves the
  machine.
- **Accountable:** every memory decision is written down and can be corrected, which matters for
  organisations that must explain what their AI was shown.

Users: companies building coding assistants and chatbots, organisations with privacy rules (health,
finance, government), and teams using small or local AI models.

**How it could be offered:** a free open-source library; a drop-in version that sits in front of any
chat app (change one web address); and a paid dashboard for teams.

## Part 11: The 30-second version

> "AI chat assistants have no memory of their own: on every message, software must decide what
> past conversation to send them. Today's memory products choose one method for the whole
> conversation, but conversations change: chatting, debugging, recalling, coding. CEAI chooses the
> right memory method for every single message, explains each choice, and lets a person override
> it. It needs no extra AI calls, so it is 162 times faster to build memory than Mem0. On
> conversations that change type, it finds the needed information 98.6% of the time vs 87.4% for
> the best fixed method. It catches coding mistakes that Mem0 and simple memory miss. We tested it
> fairly, with locked settings, pre-registered experiments and an independent benchmark, and we
> report where it still falls short."

---

## Glossary

| Term | Meaning |
|---|---|
| **AI judge** | An AI model used to mark answers correct / partly correct / wrong |
| **AST (Abstract Syntax Tree)** | How a programming language's parser represents code as structure; we use it to compare function definitions exactly |
| **ASSE / Controller** | Our component that picks the memory strategy for each message |
| **Baseline** | A simpler or existing system you compare against |
| **Benchmark** | A standard test set used by many researchers |
| **BEAM** | An independent benchmark by other researchers (coding and general conversations) |
| **Chunk / chunking** | A stored piece of conversation; deciding how big each stored piece is |
| **Confidence interval** | The range the true difference most likely lies in (95% sure) |
| **Context** | The text sent to the AI model with each message |
| **Context window** | The maximum amount of text a model can take at once |
| **Correlation** | How closely two measurements move together (1 = perfectly) |
| **Dashboard** | A web page showing each decision live |
| **Dev / test split** | Tune on one half of the data, report on the other, unseen half |
| **Embedding** | Text turned into numbers that capture its meaning, so similar meanings are close |
| **Escalation** | A warning from one component that changes the *next* decision |
| **Evidence hit** | Whether the information needed to answer reached the model |
| **F1 score** | How closely an answer's words match the correct answer (0 to 1) |
| **FAISS** | A fast open-source library for searching by meaning |
| **Frozen system** | Settings locked before final testing |
| **Hybrid** | Recent messages plus searched older passages, together |
| **LLM** | Large Language Model, the AI that writes replies (e.g. ChatGPT, Claude) |
| **LoCoMo / LoCoMo-Plus** | Benchmarks of very long conversations with questions about earlier parts (Plus: implied clues) |
| **Loss score** | How much important information a summary dropped |
| **Mem0** | A popular existing memory product we compared against |
| **Middleware** | Software that sits between two others (here: between the chat app and the AI model) |
| **NLI (Natural Language Inference)** | A small model that tells whether one sentence contradicts another |
| **Override** | A person forcing a different memory choice |
| **Precision** | Of the items flagged, how many were truly correct |
| **Pre-registration** | Writing down the test and success rule *before* running it |
| **RAG (Retrieval-Augmented Generation)** | Searching stored conversation and sending the most related passages |
| **Recall** | Of all the items that should have been found, how many were found |
| **Reranker** | A second, more careful model that re-orders search results |
| **Sliding window** | Sending only the most recent messages |
| **Stale / superseded** | Outdated: replaced by newer information |
| **Statistically significant** | Very unlikely to be due to chance |
| **Summarization (L1 / L2 / L3)** | Condensing old conversation: exact facts / intentions and decisions / user profile |
| **Token** | A piece of a word; the unit in which text size and cost are measured |
| **Turn** | One message in the conversation |
| **v4 / v4b** | This week's improved versions; v4 failed our checks, v4b passed |
