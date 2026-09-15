"""Standalone web interface for the existing IT Helpdesk agent.

This module deliberately imports the agent runtime from the starter project and
does not change the CLI, prompts, tool declarations, or evaluation fixtures.
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from datetime import datetime
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import urlparse

UI_DIR = Path(__file__).resolve().parent
ROOT = UI_DIR.parent
STATIC_DIR = UI_DIR / "static"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the live runtime instead of duplicating its agent loop.
from chat import (  # noqa: E402
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env  # noqa: E402
from providers import make_provider  # noqa: E402
from tools import load_tool_declarations, to_openai_tools  # noqa: E402
from versioning import artifact_version_dict, build_artifact_version  # noqa: E402

MODEL_OPTIONS = {
    "openai": ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"],
    "gemini": ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.5-pro"],
    "openrouter": ["openai/gpt-4o-mini", "openai/gpt-4.1-mini", "google/gemini-2.5-flash"],
    "anthropic": ["claude-haiku-4-5-20251001"],
}
VERSION_OPTIONS = ["v0", "v1", "v2", "v3"]


class HelpdeskWebApp:
    def __init__(self, args: argparse.Namespace) -> None:
        load_lab_env(ROOT)
        self.provider_name = args.provider
        self.provider = make_provider(args.provider)
        self.model = args.model or getattr(self.provider, "default_model", None)
        self.history_window = args.history_window
        self.max_tool_rounds = args.max_tool_rounds
        self.system_prompt_path = args.system_prompt
        self.tools_path = args.tools
        self.system_prompt = self.system_prompt_path.read_text(encoding="utf-8")
        self.tools = to_openai_tools(load_tool_declarations(self.tools_path))
        self.artifact = build_artifact_version(args.version, self.system_prompt_path, self.tools_path)
        self.transcripts_dir = args.transcripts_dir
        self.sessions: dict[str, dict[str, Any]] = {}
        self.lock = Lock()

    def config(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model": self.model,
            "history_window": self.history_window,
            "max_tool_rounds": self.max_tool_rounds,
            **artifact_version_dict(self.artifact),
        }

    def options(self) -> dict[str, Any]:
        return {"providers": MODEL_OPTIONS, "versions": VERSION_OPTIONS}

    def configure(self, provider_name: str, model: str, version: str, old_session_id: str | None) -> tuple[str, dict[str, Any]]:
        if provider_name not in MODEL_OPTIONS or model not in MODEL_OPTIONS[provider_name]:
            raise ValueError("Provider hoặc model không hợp lệ.")
        if version not in VERSION_OPTIONS:
            raise ValueError("Version chỉ có thể là v0, v1, v2 hoặc v3.")
        with self.lock:
            self.provider_name = provider_name
            self.provider = make_provider(provider_name)
            self.model = model
            self.artifact = build_artifact_version(version, self.system_prompt_path, self.tools_path)
            if old_session_id:
                self.sessions.pop(old_session_id, None)
            return self.new_session()

    def new_session(self) -> tuple[str, dict[str, Any]]:
        session_id = secrets.token_urlsafe(24)
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join((safe_slug(self.artifact.version), safe_slug(self.provider_name), timestamp))
        transcript_path = self.transcripts_dir / f"{transcript_id}.transcript.json"
        session = {
            "history": [],
            "transcript_path": transcript_path,
            "transcript": {
                "transcript_id": transcript_id,
                **artifact_version_dict(self.artifact),
                "provider": self.provider_name,
                "model": self.model,
                "system_prompt": str(self.system_prompt_path),
                "tools": str(self.tools_path),
                "history_window": self.history_window,
                "max_tool_rounds": self.max_tool_rounds,
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "turns": [],
            },
        }
        self.sessions[session_id] = session
        return session_id, session

    def get_session(self, session_id: str | None) -> tuple[str, dict[str, Any]]:
        with self.lock:
            if session_id and session_id in self.sessions:
                return session_id, self.sessions[session_id]
            return self.new_session()

    def reset(self, old_session_id: str | None) -> tuple[str, dict[str, Any]]:
        with self.lock:
            if old_session_id:
                self.sessions.pop(old_session_id, None)
            return self.new_session()

    def chat(self, session_id: str | None, user_text: str) -> tuple[str, dict[str, Any]]:
        clean_text = user_text.strip()
        if not clean_text:
            raise ValueError("Tin nhắn không được để trống.")

        session_id, session = self.get_session(session_id)
        with self.lock:
            history = session["history"]
            turn_record: dict[str, Any] = {
                "turn_index": len(session["transcript"]["turns"]) + 1,
                "started_at": now_iso(),
                "user": clean_text,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }
            messages = [
                {"role": "system", "content": self.system_prompt},
                *trim_history(history, self.history_window),
                {"role": "user", "content": clean_text},
            ]
            try:
                result = run_model_tool_loop(
                    provider=self.provider,
                    messages=messages,
                    tools=self.tools,
                    model=self.model,
                    max_tool_rounds=self.max_tool_rounds,
                )
                turn_record.update(result)
                assistant_text = result["assistant_text"]
                history.extend(({"role": "user", "content": clean_text}, {"role": "assistant", "content": assistant_text}))
            except Exception as exc:  # Do not leak provider implementation details or secrets.
                turn_record.update({
                    "status": "provider_error",
                    "assistant_text": "Không thể kết nối agent lúc này. Kiểm tra provider và cấu hình cục bộ rồi thử lại.",
                    "error": type(exc).__name__,
                })

            turn_record["ended_at"] = now_iso()
            session["transcript"]["turns"].append(turn_record)
            write_transcript(session["transcript_path"], session["transcript"])
            response = {
                "assistant_text": turn_record["assistant_text"],
                "status": turn_record["status"],
                "rounds": turn_record["rounds"],
                "tool_events": turn_record["tool_events"],
                "artifact_version": self.artifact.artifact_version,
                "transcript_id": session["transcript"]["transcript_id"],
                "transcript_path": str(session["transcript_path"]),
            }
            if "error" in turn_record:
                response["error"] = turn_record["error"]
            return session_id, response


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "HelpdeskUI/1.0"

    @property
    def app(self) -> HelpdeskWebApp:
        return self.server.app  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[ui] {self.address_string()} - {format % args}")

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK, session_id: str | None = None) -> None:
        raw = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        if session_id:
            self.send_header("Set-Cookie", f"helpdesk_session={session_id}; Path=/; HttpOnly; SameSite=Lax")
        self.end_headers()
        self.wfile.write(raw)

    def session_id(self) -> str | None:
        cookie = SimpleCookie(self.headers.get("Cookie"))
        value = cookie.get("helpdesk_session")
        return value.value if value else None

    def read_json(self) -> dict[str, Any]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Content-Length không hợp lệ.") from exc
        if content_length <= 0 or content_length > 100_000:
            raise ValueError("Nội dung yêu cầu không hợp lệ.")
        try:
            return json.loads(self.rfile.read(content_length).decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("JSON không hợp lệ.") from exc

    def serve_static(self, relative: str, content_type: str) -> None:
        file_path = STATIC_DIR / relative
        if not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        raw = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self.serve_static("index.html", "text/html; charset=utf-8")
        elif path == "/static/styles.css":
            self.serve_static("styles.css", "text/css; charset=utf-8")
        elif path == "/static/app.js":
            self.serve_static("app.js", "application/javascript; charset=utf-8")
        elif path == "/api/config":
            session_id, _ = self.app.get_session(self.session_id())
            self.send_json(self.app.config(), session_id=session_id)
        elif path == "/api/options":
            self.send_json(self.app.options())
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self.read_json()
            if path == "/api/chat":
                message = payload.get("message")
                if not isinstance(message, str):
                    raise ValueError("Trường message phải là chuỗi.")
                session_id, response = self.app.chat(self.session_id(), message)
                self.send_json(response, session_id=session_id)
            elif path == "/api/reset":
                session_id, session = self.app.reset(self.session_id())
                self.send_json({
                    "message": "Đã bắt đầu cuộc trò chuyện mới.",
                    "transcript_id": session["transcript"]["transcript_id"],
                    "artifact_version": self.app.artifact.artifact_version,
                }, session_id=session_id)
            elif path == "/api/configure":
                provider, model, version = payload.get("provider"), payload.get("model"), payload.get("version")
                if not all(isinstance(value, str) for value in (provider, model, version)):
                    raise ValueError("Provider, model và version là bắt buộc.")
                session_id, session = self.app.configure(provider, model, version, self.session_id())
                self.send_json({**self.app.config(), "message": "Đã áp dụng cấu hình mới và tạo phiên chat mới.", "transcript_id": session["transcript"]["transcript_id"]}, session_id=session_id)
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Standalone IT Helpdesk web UI")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--version", required=True, help="Artifact version label, for example v3")
    parser.add_argument("--model", default=None)
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--system-prompt", type=Path, default=ROOT / "artifacts" / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ROOT / "artifacts" / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = HelpdeskWebApp(args)
    server = ThreadingHTTPServer((args.host, args.port), RequestHandler)
    server.app = app  # type: ignore[attr-defined]
    print(f"IT Helpdesk UI is running at http://{args.host}:{args.port}")
    print(f"artifact_version={app.artifact.artifact_version}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UI server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
