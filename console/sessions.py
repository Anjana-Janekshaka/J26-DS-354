"""Saved chats and settings for the terminal app, kept in ``~/.ceai`` (or ``CEAI_HOME``).

A session stores only what the user typed, the replies and any per-message memory choice. The
memory itself is rebuilt by replaying those messages through the pipeline, which makes no AI calls
and gives the same decisions every time.
"""

from __future__ import annotations

import json
import os
import random
import string
import time
from pathlib import Path

DEFAULT_SETTINGS = {
    "skin": "syno", "indicator": "unicode", "verbose": "all", "focus": False, "timestamps": False, "footer": True,
    "bell": False, "statusbar": True, "reasoning": "hide", "personality": None,
}


def home() -> Path:
    p = Path(os.environ.get("CEAI_HOME") or Path.home() / ".ceai")
    (p / "sessions").mkdir(parents=True, exist_ok=True)
    return p


def new_id() -> str:
    return time.strftime("%Y%m%d_%H%M%S_") + "".join(random.choices(string.ascii_lowercase + string.digits, k=4))


def path_of(sid: str) -> Path:
    return home() / "sessions" / f"{sid}.json"


def save(session: dict) -> None:
    session["updated"] = time.time()
    tmp = path_of(session["id"]).with_suffix(".tmp")
    tmp.write_text(json.dumps(session, indent=1), encoding="utf-8")
    tmp.replace(path_of(session["id"]))


def all_sessions() -> list[dict]:
    out = []
    for f in (home() / "sessions").glob("*.json"):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return sorted(out, key=lambda s: s.get("updated", 0), reverse=True)


def find(key: str) -> dict | None:
    """By list number (1 = newest), id, id prefix or title (case-insensitive)."""
    sessions = all_sessions()
    key = key.strip()
    if key.isdigit() and 1 <= int(key) <= len(sessions):
        return sessions[int(key) - 1]
    for s in sessions:
        if s["id"] == key or (s.get("title") or "").lower() == key.lower():
            return s
    starts = [s for s in sessions if s["id"].startswith(key)]
    return starts[0] if len(starts) == 1 else None


def latest() -> dict | None:
    sessions = all_sessions()
    return sessions[0] if sessions else None


def delete(sid: str) -> None:
    path_of(sid).unlink(missing_ok=True)


def load_settings() -> dict:
    s = dict(DEFAULT_SETTINGS)
    try:
        s.update(json.loads((home() / "config.json").read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        pass
    return s


def save_settings(settings: dict) -> None:
    (home() / "config.json").write_text(json.dumps(settings, indent=1), encoding="utf-8")
