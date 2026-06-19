from __future__ import annotations

import json
import os
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.brain_engine import BrainFirstEngine

STATIC_DIR = ROOT / "app" / "static"
ENGINE = BrainFirstEngine(ROOT / "brain")


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/api/health", "/health", "/healthz"}:
            self._send_json({"ok": True})
            return

        if parsed.path == "/api/meta":
            self._send_json(
                {
                    "grades": ["auto", "1학년", "2학년", "3학년"],
                    "topics": ["auto", "출결", "창체", "교과학습발달상황", "수상", "자격증", "독서", "행특", "정정", "기타"],
                    "questionTypes": ["auto", "2026 변경사항", "학년별 차이", "기재 가능 여부", "원문 페이지 찾기"],
                }
            )
            return

        if parsed.path in {"/", "/index.html"}:
            self.path = "/index.html"
        elif not parsed.path.startswith("/api/") and "." not in Path(parsed.path).name:
            self.path = "/index.html"

        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/ask":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
            question = payload["question"].strip()
        except Exception:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid request body")
            return

        if not question:
            self.send_error(HTTPStatus.BAD_REQUEST, "Question is required")
            return

        response = ENGINE.answer_question(
            question=question,
            selected_grade=payload.get("selectedGrade", "auto"),
            selected_topic=payload.get("selectedTopic", "auto"),
            selected_question_type=payload.get("selectedQuestionType", "auto"),
        )
        self._send_json(response)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str | None = None, port: int | None = None) -> None:
    resolved_host = host or os.environ.get("HOST", "0.0.0.0")
    resolved_port = port or int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((resolved_host, resolved_port), AppHandler)
    print(f"Serving on http://{resolved_host}:{resolved_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
