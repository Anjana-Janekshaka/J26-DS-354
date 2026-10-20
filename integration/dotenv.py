"""Read settings such as the AI key from a local ``.env`` file (no extra dependency).

``.env`` sits in the repo root, is git-ignored and holds ``NAME=value`` lines; copy
``.env.example`` to start. Values already set in the environment win, so a terminal
``$env:NAME = ...`` still overrides the file.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: str | Path | None = None) -> list[str]:
    """Set each ``NAME=value`` from the file unless NAME is already set. Returns the names it set."""
    p = Path(path) if path else ROOT / ".env"
    if not p.is_file():
        return []
    loaded = []
    for raw in p.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.removeprefix("export ").split("=", 1)
        name, value = name.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if name and value and name not in os.environ:
            os.environ[name] = value
            loaded.append(name)
    return loaded
