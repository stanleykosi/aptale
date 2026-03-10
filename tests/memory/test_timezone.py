from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.flows.onboarding_timezone import (  # noqa: E402
    MissingTimezoneForAlertError,
    OnboardingTimezoneError,
    capture_and_persist_onboarding_timezone,
    ensure_timezone_before_alert_scheduling,
)
from aptale.memory.timezone import (  # noqa: E402
    TimezoneDetectionError,
    TimezoneNormalizationError,
    detect_timezone_from_profile,
    normalize_timezone,
)


def _base_profile() -> dict:
    return {
        "local_currency": "NGN",
        "profit_margin_pct": 18.5,
        "preferred_routes": [
            {"origin_country": "CN", "destination_country": "NG"},
        ],
    }


def test_normalize_timezone_accepts_case_insensitive_iana_and_aliases() -> None:
    assert normalize_timezone("africa/lagos") == "Africa/Lagos"
    assert normalize_timezone("UTC") == "UTC"
    assert normalize_timezone("utc") == "UTC"


def test_normalize_timezone_rejects_non_iana_values() -> None:
    with pytest.raises(TimezoneNormalizationError):
        normalize_timezone("UTC+1")


def test_detect_timezone_from_profile_prefers_explicit_timezone() -> None:
    profile = _base_profile()
    profile["timezone"] = "asia/tokyo"
    assert detect_timezone_from_profile(profile) == "Asia/Tokyo"


def test_detect_timezone_from_profile_uses_country_default_when_present() -> None:
    profile = _base_profile()
    profile["country"] = "NG"
    assert detect_timezone_from_profile(profile) == "Africa/Lagos"


def test_detect_timezone_from_profile_fails_fast_on_invalid_explicit_timezone() -> None:
    profile = _base_profile()
    profile["timezone"] = "Mars/Phobos"
    with pytest.raises(TimezoneDetectionError):
        detect_timezone_from_profile(profile)


def test_capture_and_persist_onboarding_timezone_requests_input_when_missing(
    tmp_path: Path,
) -> None:
    profile = _base_profile()
    result = capture_and_persist_onboarding_timezone(profile, memory_dir=tmp_path / "memories")

    assert result.status == "timezone_required"
    assert result.requires_user_input is True
    assert result.timezone is None
    assert result.profile_update is None
    assert "IANA" in (result.user_prompt or "")


def test_capture_and_persist_onboarding_timezone_persists_normalized_timezone(
    tmp_path: Path,
) -> None:
    profile = _base_profile()
    result = capture_and_persist_onboarding_timezone(
        profile,
        timezone_input="africa/lagos",
        memory_dir=tmp_path / "memories",
    )

    assert result.status == "timezone_captured"
    assert result.timezone == "Africa/Lagos"
    assert result.profile_update is not None
    assert result.profile_update.user_path.is_file()
    assert result.profile_update.memory_path.is_file()

    user_text = result.profile_update.user_path.read_text(encoding="utf-8")
    assert "`Africa/Lagos`" in user_text


def test_capture_and_persist_onboarding_timezone_fails_on_invalid_input(
    tmp_path: Path,
) -> None:
    profile = _base_profile()
    with pytest.raises(OnboardingTimezoneError):
        capture_and_persist_onboarding_timezone(
            profile,
            timezone_input="UTC+1",
            memory_dir=tmp_path / "memories",
        )


def test_ensure_timezone_before_alert_scheduling_uses_override_then_profile() -> None:
    profile = _base_profile()
    profile["timezone"] = "Asia/Tokyo"

    assert (
        ensure_timezone_before_alert_scheduling(profile, override_timezone="Europe/London")
        == "Europe/London"
    )
    assert ensure_timezone_before_alert_scheduling(profile) == "Asia/Tokyo"


def test_ensure_timezone_before_alert_scheduling_fails_without_timezone() -> None:
    with pytest.raises(MissingTimezoneForAlertError):
        ensure_timezone_before_alert_scheduling(_base_profile())
