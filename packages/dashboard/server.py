"""Runtime dashboard: a dependency-free HTTP server that tails the decision log live.

    python -m dashboard.server --log-dir runs/demo --port 8765

GET  /                -> the dashboard page
GET  /api/state?since=N -> {"records": [...from line N], "escalations": [...]}
POST /api/override    -> validates an ``OverrideRequest`` and appends it to ``overrides.jsonl``;
                         the turn loop polls that file before each decision.

Reads JSONL directly and validates each line with the shared contracts (no other package imports).
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from pydantic import ValidationError

from contracts import DecisionLogRecord, EscalationEvent, OverrideRequest

STATIC = Path(__file__).parent / "static"


def _read_jsonl(path: Path, model, start: int = 0) -> list[dict]:
    out: list[dict] = []
    if not path.exists():
        return out
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f):
            if n < start or not line.strip():
                continue
            try:
                out.append(json.loads(model.model_validate_json(line).model_dump_json()))
            except (ValidationError, json.JSONDecodeError):
                continue
    return out


def make_handler(log_dir: Path):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # quiet
            pass

        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            url = urlparse(self.path)
            if url.path in ("/", "/index.html"):
                self._send(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
            elif url.path == "/api/state":
                since = int(parse_qs(url.query).get("since", ["0"])[0])
                payload = {
                    "records": _read_jsonl(log_dir / "decisions.jsonl", DecisionLogRecord, since),
                    "escalations": _read_jsonl(log_dir / "escalations.jsonl", EscalationEvent),
                    "conversation": log_dir.name,
                }
                self._send(200, json.dumps(payload).encode(), "application/json")
            else:
                self._send(404, b"not found", "text/plain")

        def do_POST(self):
            if urlparse(self.path).path != "/api/override":
                self._send(404, b"not found", "text/plain")
                return
            length = int(self.headers.get("Content-Length", "0"))
            try:
                req = OverrideRequest.model_validate_json(self.rfile.read(length))
            except ValidationError as e:
                self._send(400, str(e).encode(), "text/plain")
                return
            with open(log_dir / "overrides.jsonl", "a", encoding="utf-8") as f:
                f.write(req.model_dump_json() + "\n")
            self._send(200, b'{"queued": true}', "application/json")

    return Handler


def serve(log_dir: str | Path, port: int = 8765, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    return ThreadingHTTPServer((host, port), make_handler(log_dir))


def main() -> None:
    ap = argparse.ArgumentParser(description="Syno runtime dashboard")
    ap.add_argument("--log-dir", required=True)
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    httpd = serve(args.log_dir, args.port)
    print(f"dashboard: http://127.0.0.1:{args.port}/  (tailing {Path(args.log_dir).resolve()})")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
