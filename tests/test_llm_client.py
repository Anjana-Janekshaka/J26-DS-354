import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from integration.llm_client import CachedLLM, LLMUnavailable, OpenAICompatibleLLM, get_llm


class _Mock:
    def __init__(self, fail_first: int = 0, status: int = 429):
        self.requests = []
        self.fail_first = fail_first
        self.status = status
        mock = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                mock.requests.append({"path": self.path, "auth": self.headers.get("Authorization"), "body": body})
                if mock.fail_first > 0:
                    mock.fail_first -= 1
                    self.send_response(mock.status)
                    self.send_header("Retry-After", "0")
                    self.end_headers()
                    return
                out = {"choices": [{"message": {"content": "<think>hmm</think> Paris"}}], "usage": {"prompt_tokens": 12, "completion_tokens": 3}}
                data = json.dumps(out).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}/v1"

    def close(self):
        self.httpd.shutdown()


def test_openai_compatible_request_shape_and_think_stripping():
    m = _Mock()
    try:
        llm = OpenAICompatibleLLM(m.base, "qwen2.5:7b-instruct", api_key="k")
        assert llm("sys", "where?") == "Paris"
        req = m.requests[0]
        assert req["path"] == "/v1/chat/completions" and req["auth"] == "Bearer k"
        assert req["body"]["model"] == "qwen2.5:7b-instruct" and req["body"]["temperature"] == 0.0
        assert [x["role"] for x in req["body"]["messages"]] == ["system", "user"]
        assert (llm.prompt_tokens, llm.completion_tokens) == (12, 3)
    finally:
        m.close()


def test_retries_rate_limit_then_succeeds():
    m = _Mock(fail_first=2, status=429)
    try:
        assert OpenAICompatibleLLM(m.base, "x", max_retries=3)("s", "u") == "Paris"
        assert len(m.requests) == 3
    finally:
        m.close()


def test_non_retryable_error_raises():
    m = _Mock(fail_first=5, status=400)
    try:
        with pytest.raises(LLMUnavailable):
            OpenAICompatibleLLM(m.base, "x")("s", "u")
        assert len(m.requests) == 1
    finally:
        m.close()


def test_cache_resumes_across_instances(tmp_path):
    calls = []

    def fake(system, user):
        calls.append(user)
        return user.upper()

    c1 = CachedLLM(fake, tmp_path / "c.jsonl", name="fake")
    assert c1("s", "a") == "A" and c1("s", "a") == "A"
    c2 = CachedLLM(fake, tmp_path / "c.jsonl", name="fake")
    assert c2("s", "a") == "A" and c2("s", "b") == "B"
    assert calls == ["a", "b"] and c2.hits == 1


def test_get_llm_selection(monkeypatch, tmp_path):
    for k in ("CEAI_LLM_BASE_URL", "CEAI_LLM_MODEL", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_PROFILE"):
        monkeypatch.delenv(k, raising=False)
    assert get_llm() is None
    monkeypatch.setenv("CEAI_LLM_BASE_URL", "http://localhost:11434/v1")
    with pytest.raises(LLMUnavailable):
        get_llm()
    monkeypatch.setenv("CEAI_LLM_MODEL", "qwen2.5:7b-instruct")
    llm = get_llm(tmp_path / "cache.jsonl")
    assert isinstance(llm, CachedLLM) and llm.name == "openai-compatible/qwen2.5:7b-instruct"
