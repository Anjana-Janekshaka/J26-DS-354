"""Contradiction-resolving merge of L1 facts into the current summary state.

Before a new fact is written, it is diffed against the active state by key (``func:<name>``,
``user.location`` ...). On conflict the old fact is marked superseded with a timestamp instead of
both sitting in the summary. Rename facts (``rename:<old>``) supersede the old symbol's facts.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from contracts import utcnow
from contracts.text import normalize

from .records import Fact

_UNIQUE_KINDS = {"statement", "constraint", "decision", "request"}


@dataclass
class MergeEvent:
    key: str
    old: Fact
    new: Fact


@dataclass
class SummaryState:
    active: dict[str, Fact] = field(default_factory=dict)
    superseded: list[Fact] = field(default_factory=list)
    events: list[MergeEvent] = field(default_factory=list)

    def _supersede(self, key: str, new: Fact) -> None:
        old = self.active.pop(key, None)
        if old is None:
            return
        old.superseded_by = new.fact_id
        old.superseded_at = utcnow()
        self.superseded.append(old)
        self.events.append(MergeEvent(key=key, old=old, new=new))

    def apply(self, fact: Fact) -> None:
        if fact.kind == "rename":
            if fact.key.startswith("rename:"):
                old_name = fact.key.split(":", 1)[1]
                for prefix in ("func:", "class:"):
                    if prefix + old_name in self.active:
                        self._supersede(prefix + old_name, fact)
            self.active[fact.key] = fact
            return
        current = self.active.get(fact.key)
        if current is not None and fact.kind not in _UNIQUE_KINDS:
            if normalize(current.value) == normalize(fact.value):
                return  # restatement, keep the original provenance
            self._supersede(fact.key, fact)
        self.active[fact.key] = fact

    def superseded_for(self, key: str) -> list[Fact]:
        return [f for f in self.superseded if f.key == key]

    def attributes(self) -> dict[str, str]:
        return {k: f.value for k, f in self.active.items() if f.kind == "attribute"}
