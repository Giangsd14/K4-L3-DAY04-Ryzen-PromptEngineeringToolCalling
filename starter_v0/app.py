"""Streamlit UI for the Northstar Labs IT Helpdesk agent.

Run from ``starter_v0`` with: ``streamlit run app.py``.
The UI deliberately reuses the production tool loop in ``chat.py`` so the
visible trace, saved transcript, and command-line behaviour use the same tools.
"""

from __future__ import annotations

import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"
TRANSCRIPTS = ROOT / "transcripts"
VERSION_OPTIONS = ("v0", "v1", "v2", "v3")
PROVIDER_KEY_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

# Keys are redacted recursively; patterns also catch credentials embedded in text.
SENSITIVE_KEY = re.compile(r"(?:pass(?:word|wd)?|token|api[_ -]?key|secret|otp|mfa|recovery[_ -]?code)", re.I)
SENSITIVE_VALUE = re.compile(
    r"(?i)\b(password|passwd|token|api[ _-]?key|secret|otp|mfa|recovery[ _-]?code)"
    r"\s*([:=]|is|là)\s*([^\s,;]+)"
)
MASK = "[REDACTED]"


def redact(value: Any, *, key: str = "") -> Any:
    """Return a display/storage-safe copy without mutating tool output."""
    if SENSITIVE_KEY.search(key):
        return MASK
    if isinstance(value, dict):
        return {str(k): redact(v, key=str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return SENSITIVE_VALUE.sub(lambda match: f"{match.group(1)}={MASK}", value)
    return value


def configured_providers() -> list[str]:
    return [name for name, env_key in PROVIDER_KEY_ENV.items() if os.getenv(env_key)]


def write_transcript() -> None:
    """Persist after every completed message; transcript contains redacted data only."""
    transcript = st.session_state.transcript
    transcript["timestamp"] = now_iso()
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    st.session_state.transcript_path.write_text(
        json.dumps(redact(transcript), ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )


def start_session(version: str, provider_name: str, model: str | None) -> None:
    prompt_path = ARTIFACTS / "system_prompt.md"
    tools_path = ARTIFACTS / "tools.yaml"
    artifact = build_artifact_version(version, prompt_path, tools_path)
    session_id = secrets.token_urlsafe(18)
    created_at = now_iso()
    filename = f"{safe_slug(version)}_{safe_slug(provider_name)}_{datetime.now().strftime('%Y%m%dT%H%M%S%f')}.transcript.json"
    st.session_state.update(
        agent_config={
            "version": version,
            "provider_name": provider_name,
            "model": model,
            "system_prompt": prompt_path.read_text(encoding="utf-8"),
            "tools": to_openai_tools(load_tool_declarations(tools_path)),
            "artifact": artifact,
        },
        history=[],
        ui_messages=[],
        transcript_path=TRANSCRIPTS / filename,
        transcript={
            "session_id": session_id,
            "version": version,
            "timestamp": created_at,
            "created_at": created_at,
            "provider": provider_name,
            "model": model,
            "artifact": artifact_version_dict(artifact),
            "messages": [],
        },
    )
    write_transcript()


def show_trace(tool_events: list[dict[str, Any]], error_logs: list[str]) -> None:
    for index, event in enumerate(tool_events, start=1):
        tool_name = event.get("tool", "unknown_tool")
        with st.expander(f"Tool trace {index}: {tool_name}", expanded=False):
            st.caption("Tool input / arguments")
            st.json(redact(event.get("args", {})))
            st.caption("Tool output / result")
            # An error is intentionally rendered as JSON too—never suppressed.
            st.json(redact(event.get("result", event)))
    for error in error_logs:
        st.error(redact(error))


def render_conversation() -> None:
    for message in st.session_state.get("ui_messages", []):
        with st.chat_message(message["role"]):
            st.markdown(redact(message["content"]))
            if message["role"] == "assistant":
                show_trace(message.get("tool_results", []), message.get("error_logs", []))


def process_message(raw_user_text: str) -> None:
    user_text = redact(raw_user_text)
    st.session_state.ui_messages.append({"role": "user", "content": user_text})
    config = st.session_state.agent_config
    transcript_message: dict[str, Any] = {
        "turn": len(st.session_state.transcript["messages"]) + 1,
        "timestamp": now_iso(),
        "user_input": user_text,
        "assistant_text": "",
        "tool_calls": [],
        "tool_results": [],
        "error_logs": [],
    }

    try:
        provider = make_provider(config["provider_name"])
        messages = [
            {"role": "system", "content": config["system_prompt"]},
            *trim_history(st.session_state.history, 5),
            {"role": "user", "content": user_text},
        ]
        outcome = run_model_tool_loop(
            provider=provider, messages=messages, tools=config["tools"],
            model=config["model"], max_tool_rounds=4,
        )
        assistant_text = redact(outcome["assistant_text"])
        tool_events = redact(outcome["tool_events"])
        transcript_message.update({
            "assistant_text": assistant_text,
            "status": outcome["status"],
            "tool_calls": [
                {"name": event.get("tool"), "arguments": event.get("args", {})} for event in tool_events
            ],
            "tool_results": tool_events,
        })
        st.session_state.history.extend((
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_text},
        ))
    except Exception as exc:
        # Preserve the failure as evidence, but redact it before display/storage.
        assistant_text = "Không thể hoàn tất yêu cầu. Hãy xem error log bên dưới và kiểm tra cấu hình provider."
        tool_events = []
        transcript_message["error_logs"] = [redact(f"{type(exc).__name__}: {exc}")]
        transcript_message["status"] = "provider_or_runtime_error"
        transcript_message["assistant_text"] = assistant_text

    st.session_state.ui_messages.append({
        "role": "assistant", "content": assistant_text,
        "tool_results": tool_events, "error_logs": transcript_message["error_logs"],
    })
    st.session_state.transcript["messages"].append(transcript_message)
    write_transcript()


def main() -> None:
    st.set_page_config(page_title="Northstar Labs IT Helpdesk", page_icon="🛠️", layout="wide")
    load_lab_env(ROOT)
    st.title("🛠️ Northstar Labs — AI IT Helpdesk")
    st.caption("Tool calls and their real results are shown below each assistant response. Sensitive values are redacted.")

    available = configured_providers()
    if not available:
        st.error("Không tìm thấy API key. Sao chép .env.example thành .env và cấu hình ít nhất một provider.")
        st.stop()

    with st.sidebar:
        st.header("Phiên làm việc")
        version = st.selectbox("Version", VERSION_OPTIONS, index=3)
        provider_name = st.selectbox("Provider", available)
        default_model = getattr(make_provider(provider_name), "default_model", None)
        model = st.text_input("Model (để trống dùng mặc định)", value=default_model or "") or None
        st.caption("Đổi Version/Provider/Model sẽ tạo phiên chat mới để không lẫn transcript.")
        signature = (version, provider_name, model)
        if "configuration_signature" not in st.session_state or st.session_state.configuration_signature != signature:
            start_session(version, provider_name, model)
            st.session_state.configuration_signature = signature
        if st.button("Cuộc trò chuyện mới", use_container_width=True):
            start_session(version, provider_name, model)
        st.divider()
        artifact = st.session_state.agent_config["artifact"]
        st.write(f"**Version:** `{artifact.version}`")
        st.caption(f"Artifact: `{artifact.artifact_version}`")
        st.caption(f"Transcript: `{st.session_state.transcript_path.name}`")

    render_conversation()
    if user_text := st.chat_input("Ví dụ: Kiểm tra VPN trên LT-204"):
        process_message(user_text)
        st.rerun()


if __name__ == "__main__":
    main()
