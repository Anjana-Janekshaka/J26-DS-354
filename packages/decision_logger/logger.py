"""Append-only JSONL storage for decision records, escalation events and override requests.

* One JSON object per line, validated against the contract model on write *and* on read.
* Files are only ever opened in append mode; each write is flushed and fsync'd so a crash never
  leaves a half-written record behind a valid one.
* ``DecisionLogger`` writes ``decisions.jsonl`` (section 4.5, exact shape) and, alongside it,
  ``escalations.jsonl`` (joined on ``source_turn_id``).
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Generic, Iterator, TypeVar

from pydantic import BaseModel, ValidationError

from contracts import DecisionLogRecord, EscalationEvent, OverrideRequest

M = TypeVar("M", bound=BaseModel)


class CorruptLogError(ValueError):
    pass


class JsonlStore(Generic[M]):
    def __init__(self, path: str | Path, model: type[M]):
        self.path = Path(path)
        self.model = model
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def append(self, item: M) -> None:
        if not isinstance(item, self.model):
            raise TypeError(f"expected {self.model.__name__}, got {type(item).__name__}")
        line = item.model_dump_json() + "\n"
        with self._lock, open(self.path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

    def read(self, start_line: int = 0, strict: bool = True) -> Iterator[M]:
        if not self.path.exists():
            return
        with open(self.path, encoding="utf-8") as f:
            for n, line in enumerate(f):
                if n < start_line or not line.strip():
                    continue
                try:
                    yield self.model.model_validate_json(line)
                except (ValidationError, json.JSONDecodeError) as e:
                    if strict:
                        raise CorruptLogError(f"{self.path}:{n + 1}: {e}") from e

    def count(self) -> int:
        if not self.path.exists():
            return 0
        with open(self.path, encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())


class DecisionLogger:
    def __init__(self, log_dir: str | Path):
        self.dir = Path(log_dir)
        self.decisions = JsonlStore(self.dir / "decisions.jsonl", DecisionLogRecord)
        self.escalations = JsonlStore(self.dir / "escalations.jsonl", EscalationEvent)

    def log(self, record: DecisionLogRecord) -> None:
        self.decisions.append(record)

    def log_escalation(self, event: EscalationEvent) -> None:
        self.escalations.append(event)

    def records(self) -> list[DecisionLogRecord]:
        return list(self.decisions.read())

    def escalation_events(self) -> list[EscalationEvent]:
        return list(self.escalations.read())


class OverrideInbox:
    """Queue of human overrides (written by the dashboard, consumed by the turn loop)."""

    def __init__(self, path: str | Path):
        self.store = JsonlStore(path, OverrideRequest)
        self._consumed = self.store.count()

    def submit(self, request: OverrideRequest) -> None:
        self.store.append(request)

    def poll(self) -> list[OverrideRequest]:
        new = list(self.store.read(start_line=self._consumed, strict=False))
        self._consumed = self.store.count()
        return new
