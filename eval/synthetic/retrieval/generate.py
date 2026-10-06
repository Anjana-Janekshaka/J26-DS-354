"""Synthetic contradiction-pairs set for the RAG staleness checker (deterministic, seeded).

Each item: {id, category, older, newer, label}, label 1 = the newer statement supersedes /
contradicts the older one, 0 = compatible. Negatives are deliberately *hard*: same topic, same
entities, different-but-compatible facts (another event, an added detail, a different service's
port, a paraphrase), plus a few unrelated pairs.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

CITIES = ["London", "Paris", "Berlin", "Tokyo", "Toronto", "Madrid", "Nairobi", "Seoul", "Lisbon", "Sydney"]
COMPANIES = ["Acme", "Globex", "Initech", "Umbrella", "Hooli", "Stark Labs", "Wayne Corp", "Pied Piper"]
ROLES = ["backend engineer", "data analyst", "product manager", "nurse", "teacher", "designer", "accountant"]
DBS = ["PostgreSQL", "MySQL", "MongoDB", "SQLite", "DynamoDB", "Cassandra"]
CACHES = ["Redis", "Memcached", "Varnish"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
THINGS = [("color", ["blue", "green", "red", "purple"]), ("food", ["sushi", "pizza", "tacos", "ramen"]), ("sport", ["tennis", "soccer", "basketball", "golf"])]
NAMES = ["Sam", "Priya", "Leo", "Mina", "Omar", "Ana", "Kofi", "Yuki"]
FUNCS = ["get_user_tasks", "create_invoice", "send_digest", "parse_rows", "load_config", "fetch_orders"]
PARAMS = ["user_id", "uid", "account", "path", "limit", "since", "due", "due_date", "payload", "timeout"]
PETS = ["dog", "cat", "parrot", "rabbit"]
ACTIVITIES = ["went hiking with my dog", "went swimming with friends", "visited a museum", "baked bread", "went to a concert", "played chess"]


def _two(rng, xs):
    a, b = rng.sample(xs, 2)
    return a, b


def positives(rng: random.Random):
    c1, c2 = _two(rng, CITIES)
    co1, co2 = _two(rng, COMPANIES)
    r1, r2 = _two(rng, ROLES)
    d1, d2 = _two(rng, DBS)
    k1, k2 = _two(rng, CACHES)
    day1, day2 = _two(rng, DAYS)
    thing, opts = rng.choice(THINGS)
    x1, x2 = _two(rng, opts)
    p1, p2 = rng.sample(range(3000, 9900, 100), 2)
    n1, n2 = rng.sample(range(1, 5), 2)
    f = rng.choice(FUNCS)
    a, b = _two(rng, PARAMS)
    name = rng.choice(NAMES)
    return [
        ("location", f"I live in {c1}.", f"I moved to {c2} last month."),
        ("location", f"I'm based in {c1} these days.", f"These days I'm living in {c2}, not {c1}."),
        ("job", f"I work at {co1} as a {r1}.", f"I left {co1} and joined {co2}."),
        ("job", f"My job is {r1}.", f"I switched careers and now work as a {r2}."),
        ("preference", f"My favorite {thing} is {x1}.", f"My favorite {thing} is {x2} now."),
        ("schedule", f"The team meeting is on {day1}.", f"The team meeting was moved to {day2}."),
        ("config", f"The API server listens on port {p1}.", f"The API server now runs on port {p2}."),
        ("tooling", f"We use {d1} as the main database.", f"We migrated the main database from {d1} to {d2}."),
        ("tooling", f"Let's use {k1} for caching.", f"We switched the cache to {k2}."),
        ("status", "The test suite is failing on main.", "All tests pass on main now."),
        ("relationship", "I'm single right now.", f"I got engaged to {name} last month."),
        ("count", f"I have {n1} kids.", f"I have {n2} kids."),
        ("code", f"```python\ndef {f}({a}):\n    ...\n```", f"```python\ndef {f}({b}):\n    ...\n```"),
    ]


def negatives(rng: random.Random):
    c1, c2 = _two(rng, CITIES)
    co1 = rng.choice(COMPANIES)
    d1 = rng.choice(DBS)
    act1, act2 = _two(rng, ACTIVITIES)
    day1, day2 = _two(rng, DAYS)
    thing, opts = rng.choice(THINGS)
    x1, x2 = _two(rng, opts)
    p1, p2 = rng.sample(range(3000, 9900, 100), 2)
    f, g = _two(rng, FUNCS)
    a, b = _two(rng, PARAMS)
    pet = rng.choice(PETS)
    name = rng.choice(NAMES)
    return [
        ("different_event", f"I {act1} on {day1}.", f"I {act2} on {day2}."),
        ("added_detail", f"I live in {c1}.", f"I love the cafes in {c1}."),
        ("added_detail", f"I work at {co1}.", f"At {co1} I lead the platform team."),
        ("paraphrase", f"We use {d1} as the main database.", f"Our data is stored in {d1}."),
        ("compatible_pref", f"I like {x1}.", f"I also enjoy {x2}."),
        ("other_service", f"The API server listens on port {p1}.", f"The metrics exporter listens on port {p2}."),
        ("travel", f"I live in {c1}.", f"I'm flying to {c2} for a conference next week."),
        ("pet", f"I have a {pet} named {name}.", f"{name} the {pet} loves long walks."),
        ("code_other_symbol", f"```python\ndef {f}({a}):\n    ...\n```", f"```python\ndef {g}({b}):\n    ...\n```"),
        ("unrelated", "The quarterly revenue report is due Friday.", "I painted the living room green."),
    ]


def generate(n_variants: int = 8, seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    items = []
    for v in range(n_variants):
        for cat, older, newer in positives(rng):
            items.append({"category": cat, "older": older, "newer": newer, "label": 1})
        for cat, older, newer in negatives(rng):
            items.append({"category": cat, "older": older, "newer": newer, "label": 0})
    for i, it in enumerate(items):
        it["id"] = f"cp{i:04d}"
        it["split"] = "dev" if rng.random() < 0.5 else "test"
    return items


def main() -> None:
    out = Path(__file__).parent / "contradiction_pairs.jsonl"
    items = generate()
    out.write_text("\n".join(json.dumps(i) for i in items) + "\n", encoding="utf-8")
    print(f"wrote {len(items)} pairs ({sum(i['label'] for i in items)} positive) to {out}")


if __name__ == "__main__":
    main()
