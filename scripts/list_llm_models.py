"""List the models your AI key can use (reads .env; never prints the key).

    .venv\\Scripts\\python scripts\\list_llm_models.py

Put one of the printed ids in .env as CEAI_LLM_MODEL.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from integration.dotenv import load_dotenv  # noqa: E402
from integration.llm_client import USER_AGENT  # noqa: E402


def main() -> None:
    load_dotenv()
    base = os.environ.get("CEAI_LLM_BASE_URL", "").rstrip("/")
    key = os.environ.get("CEAI_LLM_API_KEY", "")
    if not base:
        raise SystemExit("CEAI_LLM_BASE_URL is not set (see .env.example)")
    req = urllib.request.Request(f"{base}/models", headers={"User-Agent": USER_AGENT, "Authorization": f"Bearer {key}"})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=20).read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read()[:300]!r}")
    models = sorted(data.get("data", []), key=lambda m: m.get("id", ""))
    print(f"{len(models)} models available at {base}:")
    for m in models:
        ctx = m.get("context_window")
        print(f"  {m.get('id')}" + (f"   (context {ctx})" if ctx else "") + ("" if m.get("active", True) else "   [inactive]"))
    print(f"\nCurrently set: CEAI_LLM_MODEL={os.environ.get('CEAI_LLM_MODEL', '')}")


if __name__ == "__main__":
    main()
