"""Replay console: the recorder produces a complete snapshot per turn (fast mode, no models)."""

import json

from console.record import record, write
from demo.coding_session.scenarios import SCENARIOS


def test_recording_is_complete_and_consistent(tmp_path):
    sc = SCENARIOS[0]
    session = record(sc, fast=True)
    assert len(session["turns"]) == len(sc.exchanges)
    assert session["n_traps"] == len(sc.traps)
    for t in session["turns"]:
        assert {"signal", "features", "rules", "decision", "candidates", "prompt", "raised", "traps"} <= t.keys()
        assert set(t["candidates"]) == {"sliding_window", "summarization", "rag"}
        fired = [r for r in t["rules"] if r["fired"]]
        assert len(fired) <= 1
        # The rule the table says fired is the rule named in the logged rationale.
        assert (fired[0]["rule"] if fired else t["decision"]["rule"]) == t["decision"]["rule"]
        if not fired:
            assert t["decision"]["rule"] in ("hold", "default")
    for trap in [x for t in session["turns"] for x in t["traps"]]:
        assert {"adaptive", "fixed_6_exchange_window", "sliding_window", "summarization", "rag", "hybrid"} <= trap.keys()

    path = write(session, tmp_path)
    body = path.read_text(encoding="utf-8").split(" = ", 2)[-1].rstrip().rstrip(";")
    assert json.loads(body)["slug"] == session["slug"]
    assert session["slug"] in (tmp_path / "index.js").read_text(encoding="utf-8")


def test_message_18_escalation_switches_refactor_to_rag():
    """The controller path does not depend on the embedder, so the demo's key story holds in fast mode."""
    t18 = record(SCENARIOS[0], fast=True)["turns"][17]
    assert t18["decision"]["rule"] == "refactor_request"
    assert t18["decision"]["escalations"] and t18["decision"]["strategy"] == "rag"
