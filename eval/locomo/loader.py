"""Loader for the original LoCoMo release (Maharana et al., arXiv 2402.17753; data/locomo10.json)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

DATA = Path(__file__).parent / "data" / "locomo10.json"
DATA_URL = "https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json"
CATEGORY_NAMES = {1: "multi_hop", 2: "temporal", 3: "open_domain", 4: "single_hop", 5: "adversarial"}


@dataclass
class LocomoTurn:
    dia_id: str
    speaker: str
    text: str
    session: int
    date: str


@dataclass
class LocomoQA:
    question: str
    answer: str | None
    evidence: list[str]
    category: int


@dataclass
class LocomoConversation:
    sample_id: str
    speakers: tuple[str, str]
    turns: list[LocomoTurn] = field(default_factory=list)
    qa: list[LocomoQA] = field(default_factory=list)


def _date(raw: str) -> str:
    # "1:56 pm on 8 May, 2023" -> "8 May 2023"
    m = re.search(r"on (\d{1,2} \w+),? (\d{4})", raw or "")
    return f"{m.group(1)} {m.group(2)}" if m else (raw or "")


def load(path: Path = DATA) -> list[LocomoConversation]:
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - download it with:\n  curl -L -o {path} {DATA_URL}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    convs = []
    for sample in raw:
        c = sample["conversation"]
        conv = LocomoConversation(sample["sample_id"], (c["speaker_a"], c["speaker_b"]))
        sessions = sorted(int(k.split("_")[1]) for k in c if re.fullmatch(r"session_\d+", k))
        for s in sessions:
            date = _date(c.get(f"session_{s}_date_time", ""))
            for t in c[f"session_{s}"]:
                text = t["text"]
                if t.get("blip_caption"):
                    text += f" [shares a photo: {t['blip_caption']}]"
                conv.turns.append(LocomoTurn(t["dia_id"], t["speaker"], text, s, date))
        for q in sample["qa"]:
            ev = []
            for e in q.get("evidence", []):
                ev += [x.strip() for x in re.split(r"[;,]", e) if x.strip()]
            conv.qa.append(LocomoQA(q["question"], q.get("answer"), ev, int(q["category"])))
        convs.append(conv)
    return convs
