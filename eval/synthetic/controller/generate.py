"""Strategy-switch conversations for the controller (deterministic, seeded).

Each conversation mixes phases - personal chat, code definitions, debugging, a rename, a long
detour - and carries probes of five kinds, each with objective evidence requirements:

  early_recall     - recall a personal fact while the history still fits
  debug_followup   - ask about the fix suggested a few turns ago
  duplicate_build  - ask to write a helper that already exists (must surface the definition)
  renamed_call     - call a function whose parameters changed (needs the new signature, no unmarked old one)
  late_recall      - recall a personal fact after the long detour

Labels are NOT hand-assigned: the harness derives the oracle strategy per probe by checking which
strategy's assembled context satisfies the evidence requirement (see run.py).
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from eval.synthetic.summarization.generate import FILLER

CITIES = ["Lisbon", "Kyoto", "Oslo", "Austin", "Cairo", "Quito", "Hanoi", "Dublin"]
RELATIVES = ["sister", "brother", "cousin", "aunt"]
JOBS = ["pediatric nurse", "marine biologist", "tax attorney", "jazz pianist", "civil engineer", "pastry chef"]
HOBBIES = ["bouldering", "film photography", "beekeeping", "salsa dancing", "woodworking"]
DOMAINS = [("invoice", "invoices"), ("order", "orders"), ("ticket", "tickets"), ("shipment", "shipments"), ("lead", "leads")]
ERRORS = [("KeyError: 'customer'", "use .get('customer_id') instead of ['customer']"),
          ("TypeError: unsupported operand type(s) for +: 'int' and 'str'", "cast the quantity with int() before summing"),
          ("AttributeError: 'NoneType' object has no attribute 'total'", "return early when the lookup finds no row"),
          ("ValueError: time data '2024/01/02' does not match format", "parse dates with '%Y/%m/%d' instead of ISO")]


def make(rng: random.Random, cid: int) -> dict:
    msgs: list[dict] = []
    probes: list[dict] = []

    def say(role, text):
        msgs.append({"role": role, "content": text})

    def probe(kind, question, required, stale=None):
        probes.append({"after_index": len(msgs) - 1, "kind": kind, "question": question, "required": required, "stale": stale or []})

    city = rng.choice(CITIES)
    rel = rng.choice(RELATIVES)
    job = rng.choice(JOBS)
    hobby = rng.choice(HOBBIES)
    one, many = rng.choice(DOMAINS)
    err, fix = rng.choice(ERRORS)
    p_old, p_new = rng.sample(["customer_id", "cid", "account", "owner_id", "user_ref"], 2)

    # phase 1 - personal chat
    say("user", f"Before we start: I'm working from {city} this month, and my {rel} is a {job}.")
    say("assistant", "Nice, thanks for the context.")
    say("user", f"On weekends I've been getting into {hobby}.")
    say("assistant", f"{hobby.capitalize()} sounds like a great way to unwind.")
    probe("early_recall", f"What does my {rel} do for work?", [job])

    # phase 2 - code definitions
    say("user", f"Write a function to load {many} for a customer and one to format a {one} total as currency.")
    say("assistant", "Here they are:\n```python\n"
        f"def load_{many}({p_old}, status='open'):\n    return db.select('{many}', {p_old}={p_old}, status=status)\n\n"
        f"def format_{one}_total(amount, currency='EUR'):\n    return f'{{amount:,.2f}} {{currency}}'\n```")
    say("user", f"Explain how load_{many} handles closed {many}.")
    say("assistant", f"It filters on status, so closed {many} are excluded unless you pass status='closed'.")

    # phase 3 - debugging
    say("user", f"The {one} report crashes with {err} when I run it.")
    say("assistant", f"That happens in build_report(): {fix}.")
    say("user", "Okay, applied it. Re-running the report now.")
    say("assistant", "Let me know what the output looks like.")
    probe("debug_followup", f"It crashed again with {err.split(':')[0]} - what fix did you suggest?", [fix])
    # implicit follow-up: no lexical hook to the evidence; only recency connects them
    say("user", "Hmm, the numbers in the output look off now.")
    second_fix = rng.choice(["round amounts before grouping by month", "sort rows by created_at before the running total",
                             "drop the duplicated header row from the CSV", "convert cents to euros before summing"])
    say("assistant", f"Then {second_fix}.")
    probe("implicit_followup", "Still wrong after that. What should I try next?", [second_fix])

    # phase 4 - rename / signature change
    say("user", f"Rename the parameter {p_old} to {p_new} in load_{many}; the new auth layer only gives us {p_new}.")
    say("assistant", f"Done:\n```python\ndef load_{many}({p_new}, status='open'):\n    return db.select('{many}', {p_old}={p_new}, status=status)\n```")

    # phase 5 - long detour
    for _ in range(rng.randint(5, 7)):
        say("user", rng.choice(FILLER))
        say("assistant", rng.choice(FILLER))

    probe("duplicate_build", f"Write a helper that formats a {one} total as a currency string for the PDF export.", [f"def format_{one}_total("])
    probe("renamed_call", f"Now call load_{many} from the nightly sync job for every customer.", [f"def load_{many}({p_new}"], [f"load_{many}({p_old}"])
    probe("late_recall", f"Which city did I say I'm working from this month?", [city])
    return {"id": f"ctl{cid:03d}", "messages": msgs, "probes": probes}


def generate(n: int = 30, seed: int = 21) -> list[dict]:
    """Legacy set (family A wording, fixed structure). Kept unchanged so the original README
    numbers stay reproducible with ``run --split legacy``."""
    rng = random.Random(seed)
    return [make(rng, i) for i in range(n)]


# --------------------------------------------------------------------------- phrasing families
# Bump when the family generator's output changes, so cached traces are rebuilt.
GENERATOR_VERSION = "families-v1"

# Conversations per family and the fixed split (by family, so the test wording is never seen in
# training or tuning). The rules were written against A; B is unseen-but-trainable; C is held out.
FAMILY_SIZES = {"A": 60, "B": 70, "C": 70}
FAMILY_SEEDS = {"A": 101, "B": 202, "C": 303}
VAL_FROM_B = 20  # the last 20 B conversations are validation


def make_family(rng: random.Random, cid: str, family: str) -> dict:
    """Same evidence structure as ``make`` but with family wording and varied structure:
    0-3 extra exchanges before the code phase and a 2-12 exchange detour, so turn count and token
    pressure differ between conversations instead of being near-constant per probe kind."""
    from .families import FAMILIES

    tpl = FAMILIES[family]
    msgs: list[dict] = []
    probes: list[dict] = []

    city = rng.choice(CITIES)
    rel = rng.choice(RELATIVES)
    job = rng.choice(JOBS)
    hobby = rng.choice(HOBBIES)
    one, many = rng.choice(DOMAINS)
    err, fix = rng.choice(ERRORS)
    p_old, p_new = rng.sample(["customer_id", "cid", "account", "owner_id", "user_ref"], 2)
    second_fix = rng.choice(["round amounts before grouping by month", "sort rows by created_at before the running total",
                             "drop the duplicated header row from the CSV", "convert cents to euros before summing"])
    fields = dict(city=city, rel=rel, job=job, hobby=hobby, Hobby=hobby.capitalize(), one=one, many=many, err=err,
                  err_head=err.split(":")[0], fix=fix, second_fix=second_fix, p_old=p_old, p_new=p_new)

    def text(slot: str) -> str:
        return rng.choice(tpl[slot]).format(**fields)

    def say(role, content):
        msgs.append({"role": role, "content": content})

    def probe(kind, required, stale=None):
        probes.append({"after_index": len(msgs) - 1, "kind": kind, "question": text(kind), "required": required,
                       "stale": stale or []})

    def filler(n):
        for _ in range(n):
            say("user", rng.choice(FILLER))
            say("assistant", rng.choice(FILLER))

    say("user", text("intro"))
    say("assistant", text("intro_reply"))
    say("user", text("hobby"))
    say("assistant", text("hobby_reply"))
    probe("early_recall", [job])
    filler(rng.randint(0, 3))

    say("user", text("code_req"))
    say("assistant", "Here they are:\n```python\n"
        f"def load_{many}({p_old}, status='open'):\n    return db.select('{many}', {p_old}={p_old}, status=status)\n\n"
        f"def format_{one}_total(amount, currency='EUR'):\n    return f'{{amount:,.2f}} {{currency}}'\n```")
    say("user", text("explain"))
    say("assistant", text("explain_reply"))

    say("user", text("crash"))
    say("assistant", text("fix_reply"))
    say("user", text("applied"))
    say("assistant", text("applied_reply"))
    probe("debug_followup", [fix])
    say("user", text("off"))
    say("assistant", text("off_reply"))
    probe("implicit_followup", [second_fix])

    say("user", text("rename"))
    say("assistant", f"Done:\n```python\ndef load_{many}({p_new}, status='open'):\n    return db.select('{many}', {p_old}={p_new}, status=status)\n```")

    filler(rng.randint(2, 12))
    probe("duplicate_build", [f"def format_{one}_total("])
    probe("renamed_call", [f"def load_{many}({p_new}"], [f"load_{many}({p_old}"])
    probe("late_recall", [city])
    return {"id": cid, "family": family, "messages": msgs, "probes": probes}


def generate_families() -> list[dict]:
    convs = []
    for fam, n in FAMILY_SIZES.items():
        rng = random.Random(FAMILY_SEEDS[fam])
        convs += [make_family(rng, f"ctl-{fam}{i:03d}", fam) for i in range(n)]
    return convs


def make_splits(convs: list[dict]) -> dict[str, list[str]]:
    a = [c["id"] for c in convs if c["family"] == "A"]
    b = [c["id"] for c in convs if c["family"] == "B"]
    c = [c["id"] for c in convs if c["family"] == "C"]
    return {"train": a + b[:-VAL_FROM_B], "val": b[-VAL_FROM_B:], "test": c}


SPLITS_PATH = Path(__file__).parent / "splits.json"


def load_split(split: str) -> list[dict]:
    """Conversations for ``train`` / ``val`` / ``test`` (family-based) or ``legacy`` (original 30)."""
    if split == "legacy":
        return generate()
    convs = generate_families()
    splits = json.loads(SPLITS_PATH.read_text(encoding="utf-8")) if SPLITS_PATH.exists() else make_splits(convs)
    ids = set(splits[split])
    return [c for c in convs if c["id"] in ids]


def main() -> None:
    here = Path(__file__).parent
    out = here / "strategy_switch_conversations.jsonl"
    convs = generate()
    out.write_text("\n".join(json.dumps(c) for c in convs) + "\n", encoding="utf-8")
    print(f"wrote {len(convs)} legacy conversations, {sum(len(c['probes']) for c in convs)} probes to {out}")

    fams = generate_families()
    splits = make_splits(fams)
    assert not (set(splits["train"]) & set(splits["test"])) and not (set(splits["val"]) & set(splits["test"]))
    (here / "family_conversations.jsonl").write_text("\n".join(json.dumps(c) for c in fams) + "\n", encoding="utf-8")
    SPLITS_PATH.write_text(json.dumps({"generator_version": GENERATOR_VERSION, **splits}, indent=2) + "\n", encoding="utf-8")
    for k in ("train", "val", "test"):
        ids = set(splits[k])
        print(f"  {k:<5} {len(ids):>3} conversations, {sum(len(c['probes']) for c in fams if c['id'] in ids):>4} probes")
    print(f"wrote {SPLITS_PATH}")


if __name__ == "__main__":
    main()
