from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.errors.user_messages import (  # noqa: E402
    UserMessageCode,
    UserMessageError,
    render_user_message,
)


def test_portal_outage_message_includes_open_web_recovery() -> None:
    text = render_user_message(UserMessageCode.PORTAL_OUTAGE)
    assert "*Sourcing Blocked*" in text
    assert "portal is currently offline or unavailable" in text
    assert "No estimate was guessed." in text
    assert "Switch this leg to open-web search now." in text
    assert "Retry official portal sourcing later." in text


def test_persistent_captcha_message_includes_retry_steps() -> None:
    text = render_user_message(UserMessageCode.PERSISTENT_CAPTCHA)
    assert "persistent CAPTCHA challenge" in text
    assert "*What You Can Do Next*" in text
    assert "open-web search" in text


def test_unsupported_route_message_requests_explicit_route_inputs() -> None:
    text = render_user_message(UserMessageCode.UNSUPPORTED_ROUTE)
    assert "*Route Unsupported*" in text
    assert "origin/destination countries and ports" in text
    assert "source hints" in text


def test_missing_fx_sources_message_requests_currency_pair_and_market_type() -> None:
    text = render_user_message(UserMessageCode.MISSING_FX_SOURCES)
    assert "*FX Sourcing Blocked*" in text
    assert "USD/NGN" in text
    assert "official rate, parallel rate, or both" in text


def test_export_generation_failure_message_offers_inline_fallback() -> None:
    text = render_user_message(UserMessageCode.EXPORT_GENERATION_FAILURE)
    assert "*Export Failed*" in text
    assert "Retry export as CSV or PDF." in text
    assert "inline in WhatsApp" in text


def test_whatsapp_attachment_failure_message_offers_retry() -> None:
    text = render_user_message(UserMessageCode.WHATSAPP_ATTACHMENT_FAILURE)
    assert "*Delivery Failed*" in text
    assert "attachment delivery failed" in text
    assert "Retry attachment delivery now." in text


def test_render_user_message_accepts_string_code_and_detail() -> None:
    text = render_user_message(
        "portal_outage",
        detail="503  service unavailable   from customs portal",
    )
    assert "*Observed Detail*" in text
    assert "503 service unavailable from customs portal" in text


def test_render_user_message_fails_on_unknown_code() -> None:
    with pytest.raises(UserMessageError):
        render_user_message("temporary_network_glitch")
