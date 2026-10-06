"""Tier generators: deterministic rule-based (default) and LLM-backed (three tier prompts).

The LLM generator takes any ``llm(system, user) -> str`` callable, so the package does not depend
on a provider SDK. Its output is validated against the tier schema; on invalid output it falls back
to the rule-based generator for that record and marks ``generator='rule_based_fallback'``.
For L1, exact code signatures are always re-derived with ``ast`` and override the model's copy,
so symbol retention never depends on the model transcribing a signature correctly.
"""

from __future__ import annotations

import json
import re
from typing import Callable, Protocol

from contracts import ConversationTurn
from contracts.text import code_signatures

from . import prompts
from .extract import rule_l1, rule_l2, rule_l3
from .records import Fact, L1Record, L2Record, L3Record

LLMCallable = Callable[[str, str], str]


class TierGenerator(Protocol):
    name: str

    def l1(self, record_id: str, turns: list[ConversationTurn], fact_seq: list[int]) -> L1Record: ...

    def l2(self, record_id: str, l1s: list[L1Record]) -> L2Record: ...

    def l3(self, record_id: str, l2s: list[L2Record], attributes: dict[str, str]) -> L3Record: ...


class RuleBasedGenerator:
    name = "rule_based"

    def l1(self, record_id, turns, fact_seq):
        return rule_l1(record_id, turns, fact_seq)

    def l2(self, record_id, l1s):
        return rule_l2(record_id, l1s)

    def l3(self, record_id, l2s, attributes):
        return rule_l3(record_id, l2s, attributes)


_JSON_OBJ = re.compile(r"\{.*\}", re.S)


def _parse_json(text: str) -> dict:
    m = _JSON_OBJ.search(text)
    if not m:
        raise ValueError("no JSON object in model output")
    return json.loads(m.group(0))


class LLMGenerator:
    name = "llm"

    def __init__(self, llm: LLMCallable):
        self.llm = llm
        self.fallback = RuleBasedGenerator()
        self.failures = 0

    def l1(self, record_id, turns, fact_seq):
        excerpt = "\n".join(f"[{t.turn_id}] {t.render()}" for t in turns)
        try:
            data = _parse_json(self.llm(prompts.L1_SYSTEM, prompts.L1_USER.format(turns=excerpt)))
            facts: list[Fact] = []
            for raw in data.get("facts", []):
                fact_seq[0] += 1
                facts.append(Fact(fact_id=f"f{fact_seq[0]:05d}", **{k: raw[k] for k in ("key", "value", "kind", "source_turn_id")}))
            # Exact signatures from the parser override whatever the model transcribed.
            facts = [f for f in facts if f.kind != "code_signature"]
            for t in turns:
                for key, sig in code_signatures(t.content).items():
                    fact_seq[0] += 1
                    facts.append(Fact(fact_id=f"f{fact_seq[0]:05d}", key=key, value=sig, kind="code_signature", source_turn_id=t.turn_id))
            return L1Record(
                record_id=record_id,
                facts=facts,
                entities=[str(e) for e in data.get("entities", [])],
                constraints=[str(c) for c in data.get("constraints", [])],
                turn_range=(turns[0].turn_id, turns[-1].turn_id),
                generator=self.name,
            )
        except Exception:
            self.failures += 1
            rec = self.fallback.l1(record_id, turns, fact_seq)
            rec.generator = "rule_based_fallback"
            return rec

    def l2(self, record_id, l1s):
        payload = json.dumps([r.model_dump(mode="json", exclude={"generator"}) for r in l1s], indent=1)
        try:
            data = _parse_json(self.llm(prompts.L2_SYSTEM, prompts.L2_USER.format(l1_json=payload)))
            return L2Record(
                record_id=record_id,
                intent=str(data["intent"]),
                decisions=[str(d) for d in data.get("decisions", [])],
                open_goals=[str(g) for g in data.get("open_goals", [])],
                source_l1_ids=[r.record_id for r in l1s],
                generator=self.name,
            )
        except Exception:
            self.failures += 1
            rec = self.fallback.l2(record_id, l1s)
            rec.generator = "rule_based_fallback"
            return rec

    def l3(self, record_id, l2s, attributes):
        payload = json.dumps([r.model_dump(mode="json", exclude={"generator"}) for r in l2s], indent=1)
        try:
            data = _parse_json(self.llm(prompts.L3_SYSTEM, prompts.L3_USER.format(l2_json=payload)))
            return L3Record(
                record_id=record_id,
                persona=str(data["persona"]),
                main_objective=str(data["main_objective"]),
                final_state=str(data["final_state"]),
                source_l2_ids=[r.record_id for r in l2s],
                generator=self.name,
            )
        except Exception:
            self.failures += 1
            rec = self.fallback.l3(record_id, l2s, attributes)
            rec.generator = "rule_based_fallback"
            return rec
