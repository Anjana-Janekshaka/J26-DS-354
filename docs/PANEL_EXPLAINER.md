# CEAI explained from zero (for a panel with no background)

Written to be read aloud. Every unusual word is explained in brackets the first time it appears,
like this: *token (a small piece of a word)*. All terms are also collected in the glossary at the
end. File names such as `pipeline.py` are the real files in our code, so you can open them if
asked.

---

## Part 1: Background in everyday words

- **LLM** (Large Language Model: the kind of AI behind ChatGPT or Claude, which reads text and
  writes a reply).
- **The model has no memory of its own.** Every time you send a message, the app must send the model
  everything it should know: your new message, plus whatever earlier parts of the conversation it
  needs. That bundle of text is called the **context** (the text handed to the model together with
  your message).
- **The context has a size limit**, called the **context window** (the most text the model can read
  at once). Size is counted in **tokens** (small pieces of words; about four tokens make three
  words). Long conversations stop fitting. Sending more text also costs more money and time.
- So on every message the app must answer one question: *"Of everything said so far, what do we send
  this time?"* The part of the software that answers it is the **memory system**. One message in a
  conversation is a **turn** (one message from either the user or the assistant).

## Part 2: The three usual ways to remember

Think of a human assistant helping you with a long task.

1. **Sliding window** (keep only the most recent messages; older ones fall off the end, like a
   window sliding along the conversation). Cheap, and great for what you are doing *right now*. But
   older facts are simply gone.
2. **Summarization** (rewrite older messages into a shorter summary, like meeting minutes). Keeps
   the gist of a long conversation in little space, but exact details (a number, the exact name and
   inputs of a function) get lost.
3. **RAG**, Retrieval-Augmented Generation (store every message, and for each new message *search*
   the store for the most related old passages and send only those, like a filing cabinet with a
   search box). Excellent for "what did I say about X weeks ago?", but it can miss the recent flow.

A fourth option, **hybrid** (half the space for recent messages, half for searched passages), mixes
1 and 3.

## Part 3: The problem

**Every existing memory product picks one of these approaches when it is built, and uses it for
the entire conversation.** Mem0, Zep, Letta and LangChain (well-known memory products and toolkits
for AI apps) each lock in one strategy.

**But real conversations change type.** In one session with an AI coding assistant, a programmer
may:

- chat about the project (recent flow matters);
- debug an error (debug: find and fix a fault; the last few messages matter);
- go on a long side topic (the gist matters);
- ask about something from an hour ago (one exact old detail matters).

No single method is right for all of these, and the wrong one causes real mistakes. We show two
live:

- **Duplicate-function trap.** An hour ago the assistant wrote a helper called `format_due_date`
  (a *function*: a named, reusable piece of code). Now you ask for "a helper that formats due
  dates". A memory that keeps only recent messages has forgotten it, so the assistant writes a
  second copy.
- **Renamed-API trap** (API, Application Programming Interface: the name and inputs you use to call
  a piece of code). Earlier you renamed the input of `get_user_tasks` from `user_id` to `uid`.
  Later you ask to use that function. If memory hands the model the old version, the code it writes
  is broken.

## Part 4: Our solution in one sentence

**CEAI chooses the best memory method for every single message, automatically, writes down why,
and lets a person override (overrule) the choice.** It is **middleware** (software that sits in the
middle, here between the chat app and the AI model), so the app and the model do not need to change.

---

## Part 5: The journey of one message, step by step, with the files that run it

We follow a real message from our demo (the scripted coding session we run live), message 18:

> **"Now call get_user_tasks from the weekly digest job for each subscribed user."**

Seventeen messages came before it. Among them: the function was written at message 2, renamed
(`user_id` → `uid`) at message 9, and then six messages were spent on an unrelated side topic.

The whole journey is run by one function, `user_turn()` in **`integration/pipeline.py`** (the "turn
loop": the code that runs once for every user message). It does the steps below in order.

### Step 0: Check for a human override

`user_turn()` first asks `decision_logger/logger.py` whether anyone pressed **override** on the
dashboard (a web page showing the system's decisions live; file `dashboard/server.py`). If so, the
request is passed to the controller (the part that makes the choice, Step 3). In this example,
nobody did.

### Step 1: The Conversation Manager reads the message

File: **`conversation_manager/manager.py`**, function `observe()`. It:

1. **Gives the message an id** ("t0035") and counts it: this is turn number 35, counting both
   sides.
2. **Counts tokens** using **tiktoken** (a standard library, i.e. ready-made code, that counts
   tokens exactly as AI models do), and works out **token-budget pressure** (how full the memory
   space is: 0 = empty, 1 = full or overflowing). Here it is **1.00**: the conversation no longer
   fits.
3. **Classifies the message type** in `conversation_manager/classifier.py`, using **patterns**
   (rules that look for telltale words). Words like *rename*, *refactor* or *call … from* mean
   **code_refactor** (changing or using existing code). Other types are *debugging*,
   *code_generation* (writing new code), *qa* (a question about the past) and *chat*.
   - Here "call get_user_tasks from …" matches the code_refactor pattern.
4. **Checks for a topic shift** (the subject suddenly changing). It turns the message into an
   **embedding** (a list of numbers that captures meaning, so sentences that mean similar things get
   similar numbers; made by the small model **MiniLM**) and compares it with the recent topic. A big
   drop in similarity, or words like "switching gears", means a shift.
5. **Publishes a signal**: the **TurnSignal** (a small standard message: turn id, turn count, task
   type, token usage, topic state), sent on the **signal bus** (`conversation_manager/bus.py`: a
   simple broadcast line every component listens to).

The shapes of these messages are fixed in **`contracts/schemas.py`**. These are the *contracts*
(agreed formats that every component must use, checked automatically by a library called
**Pydantic**). If any component sends a wrongly shaped message, it is rejected immediately.

### Step 2: All three memory methods prepare their version, at the same time

`user_turn()` starts the three methods **in parallel** (at the same time, on separate threads:
independent lines of work inside one program). Each produces a **candidate context** (its proposal
for what to send the model).

**(a) Sliding window**: `sliding_window/window.py`, function `build_context()`. It gives every
past message a **composite score** (one combined score), built from four parts in
`sliding_window/scoring.py`:

- **relevance**: how close in meaning the old message is to the new one, measured as **cosine
  similarity** (a number from 0 to 1 comparing two embeddings; 1 = same meaning);
- **freshness**: how recent it is; it halves every 8 turns (a *half-life* of 8);
- **importance**: whether it contains code, a decision, a rule, an error, numbers. "ok thanks" scores
  0;
- **state**: whether it belongs to the current topic.

It always keeps the last 2 messages, then adds the highest-scoring ones until the token budget is
full, and puts them back in time order.

**(b) Summarization**: `summarization/engine.py`, function `build_context()`. As the conversation
went on, older messages were already rolled up (every 6 messages) into three **tiers** (levels of
detail):

- **L1** (exact facts, copied word for word, including exact code *signatures*: the function's name
  and inputs, e.g. `get_user_tasks(uid, include_done=False)`), made by `summarization/extract.py`
  with Python's **AST** (Abstract Syntax Tree: Python's own way of reading code as a structure, so
  signatures are captured exactly);
- **L2** (what the user was trying to do and what was decided);
- **L3** (a short profile of who the user is and their overall goal).

Two key features:

- **Contradiction-resolving merge** (`summarization/merge.py`). When message 9 renamed the input,
  the old fact `get_user_tasks(user_id…)` was marked **superseded** (replaced by newer
  information, with the time it was replaced). The summary never presents both as true.
- **Loss score** (`summarization/loss.py`: a live measure of how much important information the
  summary dropped). It collects the **anchors** (checkable details: names, numbers, code
  identifiers) of the summarized messages and counts how many are missing from the summary. On the
  previous message this score was **0.59** (59% of anchors missing), far above the alarm level of
  **0.15**.

**(c) RAG / search**: `retrieval/engine.py`, function `build_context()`.

- Every earlier message was stored in a **vector database** (a store that finds text by meaning,
  using embeddings). We use **FAISS** (a fast open-source search library from Meta),
  `retrieval/index.py`.
- It searches for the passages closest in meaning to message 18.
- For non-code messages, a **reranker** (`retrieval/rerank.py`: a second, slower but more careful
  model that re-orders the search results) refines the order. For coding messages like this one the
  reranker is **switched off**, because we measured that it ranks ordinary prose above code.
- It packs the best passages into the token budget.
- **Staleness check** (checking whether a stored passage has become out of date). This is done when
  each message is first stored, in `retrieval/contradiction.py`:
  - **Code:** if a newer message redefines the same function with different inputs, the old passage
    is flagged stale, using an exact AST comparison.
  - **Ordinary sentences:** an **NLI model** (Natural Language Inference: a small model trained to
    tell whether one sentence contradicts another) checks pairs of sentences, in both directions.
    One example: "I live in Madrid" vs "I moved to Berlin".
  - A stale passage is never hidden. It is labelled **"[!] stale: superseded by …"**, and the newer
    passage is placed right next to it.
- Whether each message is stored alone or grouped with neighbours is the **chunking** decision
  (`retrieval/chunking.py`; a *chunk* is one stored piece).

### Step 3: The controller chooses, using only the signal

File: **`controller/controller.py`**, function `decide()`, with the rules in
**`controller/rules.py`**. The controller is called **ASSE** (Adaptive Strategy Selection Engine).

**Important design rule:** `decide()` receives **only the TurnSignal from Step 1**, never the three
candidate contexts from Step 2. It decides from information known *before* the methods run.
(Otherwise it would judge a choice by the result of making it, which is circular and called
*leakage*: information leaking from after the decision into the decision.)

It builds a **feature vector** (the short list of facts it decides from): turn count, budget
pressure, message type, previous choice, turns since the last switch. Then it checks the rules in
order:

| Rule | Choice |
|---|---|
| The whole history still fits | sliding window (nothing is lost) |
| A question about the past (qa) | RAG |
| A request to write new code | hybrid (bring back existing code first) |
| A request to change existing code (refactor) | summarization (it holds the current signatures) |
| Debugging | sliding window |
| Long casual chat | summarization |

For message 18, the rule says **refactor → summarization**. But there is a **pending escalation**
(a warning from an earlier turn). On message 17 the summary's loss score was 0.59, above 0.15, so
the warning says *"the summary is losing too much; switch summarization to RAG"*. The final choice
is **RAG**.

Two more mechanisms:

- **Dwell time** (a minimum number of turns before switching again, to stop the choice flipping back
  and forth).
- **Override** (a human's choice, which replaces the rule's choice and is marked "OVERRIDE by …").

It writes a **rationale** (a plain-English reason), e.g.: *"[refactor_request] task_type=code_refactor
→ summarization | escalation from t0033: summary loss 0.59 > 0.15 → switch summarization to RAG"*.
The decision takes about **0.1 milliseconds**.

### Step 4: Build the final prompt

File: **`integration/llm_interface.py`**, function `assemble_prompt()`. It takes the chosen
method's candidate context and wraps it with an instruction for the model ("prefer current facts;
never use anything marked stale; reuse existing definitions"). The result is the **prompt** (the
full text sent to the AI model). For hybrid, it combines searched passages (up to half the budget)
with recent messages, without duplicates.

### Step 5: Record everything, and raise warnings for the next turn

- **Decision log**: `decision_logger/logger.py` appends one line to **`decisions.jsonl`**
  (**JSONL**: a text file with one structured record per line; **append-only**: lines are only ever
  added, never edited, so the history cannot be quietly changed). The line holds the signal, the
  feature vector, the decision and all three candidates.
- **Escalations** (warnings) are created by `_escalations()` in `pipeline.py` from what the methods
  reported in Step 2:
  - "summary loss too high", and
  - "new stale passages found".

  They are saved to `escalations.jsonl` and queued for the controller. **They affect only the next
  message.** That is exactly how the warning from message 17 changed message 18.
- **Dashboard**: `dashboard/server.py` reads these files and shows the decision live in the browser.

### Step 6: Remember the new message

`_ingest()` in `pipeline.py` hands the message to all three methods to store:

- the window adds it to its list;
- the summarizer adds it and, every 6 messages, rolls older ones into L1/L2/L3;
- RAG embeds it, decides its chunk, stores it in FAISS and runs the staleness check against older
  passages.

### Step 7: The AI model replies

The prompt goes to the AI model through `integration/llm_client.py` (a connector that works with any
model offering the standard "OpenAI-compatible" interface, the common way programs talk to AI
models). The reply is itself stored as a turn. **This is the only place a large AI model is used;
the memory system itself never calls one.**

### The outcome for message 18

- The context sent to the model contains the **new** signature `def get_user_tasks(uid` and no
  unmarked old version: **CAUGHT** (the trap was avoided).
- A fixed window of the last 6 exchanges (an *exchange* is one user message plus one reply) no longer
  contains the function at all: **MISSED**.
- On message 16 (the duplicate-function trap), the rule "write new code → hybrid" brought back
  `def format_due_date(` from message 2: **CAUGHT**; the fixed window **MISSED**.

The demo runs all of this live: `python -m demo.coding_session.present`, which uses
`demo/coding_session/present.py` with the script in `demo/coding_session/script.py`.

---

## Part 6: The four components and their results

Each team member owns one.

### 1. Dynamic Sliding Window (with the Conversation Manager)

- **What:** the scored window from Step 2a, plus the message reading in Step 1.
- **Result:** we planted a fact, asked about it later, and checked whether the window kept the
  message holding it.
  - The scored window kept it **71.9%** of the time. A plain "keep the latest messages" window
    (**recency-only**: choosing by time alone) kept it 55.6%. This is called **recall** (the share
    of needed items that were actually found).
  - It was better in **59** cases and worse in **0**.
- **Honest note:** equal weights for the four scores are not the best. Relevance matters most.

### 2. Hierarchical Summarization

- **What:** the L1/L2/L3 summaries, the merge and the loss score from Step 2b.
- **Results:**
  - **Stale-fact leakage** (an outdated fact still appearing as current in the summary): **0% vs
    50%** for a **naive** summarizer (a simple one-step summarizer, used for comparison).
  - **Signature retention** (the exact function definition still present later): **90% vs 0%**.
  - The loss score follows real information loss with a **correlation of 0.91** (how closely two
    measurements move together; 1 = perfectly in step). That is why it can be trusted to trigger a
    switch.

### 3. Retrieval (RAG)

- **What:** search, reranking and the staleness check from Step 2c.
- **Results:**
  - Staleness flags: **precision 0.82** (when it flags something, it is right 82% of the time) and
    **recall 0.73** (it catches 73% of real contradictions).
  - The improved version **v4b** (this week's pre-tested upgrade) reaches **precision 1.00**, and
    **false supersession** (a still-current fact wrongly marked as outdated) falls from **23% to
    0%**. Recall is 0.69, slightly lower.
  - Better reading of search results (shorter labels, plus the reranker) raised **evidence hit**
    (the share of questions where the needed information reached the model) from **39% to 66%**.
  - It needs **no large AI model**. Competitors need one, or need facts already stored in a neat
    structured form.

### 4. The Controller (ASSE): the main contribution

- **What:** the choice from Step 3.
- **Results:**
  - On conversations that change type, it found the needed information **98.6%** of the time,
    against **87.4%** for the best single fixed method: **+11.2 points**.
    - The **confidence interval** (the range the true difference very likely lies in) is +9.3 to
      +12.9. The whole range is above zero, so the result is **statistically significant** (very
      unlikely to be luck).
  - It beats "always hybrid" by +6.0 points while sending less text.
  - On a benchmark where search is always right, it **ties** search: adapting costs nothing.
  - We also built a **machine-learned controller** (one that learns the choices from recorded
    examples, using logistic regression, random forest and gradient boosting: three standard
    learning methods). It scored lower (93% vs 99%), so we kept the readable rules.

---

## Part 7: How we tested it, and why the numbers can be trusted

**Benchmarks** (standard test sets many researchers use, so results can be compared):

- **LoCoMo**: about 600-message conversations with questions about earlier parts; our main test.
- **LoCoMo-Plus**: questions where the clue was only implied.
- **BEAM**: made by **other researchers**; we never adjusted anything for it, so it is an
  independent check.
- **Our own test sets** for each component, e.g. conversations that change type, and coding sessions
  with traps.

**Measures:**

- **Evidence hit**: did the needed information reach the model? This is objective.
- **Answer accuracy**: an AI model answers from the memory provided; another AI model, the
  **judge**, marks it correct, partly correct or wrong. We check a sample against human marking
  using **Cohen's kappa** (a standard score of how much two markers agree beyond chance).
- **F1 score**: how closely the answer's words match the correct answer (0 to 1).

**Fairness rules:**

- **Dev/test split** (we split every dataset in two, adjust the system only on the "dev" half, and
  report on the unseen "test" half; otherwise it is like grading a student on the exact questions
  they practised).
- **Frozen system** (settings locked before final testing), with each test run **once**.
- **Pre-registration** (writing down, before an experiment, exactly what will be tested and what
  counts as success, then reporting the result whatever it is; this stops anyone quietly keeping
  only the experiments that worked).
- **Gates** (pass/fail checks on the dev data that a new version must pass before it may touch the
  test data).
- **Baselines** (other systems compared under identical conditions: same questions, same memory
  space, same AI model, same judge).
- **Automated tests**: 89 small programs that check each part still works, run on every change by
  **CI** (Continuous Integration: GitHub runs them automatically on every upload).

## Part 8: Comparison with existing systems

**Mem0** is a popular memory product. We ran the real Mem0 software under the same conditions.

| | CEAI | Mem0 |
|---|---|---|
| Answer accuracy (judged) | 50.7% | 46.7% (difference not significant, so we call it equal) |
| Exact-answer match (F1) | **0.406** | 0.278 (significantly better for CEAI) |
| Large-AI calls needed to build memory, per conversation | **0** | about 54 |
| Time to build memory for one long conversation | **about 6 seconds** | about 16 minutes (162× slower) |
| Coding traps, original demo | **2 of 2 caught** | 0 of 2 |
| Coding traps, 12 new unseen sessions | **16 of 26** | 5 of 26 |

**Why Mem0 misses the traps:** it rewrites what it remembers into short notes. It remembers "a
helper called `format_due_date` was added", not the exact code needed to reuse it.

**Longer conversations:** CEAI stays at 96–100% at every length, while a simple window gets worse.
CEAI's lead over the window grows from **+28 points** for short conversations to **+42 points** for
long ones.

## Part 9: What does not work yet (say it openly)

- **On the independent BEAM benchmark, CEAI scored below "always search"** (34.6% vs 44.5%).
  - The cause is found: many BEAM questions are phrased as requests ("Could you show me how…").
    The classifier (Step 1) labels them casual chat, so the controller picks the summary, which
    lacks the details.
  - Fixing this is the first item of future work.
- **In the 12 unseen coding sessions, "always hybrid" caught 18 traps vs our 16.** The misses are
  mostly changed settings (e.g. a tax rate), and functions renamed to a completely new name, which
  the staleness check does not yet recognise.
- **Letting a small AI model write the summaries did not help.** So the default stays "no AI calls
  inside memory".

## Part 10: This week's improvements, and how our checks protected us

- We tested three upgrades, each on its own first:
  - better window weights;
  - a better staleness check;
  - better chunking.
- All three together (**v4**) failed a gate: the new window weights dropped messages even when
  everything fitted, and accuracy fell from 99% to 80%. It was **not** adopted.
- The version without the window change (**v4b**) passed every gate. On the dev data:
  - it nearly doubled the implied-clue score (0.134 → 0.264);
  - it raised the main benchmark from 0.709 to 0.785.
- Its final test runs are being completed. The official results remain those of the frozen system.

## Part 11: Why it matters (who would use it)

- **Cheaper:** no extra AI bill for memory.
- **Faster:** memory is built in seconds, not minutes.
- **Safer for coding assistants:** fewer duplicate or broken functions.
- **Private:** runs fully offline on a normal laptop; no conversation data leaves the machine.
- **Accountable:** every memory decision is written down and can be corrected.

**Users:** companies building coding assistants and chatbots; organisations with privacy rules
(health, finance, government); teams using small or local models.

**How it could be offered:**
- a free **open-source** library (code anyone can use and inspect);
- a drop-in version placed in front of any chat app (change one web address);
- a paid dashboard for teams.

## Part 12: The 30-second version

> "AI assistants have no memory of their own: for every message, software must choose what past
> conversation to send them. Today's memory products use one method for the whole conversation,
> but conversations change: chatting, debugging, recalling, coding. CEAI chooses the right method
> for every message, explains why, and lets a person override it. It needs no extra AI calls, so it
> builds memory 162 times faster than Mem0. When the conversation changes type, it finds the needed
> information 98.6% of the time vs 87.4% for the best fixed method, and it catches coding mistakes
> that Mem0 and simple memory miss. We tested it fairly, with locked settings, experiments written
> down in advance and an independent benchmark, and we show where it still falls short."

---

## Glossary

| Term | Meaning |
|---|---|
| AI judge | An AI model used to mark answers correct / partly correct / wrong |
| Anchor | A checkable detail (name, number, code identifier) used to measure summary loss |
| API | Application Programming Interface: the name and inputs used to call a piece of code |
| Append-only log | A record file where lines are only added, never changed |
| ASSE / Controller | Our component that chooses the memory method for each message (`controller/`) |
| AST | Abstract Syntax Tree: Python's structured view of code, used to compare function definitions exactly |
| Baseline | A simpler or existing system used for comparison |
| Benchmark | A standard test set used by many researchers |
| BEAM | An independent benchmark by other researchers |
| Candidate context | One method's proposal for what to send the model |
| Chunk / chunking | A stored piece of conversation / deciding how big each piece is |
| CI | Continuous Integration: tests run automatically on every code change |
| Cohen's kappa | A score of how much two markers agree beyond chance |
| Composite score | One combined score made from several parts |
| Confidence interval | The range the true difference very likely lies in |
| Context / context window | The text sent to the model / the most it can read at once |
| Contracts | Agreed message formats every component must use (`contracts/schemas.py`) |
| Correlation | How closely two measurements move together (1 = perfectly) |
| Cosine similarity | A 0–1 number comparing the meaning of two embeddings |
| Dashboard | A web page showing each decision live |
| Dev / test split | Tune on one half of the data, report on the unseen other half |
| Dwell time | Minimum turns before the controller may switch again |
| Embedding | Text turned into numbers that capture its meaning |
| Escalation | A warning from one component that changes the *next* decision |
| Evidence hit | Whether the needed information reached the model |
| Exchange | One user message plus the assistant's reply |
| F1 score | How closely an answer matches the correct one (0 to 1) |
| FAISS | A fast open-source library for searching by meaning |
| False supersession | A still-current fact wrongly marked as outdated |
| Feature vector | The short list of facts the controller decides from |
| Freshness / relevance / importance / state | The four parts of the window's score: recency, closeness in meaning, useful content, same topic |
| Frozen system | Settings locked before final testing |
| Function / signature | A named reusable piece of code / its name and inputs |
| Gate | A pass/fail check a new version must pass on dev data first |
| Half-life | How many turns until freshness halves |
| Hybrid | Recent messages plus searched older passages together |
| JSONL | A text file with one structured record per line |
| Leakage | Information from after a decision wrongly used in making it |
| LLM | Large Language Model, the AI that writes replies |
| LoCoMo / LoCoMo-Plus | Benchmarks of very long conversations (Plus: implied clues) |
| Loss score | Share of important details a summary dropped |
| Mem0 | A popular existing memory product we compared against |
| Middleware | Software sitting between two others |
| MiniLM | The small model that makes our embeddings |
| Naive summarizer | A simple one-step summarizer used for comparison |
| NLI | Natural Language Inference: a model that tells if one sentence contradicts another |
| Open-source | Code anyone can use and inspect |
| Override | A person replacing the system's choice |
| Parallel / thread | Doing several things at the same time inside one program |
| Precision | Of what was flagged, how much was right |
| Pre-registration | Writing the test and success rule down *before* running it |
| Prompt | The full text sent to the AI model |
| Pydantic | A library that checks messages have the agreed format |
| RAG | Retrieval-Augmented Generation: search stored conversation and send the best passages |
| Rationale | The plain-English reason recorded with each decision |
| Recall | Of everything that should have been found, how much was found |
| Recency-only | Choosing messages by time alone |
| Reranker | A second, more careful model that re-orders search results |
| Signal bus | The broadcast line that carries the TurnSignal to all components |
| Sliding window | Sending only the most recent messages |
| Stale / superseded | Out of date / replaced by newer information |
| Stale-fact leakage | An outdated fact still shown as current |
| Staleness check | Checking whether stored information has become out of date |
| Statistically significant | Very unlikely to be due to chance |
| Summarization tiers (L1 / L2 / L3) | Exact facts / intentions and decisions / user profile |
| tiktoken | A library that counts tokens the way AI models do |
| Token / token-budget pressure | A piece of a word / how full the memory space is (0 to 1) |
| Turn / TurnSignal | One message / the small standard message describing it |
| v4 / v4b | This week's upgraded versions: v4 failed our checks, v4b passed |
| Vector database | A store that finds text by meaning |
