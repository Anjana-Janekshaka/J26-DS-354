"""Deterministic rule-based tier generators.

L1 extraction is verbatim: exact code signatures (via ``ast``), keyed attribute statements,
rename statements, constraint / decision / request sentences, and informative statements. It
never paraphrases. L2 and L3 are rule-based reductions of the tier below; with an LLM backend
configured (``generators.LLMGenerator``) the three tier prompts in ``prompts.py`` are used instead.
"""

from __future__ import annotations

import re
from collections import Counter

from contracts import ConversationTurn
from contracts.text import code_signatures, identifiers, sentences, strip_code, unique

from .records import Fact, L1Record, L2Record, L3Record

_ATTRIBUTE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("user.name", re.compile(r"\bmy name is ([A-Z][\w'-]+(?: [A-Z][\w'-]+)?)")),
    ("user.location", re.compile(r"\bI (?:live|am living|moved|relocated|have moved|just moved) (?:in|to) ([A-Z][\w'-]+(?:[ ,]+[A-Z][\w'-]+)*)")),
    ("user.employer", re.compile(r"\bI work (?:at|for) ([A-Z][\w&'-]+(?: [A-Z][\w&'-]+)*)")),
    ("user.job", re.compile(r"\bI work as (?:a|an) ([a-z][\w -]{2,40}?)(?=[.,!?]|$)")),
    ("user.favorite", re.compile(r"\bmy fav(?:ou?rite)? (\w+) is ([\w' -]{2,40}?)(?=[.,!?]|$)")),
]
_SETTING = re.compile(
    r"\b(?:the )?`?([A-Za-z_][\w.]*(?: [a-z_]+)?)`? (?:is|was|has been) (?:now )?(?:set to|changed to|updated to|bumped to|moved to) `?([\w./:@-]+)`?",
    re.I,
)
_CHOICE = re.compile(
    r"\b(?:let'?s use|we'?ll use|we use|we'?re using|switch(?:ed|ing)? to|going with|go with|use) `?([A-Za-z][\w.+-]*)`? (?:for|as) (?:the |our )?([a-z][\w ]{2,30}?)(?=[.,!?]|$)",
    re.I,
)
_RENAME = re.compile(
    r"\brenam(?:e|ed|ing)\s+(?:the\s+)?(?:function\s+|method\s+|class\s+)?`?([A-Za-z_]\w*)`?\s*(?:\(\))?\s+(?:to|->|→|into)\s+`?([A-Za-z_]\w*)`?",
    re.I,
)
_PARAM_RENAME = re.compile(
    r"\brenam\w*\s+(?:the\s+)?(?:param(?:eter)?|arg(?:ument)?|field|column|key)\s+`?([A-Za-z_]\w*)`?\s+(?:to|->|→)\s+`?([A-Za-z_]\w*)`?(?:\s+(?:in|of|on)\s+`?([A-Za-z_]\w*)`?)?",
    re.I,
)
_CONSTRAINT = re.compile(
    r"\b(must|must not|never|always|don'?t|do not|required|should not|shouldn'?t|cannot|has to|have to|only use|no more than|at least|at most)\b",
    re.I,
)
_DECISION = re.compile(
    r"\b(we decided|decided to|let'?s (?:go with|use|keep|switch)|we'?ll (?:use|go with|keep)|agreed|going with|settled on|the plan is)\b",
    re.I,
)
_REQUEST = re.compile(
    r"^(?:can you|could you|please|i need|we need|let'?s|now|next,?|also,?|write|implement|add|create|build|fix|refactor|rename|update|make)\b",
    re.I,
)
# First-person self-disclosure: standing states, habits, goals and beliefs ("I've been so nervous
# about...", "so now I always...", "I'm saving for...", "I believe..."). These are the persona facts
# a conversational memory must keep even when they name no entity, so they outrank generic
# statements and feed the L2 open goals / L3 persona.
_USER_STATE = re.compile(
    r"\b(?:I(?:'ve| have)? been (?:feeling|trying|working|saving|learning|struggling|getting)|I(?:'m| am) (?:feeling|trying|saving|planning|working on|learning|determined|committed|worried|nervous|afraid|scared|excited|proud)|"
    r"I (?:\w+ly )?(?:feel|felt|believe|value|think that|want to|hope to|plan to|intend to|refuse|always|never|only|usually|no longer|stopped|started|switched|quit|decided|prefer|love|hate|can'?t stand)|"
    r"so now I|ever since|my (?:goal|dream|plan|priority|rule) is|is important to me|matters to me)\b",
    re.I,
)
_GOAL = re.compile(r"\b(?:want to|hope to|plan to|intend to|trying to|saving (?:for|to|up)|working (?:toward|towards|on)|my (?:goal|dream|plan) is|so I can)\b", re.I)
_MAX_USER_STATES_PER_TURN = 2

_PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]{2,}(?: [A-Z][a-z]{2,})*)\b")
_NUMBERISH = re.compile(r"\b\d[\d,.:/-]*\b")
_MAX_STATEMENTS_PER_TURN = 3


def _entities(text: str) -> list[str]:
    prose = strip_code(text)
    ents = [m for m in _PROPER.findall(prose) if m.lower() not in {"the", "this", "that", "and"}]
    ents += sorted(k.split(":", 1)[1] for k in code_signatures(text))
    ents += sorted(identifiers(prose))
    return unique(ents)


def _informativeness(sentence: str) -> float:
    return len(_PROPER.findall(sentence)) + len(identifiers(sentence)) + 0.5 * len(_NUMBERISH.findall(sentence)) + min(
        len(sentence.split()), 25
    ) / 25


def extract_facts(turn: ConversationTurn, fact_seq: list[int]) -> tuple[list[Fact], list[str]]:
    """Return (facts, constraint sentences) extracted verbatim from one turn."""

    def new(key: str, value: str, kind: str) -> Fact:
        fact_seq[0] += 1
        return Fact(fact_id=f"f{fact_seq[0]:05d}", key=key, value=value.strip(), kind=kind, source_turn_id=turn.turn_id)  # type: ignore[arg-type]

    facts: list[Fact] = []
    constraints: list[str] = []
    text = turn.content
    for key, sig in code_signatures(text).items():
        facts.append(new(key, sig, "code_signature"))

    prose = strip_code(text)
    for old, new_name, owner in _PARAM_RENAME.findall(prose):
        facts.append(new(f"param_rename:{owner or '?'}:{old}", f"{old} -> {new_name}", "rename"))
    for old, new_name in _RENAME.findall(prose):
        if not _PARAM_RENAME.search(prose) or old not in {m[0] for m in _PARAM_RENAME.findall(prose)}:
            facts.append(new(f"rename:{old}", new_name, "rename"))
    keyed_spans: list[str] = []
    for key, pat in _ATTRIBUTE_PATTERNS:
        for m in pat.finditer(prose):
            keyed_spans.append(m.group(0))
            if key == "user.favorite":
                facts.append(new(f"user.favorite.{m.group(1).lower()}", m.group(2), "attribute"))
            else:
                facts.append(new(key, m.group(1), "attribute"))
    for m in _SETTING.finditer(prose):
        keyed_spans.append(m.group(0))
        facts.append(new(f"setting:{m.group(1).lower().replace(' ', '_')}", m.group(2), "attribute"))
    for m in _CHOICE.finditer(prose):
        keyed_spans.append(m.group(0))
        facts.append(new(f"choice:{m.group(2).strip().lower().replace(' ', '_')}", m.group(1), "attribute"))

    statements: list[tuple[float, int, str]] = []
    n_states = 0
    for i, sent in enumerate(sentences(prose)):
        if len(sent.split()) < 4:
            continue
        if any(span in sent for span in keyed_spans) and not _CONSTRAINT.search(sent):
            continue  # already captured as a keyed (mergeable) fact; a free copy would go stale
        if turn.role == "user" and n_states < _MAX_USER_STATES_PER_TURN and not sent.endswith("?") and _USER_STATE.search(sent):
            facts.append(new(f"user_state:{turn.turn_id}:{i}", sent, "user_state"))
            n_states += 1
        elif _CONSTRAINT.search(sent):
            constraints.append(sent)
            facts.append(new(f"constraint:{turn.turn_id}:{i}", sent, "constraint"))
        elif _DECISION.search(sent):
            facts.append(new(f"decision:{turn.turn_id}:{i}", sent, "decision"))
        elif turn.role == "user" and (_REQUEST.search(sent) or sent.endswith("?")):
            facts.append(new(f"request:{turn.turn_id}:{i}", sent, "request"))
        elif not sent.endswith("?"):
            statements.append((_informativeness(sent), i, sent))
    for _, i, sent in sorted(statements, reverse=True)[:_MAX_STATEMENTS_PER_TURN]:
        facts.append(new(f"stmt:{turn.turn_id}:{i}", sent, "statement"))
    return facts, constraints


def rule_l1(record_id: str, turns: list[ConversationTurn], fact_seq: list[int]) -> L1Record:
    facts: list[Fact] = []
    constraints: list[str] = []
    entities: list[str] = []
    for t in turns:
        f, c = extract_facts(t, fact_seq)
        speaker = t.speaker or t.role
        for fact in f:
            if fact.kind in ("statement", "request", "decision", "constraint", "user_state") and t.speaker:
                fact.value = f"{speaker}: {fact.value}"
            if fact.kind in ("statement", "user_state") and t.metadata.get("date"):
                fact.value = f"[{t.metadata['date']}] {fact.value}"
        facts += f
        constraints += c
        entities += _entities(t.content)
    return L1Record(
        record_id=record_id,
        facts=facts,
        entities=unique(entities)[:40],
        constraints=constraints,
        turn_range=(turns[0].turn_id, turns[-1].turn_id),
    )


def rule_l2(record_id: str, l1s: list[L1Record]) -> L2Record:
    ents = Counter(e for r in l1s for e in r.entities)
    has_code = any(f.kind == "code_signature" for r in l1s for f in r.facts)
    focus = ", ".join(e for e, _ in ents.most_common(5)) or "general discussion"
    intent = f"{'Coding work' if has_code else 'Conversation'} focused on {focus}"
    decisions: list[str] = []
    for r in l1s:
        for f in r.facts:
            if f.kind == "decision":
                decisions.append(f.value)
            elif f.kind == "rename":
                decisions.append(f"renamed {f.key.split(':')[-1]} -> {f.value.split('->')[-1].strip()}")
            elif f.kind == "attribute" and f.key.startswith(("choice:", "setting:")):
                decisions.append(f"{f.key.split(':', 1)[1].replace('_', ' ')}: {f.value}")
    open_goals = [f.value for r in l1s for f in r.facts if f.kind == "request" or (f.kind == "user_state" and _GOAL.search(f.value))][-4:]
    return L2Record(
        record_id=record_id,
        intent=intent,
        decisions=unique(decisions)[-8:],
        open_goals=open_goals,
        source_l1_ids=[r.record_id for r in l1s],
    )


def rule_l3(record_id: str, l2s: list[L2Record], attributes: dict[str, str]) -> L3Record:
    persona_bits = [f"{k.split('.', 1)[1].replace('.', ' ')}: {v}" for k, v in attributes.items() if k.startswith("user.")]
    persona_bits += [v for k, v in attributes.items() if k.startswith("user_state:")][-4:]
    coding = sum(1 for r in l2s if r.intent.startswith("Coding"))
    domain = "a developer in an ongoing coding session" if coding >= len(l2s) / 2 else "a person in an ongoing conversation"
    persona = domain + (f" ({'; '.join(persona_bits)})" if persona_bits else "")
    focus = Counter()
    for r in l2s:
        for part in r.intent.split("focused on", 1)[-1].split(","):
            if part.strip():
                focus[part.strip()] += 1
    objective = "Progress on " + ", ".join(e for e, _ in focus.most_common(4)) if focus else "Unclear"
    last = l2s[-1]
    state_bits = (last.decisions[-3:] or []) + ([f"open: {g}" for g in last.open_goals[-2:]] if last.open_goals else [])
    final_state = "; ".join(state_bits) if state_bits else last.intent
    return L3Record(
        record_id=record_id,
        persona=persona,
        main_objective=objective,
        final_state=final_state,
        source_l2_ids=[r.record_id for r in l2s],
    )
