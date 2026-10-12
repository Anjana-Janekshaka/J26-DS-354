"""Evaluation probes (``remember=False``) must be read-only: they may not change later decisions."""

from integration import MemoryPipeline
from retrieval import RetrievalConfig

CONVERSATION = [
    ("user", "I live in London near the river."),
    ("assistant", "Noted."),
    ("user", "Actually I live in Paris near the river now."),
    ("assistant", "Got it."),
]
PROBE = "Which city do I live in near the river?"
FOLLOW_UPS = ["Remind me where I live near the river.", "Thanks, that helps."]


def run(embedder, nli, with_probe: bool):
    pipe = MemoryPipeline("probe-test", token_budget=500, embedder=embedder, nli=nli,
                          retrieval_config=RetrievalConfig(check_contradictions=True, min_score=0.0))
    for role, text in CONVERSATION:
        if role == "user":
            pipe.user_turn(text, respond=False)
        else:
            pipe.assistant_turn(text)
    if with_probe:
        probe = pipe.user_turn(PROBE, remember=False, respond=False)
        # the probe itself sees the stale chunk, so it is the first turn to observe the flag
        assert "contradiction_flagged" in [e.kind for e in probe.escalations]
    results = [pipe.user_turn(text, respond=False) for text in FOLLOW_UPS]
    pipe.close()
    return results


def test_probe_does_not_swallow_contradiction_escalation(embedder, nli):
    a = run(embedder, nli, with_probe=False)
    b = run(embedder, nli, with_probe=True)
    kinds = lambda rs: [sorted(e.kind for e in r.escalations) for r in rs]  # noqa: E731
    assert "contradiction_flagged" in kinds(a)[0]
    assert "contradiction_flagged" in kinds(b)[0], "probe marked the flag as reported; the real turn never escalated it"
    assert kinds(a) == kinds(b)
    assert [r.decision.selected_strategy for r in a] == [r.decision.selected_strategy for r in b]
