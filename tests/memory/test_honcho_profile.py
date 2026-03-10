from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.memory.honcho_profile import (  # noqa: E402
    HonchoProfileError,
    build_adaptive_profile,
    build_honcho_query,
    extract_operational_settings,
    load_honcho_query_prompt,
)


PROMPT_PATH = ROOT / "src" / "aptale" / "prompts" / "honcho_query.md"


def _user_profile() -> dict:
    return {
        "local_currency": "NGN",
        "profit_margin_pct": 18.5,
        "timezone": "Africa/Lagos",
        "preferred_routes": [
            {"origin_country": "CN", "destination_country": "NG"},
        ],
        "communication_style_preference": "detailed",
    }


def test_honcho_prompt_file_contract() -> None:
    assert PROMPT_PATH.is_file()
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "query_user_context" in content
    assert "Operational settings remain canonical in USER.md" in content
    assert "local currency" in content
    assert "default profit margin" in content
    assert "timezone" in content


def test_build_honcho_query_includes_prompt_guidance_and_user_message() -> None:
    query = build_honcho_query("Give me a fast quote summary.")
    assert "query_user_context" in query
    assert "Current user request:" in query
    assert "Give me a fast quote summary." in query


def test_build_adaptive_profile_uses_honcho_for_style_and_business_context_only() -> None:
    def fake_query_user_context(*, query: str):
        assert "Current user request:" in query
        return {
            "context": (
                "User prefers concise replies. Priority is reducing freight volatility "
                "for electronics import lanes from China to Nigeria."
            )
        }

    profile = build_adaptive_profile(
        user_profile=_user_profile(),
        user_message="Should I wait for better freight rates?",
        query_user_context=fake_query_user_context,
    )

    assert profile.communication_style == "concise"
    assert profile.brevity_preference == "short"
    assert profile.operational_settings.local_currency == "NGN"
    assert profile.operational_settings.profit_margin_display == "18.50"
    assert profile.operational_settings.timezone == "Africa/Lagos"
    assert profile.business_context_signals
    assert "freight volatility" in " ".join(profile.business_context_signals).lower()
    assert profile.honcho_summary is not None


def test_build_adaptive_profile_without_honcho_tool_uses_user_profile_defaults() -> None:
    profile = build_adaptive_profile(
        user_profile=_user_profile(),
        user_message="Need landed cost now.",
        query_user_context=None,
    )

    assert profile.communication_style == "detailed"
    assert profile.brevity_preference == "long"
    assert profile.business_context_signals == tuple()
    assert profile.honcho_query is None
    assert profile.honcho_summary is None


def test_build_adaptive_profile_fails_on_invalid_honcho_response_shape() -> None:
    def fake_query_user_context(*, query: str):
        _ = query
        return {"unknown": "field"}

    with pytest.raises(HonchoProfileError):
        build_adaptive_profile(
            user_profile=_user_profile(),
            user_message="Any update?",
            query_user_context=fake_query_user_context,
        )


def test_extract_operational_settings_fails_when_required_user_settings_missing() -> None:
    bad_profile = {"profit_margin_pct": 12, "timezone": "Africa/Lagos"}
    with pytest.raises(HonchoProfileError):
        extract_operational_settings(bad_profile)


def test_load_honcho_query_prompt_is_non_empty() -> None:
    assert load_honcho_query_prompt()
