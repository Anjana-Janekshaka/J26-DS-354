import json
import threading
import urllib.request

import pytest

from contracts import DecisionLogRecord, OverrideRequest
from dashboard import render_static, serve
from decision_logger import CorruptLogError, DecisionLogger, OverrideInbox
from integration import MemoryPipeline
from retrieval import RetrievalConfig

from conftest import CODE_SESSION


@pytest.fixture
def pipeline(tmp_path, embedder, nli):
    p = MemoryPipeline("it", token_budget=60, embedder=embedder, nli=nli, log_dir=tmp_path, retrieval_config=RetrievalConfig(min_score=0.0))
    yield p
    p.close()


def run_session(p):
    results = []
    for role, text in CODE_SESSION:
        if role == "user":
            results.append(p.user_turn(text))
        else:
            p.assistant_turn(text)
    return results


def test_end_to_end_logs_exact_records(pipeline, tmp_path):
    results = run_session(pipeline)
    recs = DecisionLogger(tmp_path).records()
    assert len(recs) == len(results) == 5
    assert all(isinstance(r, DecisionLogRecord) for r in recs)
    assert set(recs[-1].module_outputs) == {"sliding_window", "summarization", "rag"}
    line = (tmp_path / "decisions.jsonl").read_text(encoding="utf-8").splitlines()[0]
    assert set(json.loads(line)) == {"turn_id", "feature_vector", "decision", "module_outputs", "logged_at"}


def test_escalations_logged_and_consumed_next_turn(pipeline, tmp_path):
    results = run_session(pipeline)
    # A query that retrieves the stale get_user_tasks(user_id) chunk raises a contradiction escalation.
    pipeline.token_budget = 400
    pipeline.manager.token_budget = 400
    results.append(pipeline.user_turn("get_user_tasks user_id signature"))
    results.append(pipeline.user_turn("thanks"))
    events = DecisionLogger(tmp_path).escalation_events()
    assert events, "expected at least one Tier 2 escalation"
    by_turn = {r.turn.turn_id: i for i, r in enumerate(results)}
    for ev in events:
        i = by_turn[ev.source_turn_id]
        assert f"escalation from {ev.source_turn_id}" not in results[i].decision.rationale  # never same turn
        if i + 1 < len(results):
            assert f"escalation from {ev.source_turn_id}" in results[i + 1].decision.rationale


def test_override_inbox_reaches_controller(pipeline, tmp_path):
    OverrideInbox(tmp_path / "overrides.jsonl").submit(OverrideRequest(strategy="summarization", by="reviewer"))
    r = pipeline.user_turn("hello")
    assert r.decision.override.applied and r.decision.selected_strategy == "summarization"


def test_probe_turn_not_remembered(pipeline):
    run_session(pipeline)
    n = len(pipeline.manager.turns)
    r = pipeline.user_turn("What did we rename?", remember=False)
    assert r.turn.turn_id.endswith(".p1") and len(pipeline.manager.turns) == n


def test_logger_rejects_corrupt_lines(tmp_path):
    (tmp_path / "decisions.jsonl").write_text('{"turn_id": "x"}\n', encoding="utf-8")
    with pytest.raises(CorruptLogError):
        DecisionLogger(tmp_path).records()


def test_dashboard_static_and_live(pipeline, tmp_path):
    run_session(pipeline)
    lg = DecisionLogger(tmp_path)
    html = render_static(lg.records(), lg.escalation_events(), tmp_path / "dash.html").read_text(encoding="utf-8")
    assert "window.__CEAI_DATA__" in html and "selected_strategy" in html

    httpd = serve(tmp_path, port=0)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        state = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/state?since=2").read())
        assert len(state["records"]) == 3
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/override",
            data=json.dumps({"strategy": "rag", "by": "ui"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        assert urllib.request.urlopen(req).status == 200
        assert pipeline.user_turn("next").decision.override.by == "ui"
    finally:
        httpd.shutdown()
