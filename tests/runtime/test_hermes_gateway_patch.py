from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
import sys

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.runtime.hermes_gateway_patch import apply_patch_to_gateway_module  # noqa: E402


class _Platform(Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class _MessageType(Enum):
    TEXT = "text"
    PHOTO = "photo"
    AUDIO = "audio"
    VOICE = "voice"


@dataclass
class _Source:
    platform: _Platform
    chat_id: str
    user_id: str
    chat_name: str | None = None


@dataclass
class _Event:
    text: str
    source: _Source
    message_type: _MessageType
    media_urls: list[str]
    media_types: list[str]
    message_id: str = "msg-1"
    raw_message: dict[str, Any] | None = None


@dataclass
class _Dispatch:
    handled: bool
    user_message: str
    attachments: tuple[dict[str, Any], ...] = ()


class _FakeAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def handle_event(self, whatsapp_event: dict[str, Any], **kwargs: Any) -> _Dispatch:
        self.calls.append({"event": whatsapp_event, "kwargs": kwargs})
        return _Dispatch(
            handled=True,
            user_message="*Trade Radar Scheduled*",
            attachments=(
                {"type": "audio", "path": "/tmp/summary.mp3", "audio_as_voice": True},
            ),
        )


class _FakeRunner:
    def __init__(self) -> None:
        self._aptale_quote_enabled = True
        self._aptale_quote_adapter = _FakeAdapter()
        self._aptale_quote_store = None

    @staticmethod
    def _event_has_image(event: _Event) -> bool:
        return event.message_type == _MessageType.PHOTO

    @staticmethod
    def _normalize_aptale_intent_text(text: str) -> str:
        return " ".join(str(text).strip().lower().split())

    @staticmethod
    def _render_aptale_quote_kickoff_message() -> str:
        return "kickoff"

    @staticmethod
    def _render_aptale_scope_message() -> str:
        return "scope"

    @staticmethod
    def _apply_aptale_branding(text: str) -> str:
        return text

    @staticmethod
    def _build_aptale_user_profile() -> dict[str, Any]:
        return {
            "country": "NG",
            "local_currency": "NGN",
            "profit_margin_pct": 18.0,
            "timezone": "Africa/Lagos",
        }

    @staticmethod
    def _aptale_multimodal_extractor(**kwargs: Any) -> dict[str, Any]:
        return {}

    @staticmethod
    def _aptale_delegate_task_runner(**kwargs: Any) -> dict[str, str]:
        return {}


def _fake_gateway_module() -> Any:
    return SimpleNamespace(
        GatewayRunner=_FakeRunner,
        Platform=_Platform,
        MessageType=_MessageType,
        _hermes_home=Path("/tmp/hermes"),
        _APTALE_QUOTE_INTENT_TERMS=("quote",),
        _APTALE_DOMAIN_INTENT_TERMS=("shipping", "customs", "hs code"),
    )


def test_apply_patch_updates_intent_classification_for_trade_radar() -> None:
    module = _fake_gateway_module()
    assert apply_patch_to_gateway_module(module) is True

    runner = module.GatewayRunner()
    event = _Event(
        text="Track HS 850440 China->Nigeria, alert me daily 8am",
        source=_Source(
            platform=_Platform.WHATSAPP,
            chat_id="2348011111111@s.whatsapp.net",
            user_id="2348011111111@s.whatsapp.net",
        ),
        message_type=_MessageType.TEXT,
        media_urls=[],
        media_types=[],
    )

    intent = runner._classify_aptale_intent(event=event, session_key="sess-1")
    assert intent == "quote_loop"


def test_apply_patch_routes_voice_messages_to_quote_loop() -> None:
    module = _fake_gateway_module()
    assert apply_patch_to_gateway_module(module) is True

    runner = module.GatewayRunner()
    event = _Event(
        text="",
        source=_Source(
            platform=_Platform.WHATSAPP,
            chat_id="2348011111111@s.whatsapp.net",
            user_id="2348011111111@s.whatsapp.net",
        ),
        message_type=_MessageType.VOICE,
        media_urls=["/tmp/voice.ogg"],
        media_types=["audio/ogg"],
    )

    intent = runner._classify_aptale_intent(event=event, session_key="sess-1")
    assert intent == "quote_loop"


def test_apply_patch_routes_audio_media_even_when_message_type_is_text() -> None:
    module = _fake_gateway_module()
    assert apply_patch_to_gateway_module(module) is True

    runner = module.GatewayRunner()
    event = _Event(
        text="",
        source=_Source(
            platform=_Platform.WHATSAPP,
            chat_id="2348011111111@s.whatsapp.net",
            user_id="2348011111111@s.whatsapp.net",
        ),
        message_type=_MessageType.TEXT,
        media_urls=["/tmp/voice.ogg"],
        media_types=["unknown"],
        raw_message={"hasMedia": True, "mediaType": "ptt"},
    )

    intent = runner._classify_aptale_intent(event=event, session_key="sess-1")
    assert intent == "quote_loop"


def test_apply_patch_builds_event_payload_with_image_and_audio() -> None:
    module = _fake_gateway_module()
    apply_patch_to_gateway_module(module)
    runner = module.GatewayRunner()

    event = _Event(
        text="voice follow-up",
        source=_Source(
            platform=_Platform.WHATSAPP,
            chat_id="chat-1",
            user_id="user-1",
        ),
        message_type=_MessageType.VOICE,
        media_urls=["/tmp/invoice.png", "/tmp/voice.ogg"],
        media_types=["image/png", "audio/ogg"],
    )

    payload = runner._build_aptale_event_payload(event=event, session_key="s", session_id="id")
    assert payload["image"] == "/tmp/invoice.png"
    assert payload["audio"] == "/tmp/voice.ogg"


def test_apply_patch_builds_event_payload_with_audio_extension_fallback() -> None:
    module = _fake_gateway_module()
    apply_patch_to_gateway_module(module)
    runner = module.GatewayRunner()

    event = _Event(
        text="",
        source=_Source(
            platform=_Platform.WHATSAPP,
            chat_id="chat-1",
            user_id="user-1",
        ),
        message_type=_MessageType.TEXT,
        media_urls=["/tmp/voice.ogg"],
        media_types=["unknown"],
    )

    payload = runner._build_aptale_event_payload(event=event, session_key="s", session_id="id")
    assert payload["audio"] == "/tmp/voice.ogg"


def test_apply_patch_formats_voice_media_tag() -> None:
    module = _fake_gateway_module()
    apply_patch_to_gateway_module(module)
    runner = module.GatewayRunner()

    text = runner._format_aptale_dispatch_response(
        _Dispatch(
            handled=True,
            user_message="done",
            attachments=(
                {"type": "audio", "path": "/tmp/a.ogg", "audio_as_voice": True},
            ),
        )
    )
    assert "[[audio_as_voice]]" in text
    assert "MEDIA:/tmp/a.ogg" in text


def test_apply_patch_run_bridge_passes_new_callbacks() -> None:
    module = _fake_gateway_module()
    apply_patch_to_gateway_module(module)
    runner = module.GatewayRunner()
    event = _Event(
        text="Track HS 850440 China->Nigeria, alert me daily 8am",
        source=_Source(
            platform=_Platform.WHATSAPP,
            chat_id="2348011111111@s.whatsapp.net",
            user_id="2348011111111@s.whatsapp.net",
            chat_name="Tester",
        ),
        message_type=_MessageType.TEXT,
        media_urls=[],
        media_types=[],
    )

    response = asyncio.run(
        runner._run_aptale_quote_loop_bridge(
            event=event,
            session_key="sess-1",
            session_id="session-1",
        )
    )
    assert response is not None
    assert "Trade Radar Scheduled" in response
    assert "MEDIA:/tmp/summary.mp3" in response

    call = runner._aptale_quote_adapter.calls[0]
    kwargs = call["kwargs"]
    assert callable(kwargs["voice_transcriber"])
    assert callable(kwargs["voice_synthesizer"])
    assert callable(kwargs["schedule_cronjob"])
