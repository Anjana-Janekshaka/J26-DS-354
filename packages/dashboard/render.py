"""Static export: the same dashboard page with the decision log embedded (no server needed)."""

from __future__ import annotations

import json
from pathlib import Path

from contracts import DecisionLogRecord, EscalationEvent

STATIC = Path(__file__).parent / "static"


def render_static(records: list[DecisionLogRecord], escalations: list[EscalationEvent], out_path: str | Path) -> Path:
    data = {
        "records": [json.loads(r.model_dump_json()) for r in records],
        "escalations": [json.loads(e.model_dump_json()) for e in escalations],
    }
    blob = json.dumps(data).replace("</", "<\\/")
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    html = html.replace("<script>\n(() => {", f"<script>window.__CEAI_DATA__ = {blob};</script>\n<script>\n(() => {{", 1)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
