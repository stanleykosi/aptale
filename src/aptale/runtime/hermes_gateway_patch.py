"""Runtime patch for Hermes gateway Aptale bridge behavior.

This module patches Hermes `gateway.run.GatewayRunner` at process startup
when `APTALE_HERMES_BRIDGE_PATCH=true`.
"""

from __future__ import annotations

import asyncio
import json
import logging
import mimetypes
import os
import re
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping


logger = logging.getLogger(__name__)

_PATCHED_ATTR = "_aptale_bridge_patch_v2"
_TRUE_VALUES = {"1", "true", "yes", "on"}
_TRACK_HS_RE = re.compile(r"\btrack\b", re.IGNORECASE)
_HS_RE = re.compile(r"\bhs\s*[0-9]{4,10}\b", re.IGNORECASE)
_AUDIO_EXT_RE = re.compile(r"\.(ogg|opus|mp3|wav|m4a|aac|webm)(?:\?.*)?$", re.IGNORECASE)


def install_patch() -> None:
    """Install the Hermes gateway patch when enabled by environment."""
    if not _is_truthy(os.getenv("APTALE_HERMES_BRIDGE_PATCH", "")):
        return

    try:
        import gateway.run as gateway_run
    except Exception as exc:  # pragma: no cover - runtime-only path
        logger.debug("Aptale gateway patch skipped; gateway.run import failed: %s", exc)
        return

    apply_patch_to_gateway_module(gateway_run)


def apply_patch_to_gateway_module(gateway_run: ModuleType | Any) -> bool:
    """Patch a gateway.run-like module. Returns True when patched."""
    gateway_runner = getattr(gateway_run, "GatewayRunner", None)
    platform = getattr(gateway_run, "Platform", None)
    message_type = getattr(gateway_run, "MessageType", None)
    if gateway_runner is None or platform is None or message_type is None:
        return False

    if getattr(gateway_runner, _PATCHED_ATTR, False):
        return True

    quote_terms = tuple(getattr(gateway_run, "_APTALE_QUOTE_INTENT_TERMS", ()))
    domain_terms = tuple(getattr(gateway_run, "_APTALE_DOMAIN_INTENT_TERMS", ()))
    hermes_home = getattr(gateway_run, "_hermes_home", Path.home() / ".hermes")

    def _build_aptale_event_payload(
        *,
        event: Any,
        session_key: str,
        session_id: str,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "session_key": session_key,
            "session_id": session_id,
            "chat_id": event.source.chat_id,
            "user_id": event.source.user_id or event.source.chat_id,
            "message_id": event.message_id,
            "text": event.text or "",
            "caption": event.text or "",
        }

        for index, path in enumerate(getattr(event, "media_urls", ()) or ()):
            if not path:
                continue
            media = ""
            media_types = getattr(event, "media_types", ()) or ()
            if index < len(media_types):
                media = str(media_types[index] or "").lower()

            if media:
                is_image = media.startswith("image/")
                is_audio = media.startswith("audio/")
            else:
                is_image = event.message_type == message_type.PHOTO
                is_audio = event.message_type in (message_type.VOICE, message_type.AUDIO)
            if not is_audio and _AUDIO_EXT_RE.search(str(path)):
                is_audio = True
            if is_image and "image" not in payload:
                payload["image"] = path
            if is_audio and "audio" not in payload:
                payload["audio"] = path

        return payload

    def _classify_aptale_intent(self: Any, *, event: Any, session_key: str) -> str:
        if self._event_has_image(event):
            return "quote_loop"
        if _event_has_audio_payload(event=event, message_type=message_type):
            return "quote_loop"

        if self._aptale_quote_store is not None:
            pending = self._aptale_quote_store.get(session_key)
            if pending is not None:
                return "quote_loop"

        raw_text = str(getattr(event, "text", "") or "")
        if _looks_like_trade_radar_intent(raw_text):
            return "quote_loop"

        text = self._normalize_aptale_intent_text(raw_text)
        if not text:
            return "pass"
        if any(term in text for term in quote_terms):
            return "quote_kickoff"
        if any(term in text for term in domain_terms):
            return "domain_assist"
        return "out_of_scope"

    def _format_aptale_dispatch_response(dispatch: Any) -> str:
        message = (getattr(dispatch, "user_message", "") or "").strip()
        lines: list[str] = [message] if message else []

        for attachment in getattr(dispatch, "attachments", ()) or ():
            if not isinstance(attachment, Mapping):
                continue
            path = attachment.get("path")
            if not isinstance(path, str) or not path.strip():
                continue
            if attachment.get("audio_as_voice") is True:
                lines.append("[[audio_as_voice]]")
            lines.append(f"MEDIA:{path.strip()}")

        if not lines:
            return "Aptale quote loop finished with no response payload."
        return "\n".join(lines)

    async def _run_aptale_quote_loop_bridge(
        self: Any,
        *,
        event: Any,
        session_key: str,
        session_id: str,
    ) -> str | None:
        if (
            not self._aptale_quote_enabled
            or self._aptale_quote_adapter is None
            or event.source.platform != platform.WHATSAPP
        ):
            return None

        intent = self._classify_aptale_intent(event=event, session_key=session_key)
        if intent == "quote_kickoff":
            return self._render_aptale_quote_kickoff_message()
        if intent in {"domain_assist", "pass"}:
            return None
        if intent == "out_of_scope":
            scope_enforced = _is_truthy(os.getenv("APTALE_SCOPE_ENFORCE", "false"))
            return self._render_aptale_scope_message() if scope_enforced else None

        quote_relevant = intent == "quote_loop"
        whatsapp_event = self._build_aptale_event_payload(
            event=event,
            session_key=session_key,
            session_id=session_id,
        )
        profile = self._build_aptale_user_profile()
        export_format = os.getenv("APTALE_EXPORT_FORMAT", "pdf").strip().lower() or "pdf"
        output_dir = os.getenv(
            "APTALE_EXPORT_OUTPUT_DIR",
            str((Path(hermes_home) / "runtime" / "exports").resolve()),
        )

        def _prime_session_env() -> None:
            os.environ["HERMES_SESSION_PLATFORM"] = event.source.platform.value
            os.environ["HERMES_SESSION_CHAT_ID"] = str(event.source.chat_id or "")
            chat_name = getattr(event.source, "chat_name", None)
            if isinstance(chat_name, str) and chat_name.strip():
                os.environ["HERMES_SESSION_CHAT_NAME"] = chat_name.strip()
            os.environ["HERMES_SESSION_KEY"] = session_key

        def _voice_transcriber(*, audio_payload: str, context: Mapping[str, Any]) -> str:
            try:
                from tools.transcription_tools import transcribe_audio
            except Exception as exc:  # pragma: no cover - runtime-only path
                logger.warning("Aptale bridge voice transcriber unavailable: %s", exc)
                return ""

            path = str(audio_payload or "").strip()
            if not path:
                return ""
            result = transcribe_audio(path)
            if not bool(result.get("success")):
                try:
                    from aptale.runtime.local_stt import transcribe_audio_local
                except Exception:
                    transcribe_audio_local = None
                if callable(transcribe_audio_local):
                    result = transcribe_audio_local(path)
            if bool(result.get("success")):
                return str(result.get("transcript") or "").strip()
            logger.warning(
                "Aptale bridge voice transcription failed: %s",
                result.get("error", "unknown error"),
            )
            return ""

        def _voice_synthesizer(
            *,
            summary_text: str,
            context: Mapping[str, Any],
        ) -> Mapping[str, Any] | None:
            text = str(summary_text or "").strip()
            if not text:
                return None
            try:
                from tools.tts_tool import text_to_speech_tool
            except Exception as exc:  # pragma: no cover - runtime-only path
                logger.warning("Aptale bridge voice synthesizer unavailable: %s", exc)
                return None

            _prime_session_env()
            raw = text_to_speech_tool(text)
            try:
                payload = json.loads(raw)
            except Exception:
                return None
            if not bool(payload.get("success")):
                return None

            file_path = str(payload.get("file_path") or "").strip()
            if not file_path:
                return None
            mime_type, _ = mimetypes.guess_type(file_path)
            media_tag = str(payload.get("media_tag") or "")
            return {
                "type": "audio",
                "path": file_path,
                "mime_type": mime_type or "audio/mpeg",
                "audio_as_voice": "[[audio_as_voice]]" in media_tag,
            }

        def _schedule_cronjob_proxy(**kwargs: Any) -> Any:
            from tools.cronjob_tools import schedule_cronjob

            _prime_session_env()
            return schedule_cronjob(
                prompt=str(kwargs.get("prompt") or ""),
                schedule=str(kwargs.get("schedule") or ""),
                name=str(kwargs.get("name")).strip() if kwargs.get("name") is not None else None,
                deliver=str(kwargs.get("deliver")).strip()
                if kwargs.get("deliver") is not None
                else None,
            )

        def _run_sync() -> Any:
            return self._aptale_quote_adapter.handle_event(
                whatsapp_event,
                multimodal_extractor=self._aptale_multimodal_extractor,
                delegate_task_runner=lambda tasks: self._aptale_delegate_task_runner(
                    tasks=tasks,
                    session_id=session_id,
                    session_key=session_key,
                ),
                user_profile=profile,
                export_format=export_format,
                output_dir=output_dir,
                voice_transcriber=_voice_transcriber,
                voice_synthesizer=_voice_synthesizer,
                schedule_cronjob=_schedule_cronjob_proxy,
            )

        try:
            dispatch = await asyncio.get_running_loop().run_in_executor(None, _run_sync)
        except Exception as exc:
            logger.exception("Aptale quote-loop bridge failed for session %s", session_key)
            if quote_relevant:
                return (
                    "Aptale quote loop failed before completion.\n"
                    f"Error: {type(exc).__name__}: {exc}\n\n"
                    "Please retry with a clearer invoice image or run `/reset`."
                )
            return None

        if not getattr(dispatch, "handled", False):
            return None
        return self._format_aptale_dispatch_response(dispatch)

    gateway_runner._build_aptale_event_payload = staticmethod(_build_aptale_event_payload)
    gateway_runner._classify_aptale_intent = _classify_aptale_intent
    gateway_runner._format_aptale_dispatch_response = staticmethod(
        _format_aptale_dispatch_response
    )
    gateway_runner._run_aptale_quote_loop_bridge = _run_aptale_quote_loop_bridge
    setattr(gateway_runner, _PATCHED_ATTR, True)
    return True


def _is_truthy(value: str) -> bool:
    return str(value or "").strip().lower() in _TRUE_VALUES


def _looks_like_trade_radar_intent(text: str) -> bool:
    candidate = str(text or "").strip().lower()
    if not candidate:
        return False
    if _TRACK_HS_RE.search(candidate) is None:
        return False
    if _HS_RE.search(candidate) is None:
        return False
    return ("->" in candidate) or (" to " in candidate)


def _event_has_audio_payload(*, event: Any, message_type: Any) -> bool:
    try:
        if getattr(event, "message_type", None) in (message_type.VOICE, message_type.AUDIO):
            return True
    except Exception:
        pass

    raw_media_types = getattr(event, "media_types", ()) or ()
    for media in raw_media_types:
        media_text = str(media or "").lower()
        if media_text.startswith("audio/") or "ptt" in media_text:
            return True

    raw_media_urls = getattr(event, "media_urls", ()) or ()
    for path in raw_media_urls:
        if _AUDIO_EXT_RE.search(str(path or "").strip()):
            return True

    raw_message = getattr(event, "raw_message", None)
    if isinstance(raw_message, Mapping):
        media_type = str(raw_message.get("mediaType") or "").lower()
        if "audio" in media_type or "ptt" in media_type:
            return True
        if bool(raw_message.get("hasMedia")) and _AUDIO_EXT_RE.search(
            str(raw_message.get("mediaUrl") or "")
        ):
            return True
    return False
