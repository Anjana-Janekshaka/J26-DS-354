"""Loader for LoCoMo-Plus (Li et al., arXiv 2602.10715; https://github.com/xjtuleeyf/Locomo-Plus).

Each item has a cue dialogue (an implicit constraint), a later trigger query and a time gap. As in
the reference ``build_conv.py`` / ``unified_input.py``: item i is stitched into LoCoMo conversation
``i % 10``; the trigger is placed 7 days after the last session, the cue ``time_gap`` before the
trigger, and all events are ordered by time. Re-implemented here (no code copied) so the harness
needs no network access; the pairing and placement rules follow the reference scripts.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).parent
PLUS = HERE / "data" / "locomo_plus.json"
LOCOMO = HERE.parent / "locomo" / "data" / "locomo10.json"
PLUS_URL = "https://raw.githubusercontent.com/xjtuleeyf/Locomo-Plus/main/data/locomo_plus.json"

_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "a": 1, "an": 1}


def gap_days(time_gap: str) -> int:
    m = re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a|an)\b\s*(week|month|year)s?\b", time_gap.lower())
    if not m:
        return 0
    n = int(m.group(1)) if m.group(1).isdigit() else _NUM[m.group(1)]
    return n * {"week": 7, "month": 30, "year": 365}[m.group(2)]


def _ab(text: str, a: str, b: str) -> list[tuple[str, str]]:
    out = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("A:"):
            out.append((a, line[2:].strip()))
        elif line.startswith("B:"):
            out.append((b, line[2:].strip()))
    return out


@dataclass
class PlusTurn:
    speaker: str
    text: str
    date: str
    kind: str  # "conversation" | "cue" | "trigger"


@dataclass
class PlusItem:
    item_id: int
    relation_type: str
    time_gap: str
    base_conversation: str
    turns: list[PlusTurn]  # cue included, trigger excluded
    trigger: PlusTurn
    cue_texts: list[str]


def _fmt(d: datetime) -> str:
    return f"{d.day} {d.strftime('%B %Y')}"


def load(limit: int | None = None) -> list[PlusItem]:
    if not PLUS.exists():
        raise FileNotFoundError(f"{PLUS} missing - download it with:\n  curl -L -o {PLUS} {PLUS_URL}")
    plus = json.loads(PLUS.read_text(encoding="utf-8"))
    base = json.loads(LOCOMO.read_text(encoding="utf-8"))
    items = []
    for i, p in enumerate(plus[:limit] if limit else plus):
        sample = base[i % len(base)]
        conv = sample["conversation"]
        a, b = conv["speaker_a"], conv["speaker_b"]
        events: list[tuple[datetime, int, list[PlusTurn]]] = []
        k = 1
        last = None
        while f"session_{k}" in conv:
            t = datetime.strptime(conv[f"session_{k}_date_time"], "%I:%M %p on %d %B, %Y")
            last = t
            sess = []
            for turn in conv[f"session_{k}"]:
                text = turn["text"] + (f" [shares a photo: {turn['blip_caption']}]" if turn.get("blip_caption") else "")
                sess.append(PlusTurn(turn["speaker"], text, _fmt(t), "conversation"))
            events.append((t, 0, sess))
            k += 1
        query_time = last + timedelta(days=7)
        cue_time = query_time - timedelta(days=gap_days(p["time_gap"]))
        cue = [PlusTurn(s, x, _fmt(cue_time), "cue") for s, x in _ab(p["cue_dialogue"], a, b)]
        events.append((cue_time, 1, cue))
        events.sort(key=lambda e: (e[0], e[1]))
        turns = [t for _, _, ts in events for t in ts]
        trig = _ab(p["trigger_query"], a, b)[0]
        items.append(
            PlusItem(
                item_id=i,
                relation_type=p["relation_type"],
                time_gap=p["time_gap"],
                base_conversation=sample["sample_id"],
                turns=turns,
                trigger=PlusTurn(trig[0], trig[1], _fmt(query_time), "trigger"),
                cue_texts=[t.text for t in cue],
            )
        )
    return items
