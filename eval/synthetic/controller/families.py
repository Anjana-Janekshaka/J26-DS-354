"""Phrasing families for the controller's strategy-switch conversations.

Why families exist: the rule-based controller was written while looking at family A's wording, so
testing it on family A is circular. Every family shares the same conversation *structure* and the
same objective evidence requirements (job, fix text, function signatures, city), but the user's
wording differs:

  A - canonical wording (the original generator's sentences, which the rules were written against)
  B - paraphrases used for training / validation (rule tuning, model training)
  C - held-out paraphrases, used for the test split ONLY. Nobody tunes rules or models on these.

Each slot maps to a list of templates; one is picked per conversation with the seeded RNG.
Templates use ``str.format`` fields: city, rel, job, hobby, Hobby, one, many, err, err_head, fix,
second_fix, p_old, p_new. Any template that carries evidence (``{job}``, ``{fix}``, ``{second_fix}``,
``{city}``) must keep that field verbatim so the evidence check still works.

Integrity note for the write-up: family C was written as natural user phrasing, without running
the classifier or rules against it. Ideally a teammate who has not read ``rules.py`` writes or
reviews it; record who did in the dissertation.
"""

from __future__ import annotations

FAMILIES: dict[str, dict[str, list[str]]] = {
    "A": {
        "intro": ["Before we start: I'm working from {city} this month, and my {rel} is a {job}."],
        "intro_reply": ["Nice, thanks for the context."],
        "hobby": ["On weekends I've been getting into {hobby}."],
        "hobby_reply": ["{Hobby} sounds like a great way to unwind."],
        "early_recall": ["What does my {rel} do for work?"],
        "code_req": ["Write a function to load {many} for a customer and one to format a {one} total as currency."],
        "explain": ["Explain how load_{many} handles closed {many}."],
        "explain_reply": ["It filters on status, so closed {many} are excluded unless you pass status='closed'."],
        "crash": ["The {one} report crashes with {err} when I run it."],
        "fix_reply": ["That happens in build_report(): {fix}."],
        "applied": ["Okay, applied it. Re-running the report now."],
        "applied_reply": ["Let me know what the output looks like."],
        "debug_followup": ["It crashed again with {err_head} - what fix did you suggest?"],
        "off": ["Hmm, the numbers in the output look off now."],
        "off_reply": ["Then {second_fix}."],
        "implicit_followup": ["Still wrong after that. What should I try next?"],
        "rename": ["Rename the parameter {p_old} to {p_new} in load_{many}; the new auth layer only gives us {p_new}."],
        "duplicate_build": ["Write a helper that formats a {one} total as a currency string for the PDF export."],
        "renamed_call": ["Now call load_{many} from the nightly sync job for every customer."],
        "late_recall": ["Which city did I say I'm working from this month?"],
    },
    "B": {
        "intro": [
            "Quick context: this month I'm based in {city}. Also, my {rel} works as a {job}.",
            "FYI I'm spending this month in {city}; my {rel} is a {job}, if that ever matters.",
        ],
        "intro_reply": ["Got it, noted.", "Thanks, good to know."],
        "hobby": ["Lately my weekends go to {hobby}.", "Outside work I've picked up {hobby} recently."],
        "hobby_reply": ["{Hobby} is a fun one.", "Nice, {hobby} is a good break from screens."],
        "early_recall": ["Can you tell me my {rel}'s profession?", "My {rel} - what's their line of work again?"],
        "code_req": [
            "I need code that loads a customer's {many}, plus something that turns a {one} total into a currency string.",
            "Please give me a loader for {many} by customer and a formatter for {one} totals in currency.",
        ],
        "explain": ["What does load_{many} do with {many} that are closed?", "Do closed {many} come back from load_{many}?"],
        "explain_reply": ["Only open ones by default; pass status='closed' to get the closed {many}."],
        "crash": ["Running the {one} report gives me {err}.", "I get {err} from the {one} report now."],
        "fix_reply": ["The problem is in build_report(): {fix}.", "Look at build_report(): {fix}."],
        "applied": ["Done, running it again.", "Changed it, trying once more."],
        "applied_reply": ["Okay, tell me what you see."],
        "debug_followup": ["{err_head} is back - what did you tell me to change?", "Seeing {err_head} again. What was your suggested fix?"],
        "off": ["Now the totals in the output don't add up.", "The figures in the report seem wrong now."],
        "off_reply": ["In that case, {second_fix}.", "Then you should {second_fix}."],
        "implicit_followup": ["Still not right. Next step?", "No luck. What else should I try?"],
        "rename": [
            "Change load_{many} so it takes {p_new} instead of {p_old} - auth only hands us {p_new} now.",
            "The auth layer now gives {p_new}, so swap {p_old} for {p_new} in load_{many}.",
        ],
        "duplicate_build": [
            "I need a function that shows a {one} total as currency in the PDF export.",
            "Can you write something to print {one} totals as money for the PDF export?",
        ],
        "renamed_call": [
            "Hook load_{many} into the nightly sync job so it runs for each customer.",
            "Use load_{many} in the nightly sync for all customers.",
        ],
        "late_recall": ["What city am I in this month?", "Where did I say I'm working this month?"],
    },
    "C": {
        "intro": [
            "Some background: for the next few weeks I'm in {city}, and my {rel} is a {job}.",
            "Context for later - I'm living in {city} this month, and my {rel} happens to be a {job}.",
            "Heads up, I'm in {city} for the month. Random fact: my {rel} is a {job}.",
        ],
        "intro_reply": ["Thanks for sharing.", "Noted, appreciated.", "Sounds good."],
        "hobby": ["My free time lately goes into {hobby}.", "I've started doing {hobby} on Saturdays.", "{Hobby} has become my weekend thing."],
        "hobby_reply": ["That's a great hobby.", "{Hobby}, nice choice.", "Sounds relaxing."],
        "early_recall": [
            "Quick check: my {rel}'s job - can you say it back to me?",
            "Hang on, my {rel} works as what?",
            "Tell me again what my {rel} does.",
        ],
        "code_req": [
            "Let's start the code: a loader that fetches {many} per customer, and a formatter that prints a {one} total as money.",
            "First task: fetch a customer's {many}, and show any {one} total in currency format.",
            "I want two pieces of code - one that pulls {many} for a customer, one that renders a {one} total as currency.",
        ],
        "explain": [
            "If a {one} is closed, does load_{many} still return it?",
            "Talk me through closed {many} in load_{many}.",
            "Closed {many} - included or not in load_{many}?",
        ],
        "explain_reply": ["Not by default; closed {many} only come back when status='closed' is passed."],
        "crash": [
            "The {one} report just died: {err}.",
            "Running the {one} report blows up with {err}.",
            "{err} - that's what the {one} report prints now.",
        ],
        "fix_reply": ["It's in build_report(): {fix}.", "Change build_report(): {fix}.", "Root cause is build_report(); {fix}."],
        "applied": ["Applied your change, running again.", "Patched it, rerunning.", "Edited build_report, trying again."],
        "applied_reply": ["Okay, share what happens.", "Let me know the result."],
        "debug_followup": [
            "Same {err_head} showed up again. Which change did you tell me to make?",
            "Ugh, {err_head} again. Go back to your earlier suggestion - what was it exactly?",
            "{err_head} once more. Repeat the fix you gave me?",
        ],
        "off": ["Hmm, the totals in the report look strange now.", "Now the output numbers are suspicious.", "The report runs but the sums look odd."],
        "off_reply": ["Then {second_fix}.", "Next, {second_fix}.", "Try this: {second_fix}."],
        "implicit_followup": ["Nope, still not right. Next idea?", "That didn't sort it either. Anything else?", "Same problem. Now what?"],
        "rename": [
            "Auth now only gives us {p_new}, so load_{many} should take {p_new} rather than {p_old}.",
            "Swap the {p_old} argument of load_{many} for {p_new}; that's all the auth layer exposes now.",
            "load_{many} needs {p_new} in place of {p_old} from now on.",
        ],
        "duplicate_build": [
            "For the PDF export I need the {one} total shown as money, like 1,234.50 EUR. Can you sort that out?",
            "The PDF export should print each {one} total in currency format - give me something for that.",
            "PDF export: {one} totals have to appear as currency. What code do I need?",
        ],
        "renamed_call": [
            "The nightly sync job has to pull {many} for every customer - hook it up to load_{many}.",
            "Next: have the nightly sync job use load_{many} so each customer's {many} get loaded.",
            "Wire load_{many} into the nightly sync, once per customer.",
        ],
        "late_recall": [
            "Where am I working from this month, again?",
            "Remind me which city I mentioned I'm in right now?",
            "This month I'm based in which city?",
        ],
    },
}

SLOTS = tuple(FAMILIES["A"])
assert all(set(f) == set(SLOTS) for f in FAMILIES.values()), "every family must define every slot"
