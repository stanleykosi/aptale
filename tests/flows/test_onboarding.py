from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.flows.onboarding import (  # noqa: E402
    OnboardingError,
    begin_onboarding,
    process_onboarding_response,
)


PROMPT_PATH = ROOT / "src" / "aptale" / "prompts" / "onboarding.md"


def test_onboarding_prompt_contract() -> None:
    assert PROMPT_PATH.is_file()
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "Ask one field at a time" in content
    assert "timezone (IANA)" in content
    assert "WhatsApp" in content


def test_begin_onboarding_requests_first_field_with_whatsapp_markdown() -> None:
    state = begin_onboarding()
    assert state.status == "awaiting_input"
    assert state.channel == "whatsapp"
    assert state.pending_field == "local_currency"
    assert state.can_proceed is False
    assert "*Onboarding Setup*" in state.message_markdown
    assert "*Step 1 of 6*" in state.message_markdown


def test_process_onboarding_response_collects_all_fields_and_persists_timezone(
    tmp_path: Path,
) -> None:
    state = begin_onboarding()
    state = process_onboarding_response(state, "ngn", memory_dir=tmp_path / "memories")
    assert state.pending_field == "destination_country"

    state = process_onboarding_response(state, "Nigeria", memory_dir=tmp_path / "memories")
    assert state.pending_field == "common_lanes"

    state = process_onboarding_response(
        state, "CN->NG, TR->NG", memory_dir=tmp_path / "memories"
    )
    assert state.pending_field == "profit_margin_pct"

    state = process_onboarding_response(state, "18.5", memory_dir=tmp_path / "memories")
    assert state.pending_field == "timezone"

    state = process_onboarding_response(
        state, "Africa/Lagos", memory_dir=tmp_path / "memories"
    )
    assert state.pending_field == "communication_style_preference"

    state = process_onboarding_response(state, "concise", memory_dir=tmp_path / "memories")
    assert state.status == "completed"
    assert state.pending_field is None
    assert state.can_proceed is True
    assert "*Onboarding Complete*" in state.message_markdown
    assert "CN->NG, TR->NG" in state.message_markdown

    user_path = tmp_path / "memories" / "USER.md"
    memory_path = tmp_path / "memories" / "MEMORY.md"
    assert user_path.is_file()
    assert memory_path.is_file()
    assert "`Africa/Lagos`" in user_path.read_text(encoding="utf-8")


def test_process_onboarding_response_fails_fast_on_invalid_timezone(
    tmp_path: Path,
) -> None:
    state = begin_onboarding(
        {
            "local_currency": "NGN",
            "destination_country": "NG",
            "common_lanes": [{"origin_country": "CN", "destination_country": "NG"}],
            "profit_margin_pct": "15",
        }
    )
    assert state.pending_field == "timezone"
    with pytest.raises(OnboardingError):
        process_onboarding_response(state, "UTC+1", memory_dir=tmp_path / "memories")


def test_process_onboarding_response_fails_fast_on_invalid_style(
    tmp_path: Path,
) -> None:
    state = begin_onboarding(
        {
            "local_currency": "NGN",
            "destination_country": "NG",
            "common_lanes": [{"origin_country": "CN", "destination_country": "NG"}],
            "profit_margin_pct": "15",
            "timezone": "Africa/Lagos",
        }
    )
    assert state.pending_field == "communication_style_preference"
    with pytest.raises(OnboardingError):
        process_onboarding_response(state, "normal", memory_dir=tmp_path / "memories")
