"""Topic-shift-labeled workloads for the Dynamic Sliding Window (deterministic, seeded).

Each conversation is a sequence of topic blocks. Block starts are labeled as topic shifts. Every
block plants a few facts (each a (statement, paraphrased question) pair) among on-topic chatter.
Probes are questions asked later - either about the *current* block or about an *earlier* one -
with the gold turn id of the planted fact.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

TOPICS: dict[str, dict] = {
    "travel": {
        "facts": [
            ("We booked the hotel in {city} for {n} nights.", "How many nights did we book the hotel for?"),
            ("The flight to {city} leaves at {hour}:15 from gate B{n}.", "What time does the flight leave?"),
            ("Travel insurance costs {n}9 euros for the whole trip.", "How much was the travel insurance?"),
        ],
        "chatter": ["I still need to pack chargers and adapters.", "The weather there should be mild.",
                    "Maybe we can rent bikes once we arrive.", "I'll print the boarding passes tonight."],
    },
    "release": {
        "facts": [
            ("The release branch is cut every {day} at noon.", "When is the release branch cut?"),
            ("Version {n}.{n}.0 drops support for Python 3.8.", "Which version drops Python 3.8 support?"),
            ("Release notes must be approved by {name} before publishing.", "Who approves the release notes?"),
        ],
        "chatter": ["The changelog draft is in the wiki.", "CI was green on the last three runs.",
                    "We should tag after the smoke tests.", "Let's keep the release scope small."],
    },
    "fitness": {
        "facts": [
            ("My coach set my target heart rate to {n}5 bpm for intervals.", "What heart rate did the coach set for intervals?"),
            ("I run the {n}0k loop along the river every {day}.", "Which day do I run the river loop?"),
            ("The gym membership renews on the {n}th of each month.", "When does the gym membership renew?"),
        ],
        "chatter": ["Stretching after runs has helped my knees.", "I bought new running shoes last week.",
                    "Hydration is the hard part in summer.", "Rest days matter more than I thought."],
    },
    "budget": {
        "facts": [
            ("The marketing budget for Q{n} is {n}2 thousand dollars.", "What is the marketing budget for the quarter?"),
            ("Any purchase over {n}00 dollars needs approval from {name}.", "Who approves large purchases?"),
            ("We switched the payroll provider to {company} in March.", "Which payroll provider do we use?"),
        ],
        "chatter": ["Finance wants the forecast by Friday.", "Office supplies came in under budget.",
                    "The audit went smoothly this year.", "We might renegotiate the cloud contract."],
    },
    "garden": {
        "facts": [
            ("I planted {n} tomato plants along the south fence.", "How many tomato plants did I plant?"),
            ("The sprinkler runs at {hour} am every {day}.", "When does the sprinkler run?"),
            ("{name} gave me the lavender cuttings from her garden.", "Who gave me the lavender cuttings?"),
        ],
        "chatter": ["Slugs keep eating the lettuce.", "Compost is finally ready to use.",
                    "The roses bloomed early this year.", "I need a bigger watering can."],
    },
    "database": {
        "facts": [
            ("The orders table is partitioned by month on created_at.", "How is the orders table partitioned?"),
            ("Nightly backups are kept for {n}0 days in cold storage.", "How long are nightly backups kept?"),
            ("Read replicas lag at most {n} seconds behind the primary.", "How far behind can the read replicas lag?"),
        ],
        "chatter": ["Vacuum ran longer than usual last night.", "We should add an index on customer_id.",
                    "Connection pooling settings look fine.", "The slow query log is noisy."],
    },
}
CITIES = ["Lisbon", "Kyoto", "Oslo", "Austin", "Cairo", "Quito"]
NAMES = ["Priya", "Marco", "Aiko", "Tunde", "Elena", "Jonas"]
COMPANIES = ["Gusto", "Deel", "Rippling", "Paychex"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
ACKS = ["Got it.", "Makes sense.", "Noted, thanks.", "Sounds good.", "Okay, I'll remember that."]


def _fill(rng, s: str) -> str:
    return s.format(city=rng.choice(CITIES), n=rng.randint(2, 9), hour=rng.randint(6, 11), day=rng.choice(DAYS),
                    name=rng.choice(NAMES), company=rng.choice(COMPANIES))


def make_conversation(rng: random.Random, cid: int, n_blocks: int = 5) -> dict:
    msgs: list[dict] = []
    shifts: list[int] = []
    planted: list[dict] = []
    probes: list[dict] = []
    topics = rng.sample(list(TOPICS), n_blocks)
    for b, topic in enumerate(topics):
        spec = TOPICS[topic]
        shifts.append(len(msgs))
        first = True
        facts = rng.sample(spec["facts"], 2)
        for fact, question in facts:
            for _ in range(rng.randint(1, 2)):
                text = rng.choice(spec["chatter"])
                if first and b > 0:
                    text = f"Switching topics - {topic} now. " + text
                    first = False
                msgs.append({"role": "user", "content": text, "block": b})
                msgs.append({"role": "assistant", "content": rng.choice(ACKS), "block": b})
            msgs.append({"role": "user", "content": _fill(rng, fact), "block": b})
            planted.append({"turn_index": len(msgs) - 1, "question": question, "block": b})
            msgs.append({"role": "assistant", "content": rng.choice(ACKS), "block": b})
        # probes after the block: one about this block, one about an earlier block (if any)
        own = [p for p in planted if p["block"] == b]
        probes.append({"after_index": len(msgs) - 1, "kind": "current_block", **rng.choice(own)})
        if b > 0:
            older = [p for p in planted if p["block"] < b]
            probes.append({"after_index": len(msgs) - 1, "kind": "earlier_block", **rng.choice(older)})
    return {"id": f"sw{cid:03d}", "messages": msgs, "shift_indices": shifts, "probes": probes}


def generate(n: int = 40, seed: int = 5) -> list[dict]:
    rng = random.Random(seed)
    return [make_conversation(rng, i) for i in range(n)]


def main() -> None:
    out = Path(__file__).parent / "topic_shift_workloads.jsonl"
    convs = generate()
    out.write_text("\n".join(json.dumps(c) for c in convs) + "\n", encoding="utf-8")
    print(f"wrote {len(convs)} conversations, {sum(len(c['probes']) for c in convs)} probes to {out}")


if __name__ == "__main__":
    main()
