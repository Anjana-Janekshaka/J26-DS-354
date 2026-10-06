import warnings
from datetime import datetime, timezone

import pytest

from contracts import ConversationTurn, TokenUsage, TurnSignal
from contracts.text import HashingEmbedder

warnings.filterwarnings("ignore")


class KeywordNLI:
    """Deterministic NLI stand-in: contradiction iff both sentences mention a city and the cities differ."""

    CITIES = {"london", "paris", "berlin", "tokyo"}

    def __init__(self):
        self.calls = 0

    def contradiction_prob(self, pairs):
        self.calls += len(pairs)
        out = []
        for a, b in pairs:
            ca = {w.strip(".,").lower() for w in a.split()} & self.CITIES
            cb = {w.strip(".,").lower() for w in b.split()} & self.CITIES
            out.append(0.99 if ca and cb and ca != cb else 0.01)
        return out


@pytest.fixture
def embedder():
    return HashingEmbedder()


@pytest.fixture
def nli():
    return KeywordNLI()


def make_signal(turn_id="t0100", budget=500, used=100, task_type="chat", state="task-1", turn_count=10):
    return TurnSignal(
        turn_id=turn_id,
        conversation_id="test",
        turn_count=turn_count,
        task_type=task_type,
        token_usage=TokenUsage(used=used, budget=budget),
        conversation_state=state,
        timestamp=datetime(2026, 10, 6, tzinfo=timezone.utc),
    )


def turns_from(msgs):
    return [ConversationTurn(turn_id=f"t{i + 1:04d}", role=r, content=c) for i, (r, c) in enumerate(msgs)]


CODE_SESSION = [
    ("user", "Write a helper to fetch a user's tasks."),
    ("assistant", "```python\ndef get_user_tasks(user_id):\n    return db.query(user_id)\n```"),
    ("user", "I live in London. We must never log raw tokens."),
    ("assistant", "Noted."),
    ("user", "Rename the param user_id to uid in get_user_tasks."),
    ("assistant", "```python\ndef get_user_tasks(uid):\n    return db.query(uid)\n```"),
    ("user", "Actually I moved to Paris last month."),
    ("assistant", "Got it."),
    ("user", "ok"),
    ("assistant", "sure"),
]
