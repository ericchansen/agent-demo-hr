"""Local Teams-style chat demo — the user-facing surface. Zero new deps (stdlib).

    python -m demo.app            # serves http://127.0.0.1:8000

# ponytail: a single-file stdlib http.server (ThreadingHTTPServer) for a local
# demo — not a production host. All real work is the existing Roster tools + the
# aggregate stand-in, wired through demo/router.py. The persona dropdown sets the
# per-request signed-in user so the row-level-security money-shot works for real.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from roster_mcp.auth_obo import resolve_scope
from roster_mcp.config import db_path, export_dir

from .router import route

HOST, PORT = "127.0.0.1", 8000
MAX_REQUEST_BYTES = 16_384

PERSONAS = [
    ("EMEA HR Business Partner", "emea.hrbp@contoso.com"),
    ("APAC HR Business Partner", "apac.hrbp@contoso.com"),
]

DEMO_QUESTIONS = [
    "What's Contoso's attrition rate in EMEA this year?",
    "Which team has the highest attrition?",
    "List active employees on the Azure Data team in EMEA.",
    "Export the full active roster for my region to Excel.",
    "Who rolls up to employee 100001?",
]

# Compact column subset for the in-chat table (full set is exported).
DISPLAY_COLS = ["employee_id", "full_name", "job_title", "team", "region", "active_status"]

_TEMPLATE = Path(__file__).resolve().parent / "index.html"


def _render_page() -> str:
    opts = "".join(f'<option value="{upn}">{name}</option>' for name, upn in PERSONAS)
    chips = "".join(f'<div class="chip">{q}</div>' for q in DEMO_QUESTIONS)
    return (
        _TEMPLATE.read_text(encoding="utf-8")
        .replace("__PERSONA_OPTS__", opts)
        .replace("__CHIPS__", chips)
        .replace("__DISPLAY_COLS__", json.dumps(DISPLAY_COLS))
    )


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # quieter console
        pass

    def _send(self, code: int, body: bytes, ctype: str, headers: dict | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: dict) -> None:
        self._send(
            code,
            json.dumps(payload).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _json_error(self, code: int, message: str) -> None:
        self._send_json(
            code,
            {"path": "deterministic", "tool": "error", "answer": message},
        )

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send(200, _render_page().encode("utf-8"), "text/html; charset=utf-8")
        elif parsed.path == "/favicon.ico":
            self._send(204, b"", "image/x-icon")
        elif parsed.path == "/download":
            self._download(parse_qs(parsed.query).get("file", [""])[0])
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/chat":
            self._send(404, b"not found", "text/plain")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            self._json_error(400, "Invalid Content-Length.")
            return
        if length <= 0:
            self._json_error(400, "Request body is required.")
            return
        if length > MAX_REQUEST_BYTES:
            self._json_error(413, "Request body is too large.")
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json_error(400, "Request body must be valid JSON.")
            return
        if not isinstance(payload, dict):
            self._json_error(400, "Request body must be a JSON object.")
            return
        question = payload.get("question")
        upn = payload.get("upn")
        if not isinstance(question, str) or not question.strip():
            self._json_error(400, "Question is required.")
            return
        if upn is not None and not isinstance(upn, str):
            self._json_error(400, "UPN must be a string.")
            return
        scope = resolve_scope(upn or None)
        self._send_json(200, route(question, scope))

    def _download(self, name: str) -> None:
        base = export_dir().resolve()
        target = (base / name).resolve()
        # path-traversal guard: file must sit directly in export_dir, right suffix
        if target.parent != base or target.suffix not in {".xlsx", ".csv"} or not target.exists():
            self._send(404, b"not found", "text/plain")
            return
        ctype = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if target.suffix == ".xlsx"
            else "text/csv"
        )
        self._send(
            200,
            target.read_bytes(),
            ctype,
            {"Content-Disposition": f'attachment; filename="{target.name}"'},
        )


def main() -> None:
    if not db_path().exists():
        raise SystemExit(f"Seed DB not found at {db_path()}. Run:  python data/seed_local.py")
    print(f"Contoso HR Assistant demo -> http://{HOST}:{PORT}  (Ctrl+C to stop)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
