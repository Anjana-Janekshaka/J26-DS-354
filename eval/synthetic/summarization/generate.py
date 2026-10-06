"""Degradation-injected developer traces for the summarization engine (deterministic, seeded).

Each trace is a coding conversation into which degradations are injected: parameter changes,
function renames, setting changes, a relocation, and long filler turns that push early facts out of
any recency window. Ground truth records the *current* value of every fact and every superseded
value, so the harness can measure what survives summarization and whether stale state leaks.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

VERBS = ["get", "load", "sync", "build", "parse", "send", "fetch", "render", "compute", "archive"]
NOUNS = ["user_tasks", "invoice", "digest", "report_rows", "config", "orders", "metrics", "session", "webhook", "audit_log"]
PARAMS = ["user_id", "uid", "account_id", "path", "limit", "since", "due_date", "payload", "timeout", "retries", "tz", "verbose"]
SETTINGS = [("api_port", ["8080", "9000", "8443", "5000"]), ("log_level", ["INFO", "DEBUG", "WARNING"]),
            ("worker_count", ["4", "8", "16"]), ("cache_ttl", ["60", "300", "900"])]
CITIES = ["London", "Paris", "Berlin", "Lisbon", "Toronto", "Seoul"]
CONSTRAINTS = ["We must never log raw access tokens.", "The public API must stay backwards compatible until v3.",
               "Do not add new dependencies without review.", "All timestamps must be stored in UTC."]
FILLER = [
    "Let's also tidy the CI workflow: cache pip downloads, run ruff before pytest, upload junit reports, and pin the action versions so builds are reproducible across forks and release branches.",
    "For the docs site we can use mkdocs-material with a navigation section per service, an architecture page with the request flow, and a changelog generated from conventional commits on each tagged release.",
    "The Dockerfile should be multi-stage: build wheels in a builder image, copy them into a slim runtime image with a non-root user, and keep the virtualenv and local caches out of the build context.",
    "On observability: emit JSON logs with a request id, export RED metrics per endpoint, and add a tracing span around every outbound HTTP call so slow third-party responses show up on the latency dashboard.",
    "For the staging deploy, push the image from CI on merges to main, run migrations as a release step before traffic shifts, and keep rollback to a single command documented in the runbook.",
]


def _code(name: str, params: list[str]) -> str:
    return f"```python\ndef {name}({', '.join(params)}):\n    ...\n```"


def make_trace(rng: random.Random, tid: int) -> dict:
    msgs: list[tuple[str, str]] = []
    funcs: dict[str, list[str]] = {}
    superseded: list[str] = []
    names = rng.sample([f"{v}_{n}" for v in VERBS for n in NOUNS], 4)
    for name in names:
        params = rng.sample(PARAMS, rng.randint(1, 3))
        funcs[name] = params
        msgs += [("user", f"Write a function {name} for the service layer."), ("assistant", "Added:\n" + _code(name, params))]
    city1, city2 = rng.sample(CITIES, 2)
    msgs += [("user", f"Context for later: I live in {city1} so standups are in my morning."), ("assistant", "Noted.")]
    setting, values = rng.choice(SETTINGS)
    v1, v2 = rng.sample(values, 2)
    msgs += [("user", f"The {setting} is set to {v1} in production."), ("assistant", "Got it.")]
    constraint = rng.choice(CONSTRAINTS)
    msgs += [("user", constraint), ("assistant", "Understood, I will follow that.")]

    for _ in range(rng.randint(3, 5)):
        msgs += [("user", rng.choice(FILLER)), ("assistant", rng.choice(FILLER))]

    # degradation 1: parameter change on one function
    f1 = names[0]
    old_sig = f"def {f1}({', '.join(funcs[f1])})"
    new_params = [p for p in funcs[f1]] + [rng.choice([p for p in PARAMS if p not in funcs[f1]])]
    funcs[f1] = new_params
    superseded.append(old_sig)
    msgs += [("user", f"Change the signature of {f1}: it needs one more parameter."), ("assistant", "Updated:\n" + _code(f1, new_params))]
    # degradation 2: function rename
    f2 = names[1]
    new_name = "fetch_" + f2.split("_", 1)[1] if not f2.startswith("fetch_") else "load_" + f2.split("_", 1)[1]
    superseded.append(f"def {f2}({', '.join(funcs[f2])})")
    funcs[new_name] = funcs.pop(f2)
    msgs += [("user", f"Rename {f2} to {new_name}."), ("assistant", "Renamed:\n" + _code(new_name, funcs[new_name]))]
    # degradation 3: setting change + relocation
    msgs += [("user", f"The {setting} has been changed to {v2}."), ("assistant", "Updated the deployment config.")]
    msgs += [("user", f"Also, I just moved to {city2}, so standups shift."), ("assistant", "Okay.")]

    for _ in range(rng.randint(2, 4)):
        msgs += [("user", rng.choice(FILLER)), ("assistant", rng.choice(FILLER))]
    msgs += [("user", "ok"), ("assistant", "sure")]

    current = {f"def {n}({', '.join(p)})": "signature" for n, p in funcs.items()}
    current[v2] = "setting"
    current[city2] = "location"
    current[constraint] = "constraint"
    stale = superseded + [f"{setting} is set to {v1}", city1]
    return {"id": f"trace{tid:03d}", "messages": msgs, "current_facts": current, "stale_facts": stale}


def generate(n: int = 30, seed: int = 11) -> list[dict]:
    rng = random.Random(seed)
    return [make_trace(rng, i) for i in range(n)]


def main() -> None:
    out = Path(__file__).parent / "degradation_traces.jsonl"
    traces = generate()
    out.write_text("\n".join(json.dumps(t) for t in traces) + "\n", encoding="utf-8")
    print(f"wrote {len(traces)} traces to {out}")


if __name__ == "__main__":
    main()
