"""Optional LLM backends, all exposing ``llm(system, user) -> str``.

Used for LLM-backed summary tiers, the LLM-judge half of the dual-source oracle, and QA answering
in the benchmark harnesses. Nothing in the core pipeline requires an LLM; when none is configured
those paths are skipped and reported as not run.

Backends (picked by ``get_llm``):

* ``OpenAICompatibleLLM`` - any OpenAI-compatible ``/chat/completions`` endpoint: a local Ollama or
  vLLM server (free, e.g. on a Kaggle / Colab GPU), or a free API tier such as Groq or OpenRouter.
  Standard library only. Configure with
      CEAI_LLM_BASE_URL   e.g. http://localhost:11434/v1  (Ollama)
      CEAI_LLM_MODEL      e.g. qwen2.5:7b-instruct
      CEAI_LLM_API_KEY    only for hosted endpoints
* ``ClaudeLLM`` - Anthropic SDK, used when Anthropic credentials are present and no
  ``CEAI_LLM_BASE_URL`` is set. Server-side refusal fallbacks are enabled (``fallbacks: "default"``);
  a final ``stop_reason == "refusal"`` raises.

``CachedLLM`` wraps any backend with an append-only JSONL cache keyed by (model, system, user), so
an interrupted run (e.g. a notebook timeout) resumes without repeating calls.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

CLAUDE_MODEL = os.environ.get("CEAI_CLAUDE_MODEL", "claude-opus-5-5")
_THINK = re.compile(r"<think>.*?</think>", re.S)


class LLMUnavailable(RuntimeError):
    pass


def credentials_present() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_PROFILE"))


class ClaudeLLM:
    def __init__(self, model: str = CLAUDE_MODEL, max_tokens: int = 16000, effort: str = "medium"):
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover
            raise LLMUnavailable("pip install anthropic to use the Claude backend") from e
        self.model = model
        self.name = f"anthropic/{model}"
        self.max_tokens = max_tokens
        self.effort = effort
        self.client = anthropic.Anthropic()

    def __call__(self, system: str, user: str) -> str:
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"effort": self.effort},
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default"},
        )
        if response.stop_reason == "refusal":
            raise LLMUnavailable(f"request declined ({getattr(response, 'stop_details', None)})")
        return "".join(block.text for block in response.content if block.type == "text")


class OpenAICompatibleLLM:
    """Minimal client for ``POST {base_url}/chat/completions`` (Ollama, vLLM, Groq, OpenRouter...)."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout_s: float = 300.0,
        max_retries: int = 6,
    ):
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.model = model
        self.name = f"openai-compatible/{model}"
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.calls = 0
        self.seconds = 0.0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def __call__(self, system: str, user: str) -> str:
        body = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
        ).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        delay = 2.0
        t_start = time.time()
        for attempt in range(self.max_retries + 1):
            req = urllib.request.Request(self.url, data=body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    data = json.loads(resp.read())
                break
            except urllib.error.HTTPError as e:
                retryable = e.code == 429 or e.code >= 500
                if not retryable or attempt == self.max_retries:
                    raise LLMUnavailable(f"{self.url} returned HTTP {e.code}: {e.read()[:300]!r}") from e
                wait = float(e.headers.get("Retry-After") or delay)
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == self.max_retries:
                    raise LLMUnavailable(f"cannot reach {self.url}: {e}") from e
                wait = delay
            time.sleep(wait)
            delay = min(delay * 2, 60.0)
        self.calls += 1
        self.seconds += time.time() - t_start
        usage = data.get("usage") or {}
        self.prompt_tokens += int(usage.get("prompt_tokens") or 0)
        self.completion_tokens += int(usage.get("completion_tokens") or 0)
        text = data["choices"][0]["message"].get("content") or ""
        return _THINK.sub("", text).strip()  # reasoning models (e.g. qwen3, deepseek-r1) emit <think> blocks


class CachedLLM:
    """Disk cache in front of any ``llm(system, user)``; safe to share between threads."""

    def __init__(self, inner: Callable[[str, str], str], path: str | Path, name: str | None = None):
        self.inner = inner
        self.name = name or getattr(inner, "name", type(inner).__name__)
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._cache: dict[str, str] = {}
        self.hits = 0
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    self._cache[rec["key"]] = rec["output"]

    def _key(self, system: str, user: str) -> str:
        return hashlib.sha256(json.dumps([self.name, system, user]).encode()).hexdigest()

    def __call__(self, system: str, user: str) -> str:
        key = self._key(system, user)
        with self._lock:
            if key in self._cache:
                self.hits += 1
                return self._cache[key]
        out = self.inner(system, user)
        with self._lock:
            self._cache[key] = out
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "model": self.name, "output": out}) + "\n")
        return out


def get_llm(cache_path: str | Path | None = None, role: str = "answer"):
    """Configured backend (OpenAI-compatible endpoint first, then Claude), optionally cached; else None.

    ``role='judge'`` reads ``CEAI_JUDGE_MODEL`` / ``CEAI_JUDGE_BASE_URL`` / ``CEAI_JUDGE_API_KEY`` first,
    falling back to the ``CEAI_LLM_*`` settings, so the judge can be a different (larger) model.
    """
    llm = None
    pick = (lambda k: os.environ.get(f"CEAI_JUDGE_{k}") or os.environ.get(f"CEAI_LLM_{k}")) if role == "judge" else (
        lambda k: os.environ.get(f"CEAI_LLM_{k}"))
    base = pick("BASE_URL")
    if base:
        model = pick("MODEL")
        if not model:
            raise LLMUnavailable("CEAI_LLM_BASE_URL is set but CEAI_LLM_MODEL is not")
        # Short replies are all the harnesses need; a low cap stops a chatty model spending minutes per call.
        default_cap = "16" if role == "judge" else "96"
        llm = OpenAICompatibleLLM(base, model, api_key=pick("API_KEY"), max_tokens=int(pick("MAX_TOKENS") or default_cap))
    elif credentials_present():
        try:
            llm = ClaudeLLM()
        except LLMUnavailable:
            llm = None
    if llm is not None and cache_path is not None:
        return CachedLLM(llm, cache_path)
    return llm


def concurrency() -> int:
    """Parallel requests the harnesses may send (match OLLAMA_NUM_PARALLEL / the server's batch size)."""
    return max(1, int(os.environ.get("CEAI_LLM_CONCURRENCY", "4")))


def stats(llm) -> dict:
    inner = getattr(llm, "inner", llm)
    calls = getattr(inner, "calls", 0)
    return {"calls": calls, "cache_hits": getattr(llm, "hits", 0), "seconds": round(getattr(inner, "seconds", 0.0), 1),
            "s_per_call": round(getattr(inner, "seconds", 0.0) / calls, 2) if calls else None,
            "prompt_tokens": getattr(inner, "prompt_tokens", 0), "completion_tokens": getattr(inner, "completion_tokens", 0)}


def describe(llm) -> str:
    return getattr(llm, "name", type(llm).__name__) if llm is not None else "none"
