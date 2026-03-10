"""Timezone normalization and detection utilities for Aptale."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones


_ALIASES = {
    "utc": "UTC",
    "z": "UTC",
    "gmt": "Etc/GMT",
}

_COUNTRY_DEFAULT_TIMEZONES = {
    "NG": "Africa/Lagos",
    "CN": "Asia/Shanghai",
    "JP": "Asia/Tokyo",
    "IN": "Asia/Kolkata",
    "TR": "Europe/Istanbul",
    "GB": "Europe/London",
    "DE": "Europe/Berlin",
    "FR": "Europe/Paris",
    "AE": "Asia/Dubai",
    "BR": "America/Sao_Paulo",
    "MX": "America/Mexico_City",
    "ZA": "Africa/Johannesburg",
}

_PROFILE_TIMEZONE_KEYS = ("timezone", "local_timezone", "tz", "timezone_hint")
_PROFILE_COUNTRY_KEYS = ("country", "destination_country")


class TimezoneError(ValueError):
    """Base error for timezone detection/normalization failures."""


class TimezoneNormalizationError(TimezoneError):
    """Raised when a timezone value cannot be normalized to IANA."""


class TimezoneDetectionError(TimezoneError):
    """Raised when timezone detection from context fails unexpectedly."""


def normalize_timezone(value: Any) -> str:
    """Normalize timezone input to canonical IANA timezone string."""
    text = str(value).strip()
    if not text:
        raise TimezoneNormalizationError("Timezone value must not be blank.")

    alias = _ALIASES.get(text.casefold())
    if alias is not None:
        _validate_iana(alias)
        return alias

    candidate = _lookup_case_insensitive_iana(text)
    if candidate is None:
        raise TimezoneNormalizationError(
            "Timezone must be a valid IANA timezone string "
            "(example: Africa/Lagos, Asia/Tokyo, Europe/London)."
        )

    _validate_iana(candidate)
    return candidate


def detect_timezone_from_profile(user_profile: Mapping[str, Any]) -> str | None:
    """
    Detect a timezone from user profile context.

    Detection order:
    1) explicit timezone-like keys in user profile
    2) country defaults for non-ambiguous mappings
    """
    if not isinstance(user_profile, Mapping):
        raise TimezoneDetectionError("user_profile must be a mapping.")

    for key in _PROFILE_TIMEZONE_KEYS:
        value = user_profile.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        try:
            return normalize_timezone(text)
        except TimezoneNormalizationError as exc:
            raise TimezoneDetectionError(
                f"Invalid timezone provided in user profile field '{key}'."
            ) from exc

    country = _detect_country_code(user_profile)
    if country is None:
        return None
    return _COUNTRY_DEFAULT_TIMEZONES.get(country)


def _detect_country_code(user_profile: Mapping[str, Any]) -> str | None:
    for key in _PROFILE_COUNTRY_KEYS:
        value = user_profile.get(key)
        if value is None:
            continue
        code = str(value).strip().upper()
        if len(code) == 2 and code.isalpha():
            return code
    return None


@lru_cache(maxsize=1)
def _timezone_casefold_index() -> dict[str, str]:
    return {name.casefold(): name for name in available_timezones()}


def _lookup_case_insensitive_iana(value: str) -> str | None:
    return _timezone_casefold_index().get(value.casefold())


def _validate_iana(value: str) -> None:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise TimezoneNormalizationError(f"Unknown IANA timezone: {value!r}") from exc
