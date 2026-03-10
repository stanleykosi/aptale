"""Timezone capture flow for onboarding and alert scheduling guardrails."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from aptale.memory.profile_updates import (
    ProfileUpdateError,
    ProfileUpdateResult,
    apply_preference_profile_updates,
)
from aptale.memory.timezone import (
    TimezoneDetectionError,
    TimezoneNormalizationError,
    detect_timezone_from_profile,
    normalize_timezone,
)


TIMEZONE_CAPTURE_PROMPT = (
    "Please share your local timezone using an IANA value "
    "(for example: Africa/Lagos, Europe/London, Asia/Tokyo)."
)


class OnboardingTimezoneError(RuntimeError):
    """Raised when onboarding timezone capture flow fails."""


class MissingTimezoneForAlertError(OnboardingTimezoneError):
    """Raised when alert scheduling is attempted without a timezone."""


@dataclass(frozen=True)
class OnboardingTimezoneResult:
    """Result of onboarding timezone capture and persistence."""

    status: str
    timezone: str | None
    requires_user_input: bool
    user_prompt: str | None
    profile_update: ProfileUpdateResult | None


def capture_and_persist_onboarding_timezone(
    user_profile: Mapping[str, Any],
    *,
    timezone_input: str | None = None,
    memory_dir: str | Path | None = None,
) -> OnboardingTimezoneResult:
    """
    Capture timezone during onboarding and persist it to USER.md/MEMORY.md.

    If neither explicit input nor profile detection can resolve a timezone,
    returns a deterministic prompt requesting an IANA timezone from the user.
    """
    if not isinstance(user_profile, Mapping):
        raise OnboardingTimezoneError("user_profile must be a mapping.")

    timezone = _resolve_timezone(user_profile, timezone_input=timezone_input)
    if timezone is None:
        return OnboardingTimezoneResult(
            status="timezone_required",
            timezone=None,
            requires_user_input=True,
            user_prompt=TIMEZONE_CAPTURE_PROMPT,
            profile_update=None,
        )

    payload = _build_preference_payload_for_persistence(user_profile, timezone=timezone)
    try:
        result = apply_preference_profile_updates(payload, memory_dir=memory_dir)
    except ProfileUpdateError as exc:
        raise OnboardingTimezoneError(
            "Timezone captured but could not be persisted; profile payload is incomplete."
        ) from exc

    return OnboardingTimezoneResult(
        status="timezone_captured",
        timezone=timezone,
        requires_user_input=False,
        user_prompt=None,
        profile_update=result,
    )


def ensure_timezone_before_alert_scheduling(
    user_profile: Mapping[str, Any],
    *,
    override_timezone: str | None = None,
) -> str:
    """
    Ensure an alert scheduling request has a normalized timezone.

    Prefers explicit override, then falls back to stored/detected profile data.
    """
    if not isinstance(user_profile, Mapping):
        raise MissingTimezoneForAlertError("user_profile must be a mapping.")

    timezone = _resolve_timezone(user_profile, timezone_input=override_timezone)
    if timezone is None:
        raise MissingTimezoneForAlertError(
            "Timezone is required before scheduling alerts. Capture timezone during onboarding."
        )
    return timezone


def _resolve_timezone(
    user_profile: Mapping[str, Any],
    *,
    timezone_input: str | None,
) -> str | None:
    if timezone_input is not None and str(timezone_input).strip():
        try:
            return normalize_timezone(timezone_input)
        except TimezoneNormalizationError as exc:
            raise OnboardingTimezoneError("Provided timezone is invalid.") from exc

    try:
        return detect_timezone_from_profile(user_profile)
    except TimezoneDetectionError as exc:
        raise OnboardingTimezoneError("Stored timezone value is invalid.") from exc


def _build_preference_payload_for_persistence(
    user_profile: Mapping[str, Any], *, timezone: str
) -> dict[str, Any]:
    return {
        "local_currency": user_profile.get("local_currency"),
        "profit_margin_pct": user_profile.get("profit_margin_pct"),
        "timezone": timezone,
        "preferred_routes": user_profile.get("preferred_routes", []),
    }
