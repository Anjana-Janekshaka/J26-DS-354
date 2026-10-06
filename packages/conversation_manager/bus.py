"""In-process publish/subscribe bus for ``TurnSignal`` broadcasts."""

from __future__ import annotations

import threading
from typing import Callable

from contracts import TurnSignal

Subscriber = Callable[[TurnSignal], None]


class SignalBus:
    def __init__(self, keep_history: int = 10_000):
        self._subs: list[Subscriber] = []
        self._history: list[TurnSignal] = []
        self._keep = keep_history
        self._lock = threading.Lock()

    def subscribe(self, fn: Subscriber) -> Callable[[], None]:
        with self._lock:
            self._subs.append(fn)

        def unsubscribe() -> None:
            with self._lock:
                if fn in self._subs:
                    self._subs.remove(fn)

        return unsubscribe

    def publish(self, signal: TurnSignal) -> None:
        with self._lock:
            subs = list(self._subs)
            self._history.append(signal)
            if len(self._history) > self._keep:
                del self._history[: len(self._history) - self._keep]
        for fn in subs:
            fn(signal)

    @property
    def history(self) -> list[TurnSignal]:
        return list(self._history)
