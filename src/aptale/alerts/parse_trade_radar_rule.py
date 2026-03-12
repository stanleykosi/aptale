"""Parser for explicit HS-lane trade radar scheduling requests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Callable
from uuid import uuid4

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError
from aptale.contracts.normalize import normalize_hs_code
from aptale.memory.timezone import normalize_timezone


_COUNTRY_ALIASES: dict[str, str] = {
    "cn": "CN",
    "china": "CN",
    "ng": "NG",
    "nigeria": "NG",
    "tr": "TR",
    "turkey": "TR",
    "turkiye": "TR",
    "us": "US",
    "usa": "US",
    "united states": "US",
    "gb": "GB",
    "uk": "GB",
    "united kingdom": "GB",
}

_TRACK_RE = re.compile(
    r"track\s+hs\s*(?P<hs>[0-9.\- ]{4,18})\s+(?P<origin>[A-Za-z .'-]+?)\s*(?:->|to)\s*(?P<dest>[A-Za-z .'-]+)",
    re.IGNORECASE,
)
_TIME_AT_RE = re.compile(r"\bat\s+(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<ampm>am|pm)?\b", re.IGNORECASE)
_TIMEZONE_IANA_RE = re.compile(r"\b[A-Za-z_]+/[A-Za-z0-9_+\-]+(?:/[A-Za-z0-9_+\-]+)?\b")


class TradeRadarRuleParseError(ValueError):
    """Raised when a trade radar request cannot be parsed safely."""


@dataclass(frozen=True)
class TradeRadarRuleParseResult:
    """Parsed trade radar rule output."""

    trade_radar_rule: dict[str, Any]
    timezone: str


def parse_trade_radar_rule_request(
    request_text: str,
    *,
    user_id: str,
    default_timezone: str | None = None,
    now_fn: Callable[[], datetime] | None = None,
    alert_id_factory: Callable[[], str] | None = None,
) -> TradeRadarRuleParseResult:
    text = str(request_text).strip()
    if not text:
        raise TradeRadarRuleParseError("request_text must not be blank.")
    normalized_user_id = str(user_id).strip()
    if not normalized_user_id:
        raise TradeRadarRuleParseError("user_id must not be blank.")

    match = _TRACK_RE.search(text)
    if not match:
        raise TradeRadarRuleParseError(
            "Trade radar requests must use explicit phrasing like: "
            "Track HS 850440 China->Nigeria, alert me daily 8am."
        )

    hs_code = normalize_hs_code(match.group("hs"))
    origin = _resolve_country(match.group("origin"))
    destination = _resolve_country(match.group("dest"))
    if origin is None or destination is None:
        raise TradeRadarRuleParseError("Could not resolve origin/destination countries from request.")

    schedule = _parse_schedule_cron(text)
    timezone_value = _parse_timezone(text, default_timezone=default_timezone)
    now = now_fn() if now_fn is not None else datetime.now(timezone.utc)
    alert_id = (
        str(alert_id_factory()).strip() if alert_id_factory is not None else f"trdr_{uuid4().hex[:12]}"
    )
    if not alert_id:
        raise TradeRadarRuleParseError("alert_id must not be blank.")

    payload = {
        "schema_version": "1.0",
        "alert_id": alert_id,
        "user_id": normalized_user_id,
        "hs_code": hs_code,
        "origin_country": origin,
        "destination_country": destination,
        "schedule_cron": schedule,
        "timezone": timezone_value,
        "deliver": "origin",
        "active": True,
        "created_at": _utc_iso(now),
    }

    try:
        validated = normalize_and_validate_payload("trade_radar_rule", payload)
    except ContractsError as exc:
        raise TradeRadarRuleParseError(
            "Parsed trade radar rule failed schema validation."
        ) from exc

    return TradeRadarRuleParseResult(
        trade_radar_rule=validated,
        timezone=timezone_value,
    )


def _parse_schedule_cron(text: str) -> str:
    lowered = text.lower()
    if "daily" in lowered or "every day" in lowered:
        hour, minute = _parse_hour_minute(text, default_hour=8, default_minute=0)
        return f"{minute} {hour} * * *"
    return "0 8 * * *"


def _parse_hour_minute(text: str, *, default_hour: int, default_minute: int) -> tuple[int, int]:
    match = _TIME_AT_RE.search(text)
    if not match:
        return default_hour, default_minute

    hour = int(match.group("hour"))
    minute = int(match.group("minute") or "0")
    ampm = (match.group("ampm") or "").lower()
    if ampm:
        if hour < 1 or hour > 12:
            raise TradeRadarRuleParseError("Hour with am/pm must be between 1 and 12.")
        if ampm == "am":
            hour = 0 if hour == 12 else hour
        else:
            hour = 12 if hour == 12 else hour + 12
    else:
        if hour < 0 or hour > 23:
            raise TradeRadarRuleParseError("24-hour hour must be between 0 and 23.")

    if minute < 0 or minute > 59:
        raise TradeRadarRuleParseError("Minute must be between 0 and 59.")
    return hour, minute


def _parse_timezone(text: str, *, default_timezone: str | None) -> str:
    for candidate in _TIMEZONE_IANA_RE.findall(text):
        try:
            return normalize_timezone(candidate)
        except Exception:
            continue
    if default_timezone:
        try:
            return normalize_timezone(default_timezone)
        except Exception as exc:
            raise TradeRadarRuleParseError("default_timezone is invalid.") from exc
    raise TradeRadarRuleParseError("Timezone is required for trade radar scheduling.")


def _resolve_country(raw: str) -> str | None:
    normalized = " ".join(str(raw).strip().lower().split())
    if not normalized:
        return None
    if normalized in _COUNTRY_ALIASES:
        return _COUNTRY_ALIASES[normalized]

    for alias, code in sorted(_COUNTRY_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in normalized:
            return code
    if len(normalized) == 2 and normalized.isalpha():
        return normalized.upper()
    return None


def _utc_iso(value: datetime) -> str:
    dt = value
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
