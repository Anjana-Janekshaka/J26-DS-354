"""Chat model switching and .env loading (no network, no models)."""

import io
import json

import pytest

from console import chat
from integration.dotenv import load_dotenv


@pytest.fixture
def api_env(monkeypatch):
    monkeypatch.setenv("CEAI_LLM_BASE_URL", "https://api.example.test/openai/v1")
    monkeypatch.setenv("CEAI_LLM_MODEL", "big-model")
    monkeypatch.setenv("CEAI_LLM_API_KEY", "test-key")
    chat._api_cache.clear()


def test_api_model_list_keeps_chat_models_only(api_env, monkeypatch):
    seen = {}

    def fake_urlopen(req, timeout=0):
        seen["ua"] = req.get_header("User-agent")
        seen["auth"] = req.get_header("Authorization")
        data = {"data": [{"id": m} for m in ["whisper-large-v3", "big-model", "meta-llama/llama-prompt-guard-2-22m",
                                             "canopylabs/orpheus-v1-english", "small-model"]]}
        return io.BytesIO(json.dumps(data).encode())

    monkeypatch.setattr(chat.urllib.request, "urlopen", fake_urlopen)
    assert chat._api_models("https://api.example.test/openai/v1", "test-key") == ["big-model", "small-model"]
    assert seen["auth"] == "Bearer test-key" and "Python-urllib" not in seen["ua"]


def test_choices_cover_api_and_ollama(api_env, monkeypatch):
    monkeypatch.setattr(chat, "_api_models", lambda base, key: ["big-model", "small-model"])
    monkeypatch.setattr(chat, "_ollama_models", lambda base=chat.OLLAMA: ["qwen2.5:7b"])
    got = [(c["provider"], c["id"]) for c in chat.model_choices()]
    assert got == [("api", "big-model"), ("api", "small-model"), ("ollama", "qwen2.5:7b")]


def test_choices_fall_back_to_configured_model_when_list_fails(api_env, monkeypatch):
    monkeypatch.setattr(chat, "_api_models", lambda base, key: [])
    monkeypatch.setattr(chat, "_ollama_models", lambda base=chat.OLLAMA: [])
    assert [c["id"] for c in chat.model_choices()] == ["big-model"]


def test_use_model_switches_provider_and_turns_off(api_env, monkeypatch):
    monkeypatch.setenv("CEAI_CHAT_MAX_TOKENS", "900")
    session = object.__new__(chat.ChatSession)  # skip loading the memory models
    session.llm, session.ai = chat.make_llm("api", "big-model")
    assert session.ai["provider"] == "api" and session.llm.max_tokens == 900

    session.use_model("small-model")  # same provider
    assert session.ai["model"] == "small-model" and session.llm.url.startswith("https://api.example.test")

    session.use_model("qwen2.5:7b", "ollama")
    assert session.ai["where"] == chat.OLLAMA_WHERE and session.llm.url.startswith(chat.OLLAMA)

    session.use_model("none")
    assert session.llm is None and session.ai["connected"] is False
    with pytest.raises(ValueError):
        session.use_model("big-model")  # no provider left to infer


def test_dotenv_does_not_override_and_strips_quotes(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text('SYNO_T_A=from-file\nexport SYNO_T_B="quoted"\n# SYNO_T_C=comment\nSYNO_T_D=\n', encoding="utf-8")
    monkeypatch.setenv("SYNO_T_A", "from-shell")
    for k in ("SYNO_T_B", "SYNO_T_C", "SYNO_T_D"):
        monkeypatch.delenv(k, raising=False)
    assert load_dotenv(f) == ["SYNO_T_B"]
    import os

    assert os.environ["SYNO_T_A"] == "from-shell" and os.environ["SYNO_T_B"] == "quoted"
    assert "SYNO_T_C" not in os.environ and "SYNO_T_D" not in os.environ
    monkeypatch.delenv("SYNO_T_B")
