"""Alert-rule parsing for natural-language threshold scheduling requests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
import re
from typing import Any, Callable, Mapping
from uuid import uuid4

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError
from aptale.contracts.normalize import normalize_currency
from aptale.memory.timezone import (
    TimezoneNormalizationError,
    normalize_timezone,
)


DEFAULT_SCHEDULE_CRON = "0 8 * * *"
_VALID_DELIVER_TARGETS = frozenset(
    {"origin", "whatsapp", "telegram", "discord", "slack", "local"}
)
_CRON_FIELD_RE = re.compile(r"^[\d*/,\-]+$")
_TIMEZONE_IANA_RE = re.compile(r"\b[A-Za-z_]+/[A-Za-z0-9_+\-]+(?:/[A-Za-z0-9_+\-]+)?\b")
_CURRENCY_PAIR_RE = re.compile(r"\b([A-Za-z]{3})\s*/\s*([A-Za-z]{3})\b")
_CURRENCY_TO_RE = re.compile(r"\b([A-Za-z]{3})\s+to\s+([A-Za-z]{3})\b", re.IGNORECASE)
_FROM_TO_COUNTRY_RE = re.compile(
    r"\bfrom\s+([A-Za-z .'\-]+?)\s+(?:to|->)\s+([A-Za-z .'\-]+?)(?:$|[,.]| every| at| on| timezone| deliver)",
    re.IGNORECASE,
)
_TIME_AT_RE = re.compile(
    r"\bat\s+(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<ampm>am|pm)?\b",
    re.IGNORECASE,
)

_COUNTRY_ALIASES: dict[str, str] = {
    "cn": "CN",
    "china": "CN",
    "prc": "CN",
    "ng": "NG",
    "nigeria": "NG",
    "tr": "TR",
    "turkey": "TR",
    "turkiye": "TR",
    "us": "US",
    "usa": "US",
    "united states": "US",
    "ru": "RU",
    "russia": "RU",
    "jp": "JP",
    "japan": "JP",
    "gb": "GB",
    "uk": "GB",
    "united kingdom": "GB",
    "de": "DE",
    "germany": "DE",
    "fr": "FR",
    "france": "FR",
}


class AlertRuleParseError(ValueError):
    """Raised when natural-language alert requests cannot be parsed safely."""


@dataclass(frozen=True)
class AlertRuleParseResult:
    """Parsed alert rule plus resolved timezone context."""

    alert_rule: dict[str, Any]
    timezone: str
    monitored_dimension: str
    comparison_operator: str
    threshold: float
    schedule_cron: str
    deliver: str


def parse_alert_rule_request(
    request_text: str,
    *,
    user_id: str,
    default_timezone: str | None = None,
    default_deliver: str = "origin",
    default_base_currency: str | None = None,
    default_quote_currency: str | None = None,
    now_fn: Callable[[], datetime] | None = None,
    alert_id_factory: Callable[[], str] | None = None,
) -> AlertRuleParseResult:
    """
    Parse a natural-language threshold request into a validated alert rule payload.

    This parser extracts:
    - monitored dimension (`metric`)
    - comparison operator (`condition`)
    - threshold
    - schedule (`schedule_cron`)
    - timezone (returned in `AlertRuleParseResult`)
    - delivery target (`deliver`)
    """
    text = _require_non_blank(request_text, name="request_text")
    normalized_user_id = _require_non_blank(user_id, name="user_id")

    metric = _parse_metric(text)
    condition, threshold = _parse_condition_and_threshold(text)
    schedule_cron = _parse_schedule_cron(text)
    timezone = _parse_timezone(text, default_timezone=default_timezone)
    deliver = _parse_deliver_target(text, default_deliver=default_deliver)
    base_currency, quote_currency = _parse_currencies(
        text,
        metric=metric,
        default_base_currency=default_base_currency,
        default_quote_currency=default_quote_currency,
    )
    route = _parse_route(text) if metric in {"freight_quote_amount", "landed_cost_total"} else None

    now = now_fn() if now_fn is not None else datetime.now(dt_timezone.utc)
    alert_id = (
        _require_non_blank(alert_id_factory(), name="alert_id")
        if alert_id_factory is not None
        else f"alrt_{uuid4().hex[:12]}"
    )

    payload = {
        "schema_version": "1.0",
        "alert_id": alert_id,
        "user_id": normalized_user_id,
        "active": True,
        "metric": metric,
        "condition": condition,
        "threshold": threshold,
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "route": route,
        "schedule_cron": schedule_cron,
        "deliver": deliver,
        "message_template": _build_message_template(
            metric=metric,
            condition=condition,
            threshold=threshold,
            timezone=timezone,
            schedule_cron=schedule_cron,
            deliver=deliver,
        ),
        "created_at": _utc_iso(now),
    }

    try:
        validated = normalize_and_validate_payload("alert_rule", payload)
    except ContractsError as exc:
        raise AlertRuleParseError(
            "Parsed alert rule payload failed schema validation."
        ) from exc

    return AlertRuleParseResult(
        alert_rule=validated,
        timezone=timezone,
        monitored_dimension=metric,
        comparison_operator=condition,
        threshold=threshold,
        schedule_cron=schedule_cron,
        deliver=deliver,
    )


def _parse_metric(text: str) -> str:
    lowered = text.lower()

    if "landed cost" in lowered or "total landed cost" in lowered:
        return "landed_cost_total"
    if "freight" in lowered or "shipping quote" in lowered or "shipping cost" in lowered:
        return "freight_quote_amount"
    if "parallel" in lowered or "black market" in lowered:
        return "fx_parallel_rate"
    if "official" in lowered and ("fx" in lowered or "exchange rate" in lowered):
        return "fx_official_rate"
    if "fx" in lowered or "exchange rate" in lowered:
        return "fx_official_rate"

    raise AlertRuleParseError(
        "Could not determine monitored dimension from alert request."
    )


def _parse_condition_and_threshold(text: str) -> tuple[str, float]:
    lowered = text.lower()
    number = r"(?P<num>-?\d[\d,]*(?:\.\d+)?)"
    patterns = (
        ("lte", rf"(?:at\s+or\s+below|at\s+most|no\s+more\s+than|not\s+above|<=)\s*{number}"),
        ("gte", rf"(?:at\s+or\s+above|at\s+least|no\s+less\s+than|not\s+below|>=)\s*{number}"),
        ("lt", rf"(?:below|under|less\s+than|<)\s*{number}"),
        ("gt", rf"(?:above|over|greater\s+than|more\s+than|>)\s*{number}"),
        ("eq", rf"(?:equal\s+to|equals|exactly|==|=)\s*{number}"),
    )

    for condition, pattern in patterns:
        match = re.search(pattern, lowered, flags=re.IGNORECASE)
        if match:
            return condition, _to_float(match.group("num"))

    raise AlertRuleParseError(
        "Could not parse comparison operator and numeric threshold from request."
    )


def _parse_schedule_cron(text: str) -> str:
    cron = _extract_cron_expression(text)
    if cron is not None:
        return cron

    lowered = text.lower()

    interval_match = re.search(r"\bevery\s+(\d+)\s+hours?\b", lowered)
    if interval_match:
        hours = int(interval_match.group(1))
        if hours < 1 or hours > 23:
            raise AlertRuleParseError("Hourly interval must be between 1 and 23 hours.")
        return f"0 */{hours} * * *"

    if "every hour" in lowered:
        return "0 * * * *"

    if "every weekday" in lowered or "weekdays" in lowered:
        hour, minute = _parse_hour_minute(text, default_hour=8, default_minute=0)
        return f"{minute} {hour} * * 1-5"

    if (
        "every day" in lowered
        or "daily" in lowered
        or "every morning" in lowered
        or "each day" in lowered
    ):
        hour, minute = _parse_hour_minute(text, default_hour=8, default_minute=0)
        return f"{minute} {hour} * * *"

    return DEFAULT_SCHEDULE_CRON


def _extract_cron_expression(text: str) -> str | None:
    pattern = re.compile(
        r"(?<!\S)(?:on\s+schedule\s+|schedule\s+)?((?:[\d*/,\-]+\s+){4}[\d*/,\-]+)(?!\S)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        candidate = " ".join(match.group(1).split())
        parts = candidate.split()
        if len(parts) != 5:
            continue
        if all(_CRON_FIELD_RE.fullmatch(part) for part in parts):
            return candidate
    return None


def _parse_hour_minute(text: str, *, default_hour: int, default_minute: int) -> tuple[int, int]:
    match = _TIME_AT_RE.search(text)
    if not match:
        return default_hour, default_minute

    hour = int(match.group("hour"))
    minute = int(match.group("minute") or "0")
    ampm = (match.group("ampm") or "").lower()

    if ampm:
        if hour < 1 or hour > 12:
            raise AlertRuleParseError("Hour with am/pm must be between 1 and 12.")
        if ampm == "am":
            hour = 0 if hour == 12 else hour
        else:
            hour = 12 if hour == 12 else hour + 12
    else:
        if hour < 0 or hour > 23:
            raise AlertRuleParseError("24-hour clock hour must be between 0 and 23.")

    if minute < 0 or minute > 59:
        raise AlertRuleParseError("Minute must be between 0 and 59.")
    return hour, minute


def _parse_timezone(text: str, *, default_timezone: str | None) -> str:
    for candidate in _TIMEZONE_IANA_RE.findall(text):
        try:
            return normalize_timezone(candidate)
        except TimezoneNormalizationError:
            continue

    for token in re.findall(r"\b(?:UTC|GMT)\b", text, flags=re.IGNORECASE):
        try:
            return normalize_timezone(token)
        except TimezoneNormalizationError:
            continue

    if "local time" in text.lower() and default_timezone:
        return _normalize_timezone_value(default_timezone)

    if default_timezone:
        return _normalize_timezone_value(default_timezone)

    raise AlertRuleParseError(
        "Timezone is required for alert scheduling. Provide an IANA timezone "
        "(for example: Africa/Lagos) or set a default timezone."
    )


def _normalize_timezone_value(value: str) -> str:
    try:
        return normalize_timezone(value)
    except TimezoneNormalizationError as exc:
        raise AlertRuleParseError("Default timezone is invalid.") from exc


def _parse_deliver_target(text: str, *, default_deliver: str) -> str:
    lowered = text.lower()

    if (
        "to origin" in lowered
        or "same chat" in lowered
        or "this chat" in lowered
        or "deliver to origin" in lowered
    ):
        return "origin"

    for target in _VALID_DELIVER_TARGETS:
        if target == "origin":
            continue
        if re.search(rf"\b(?:deliver|send)(?:\s+\w+){{0,3}}\s+to\s+{target}\b", lowered):
            return target
        if re.search(rf"\bon\s+{target}\b", lowered):
            return target

    return _normalize_deliver(default_deliver)


def _normalize_deliver(value: str) -> str:
    deliver = _require_non_blank(value, name="default_deliver").lower()
    if deliver not in _VALID_DELIVER_TARGETS:
        raise AlertRuleParseError(
            f"Unsupported deliver target: {value!r}. "
            f"Expected one of: {', '.join(sorted(_VALID_DELIVER_TARGETS))}."
        )
    return deliver


def _parse_currencies(
    text: str,
    *,
    metric: str,
    default_base_currency: str | None,
    default_quote_currency: str | None,
) -> tuple[str | None, str | None]:
    if metric not in {"fx_parallel_rate", "fx_official_rate"}:
        return None, None

    pair = _extract_currency_pair(text)
    if pair is not None:
        return pair

    if default_base_currency and default_quote_currency:
        return (
            normalize_currency(default_base_currency),
            normalize_currency(default_quote_currency),
        )
    if default_base_currency or default_quote_currency:
        raise AlertRuleParseError(
            "Both default_base_currency and default_quote_currency are required together."
        )

    raise AlertRuleParseError(
        "FX alerts require a currency pair (for example: USD/NGN) "
        "or default base/quote currencies."
    )


def _extract_currency_pair(text: str) -> tuple[str, str] | None:
    match = _CURRENCY_PAIR_RE.search(text)
    if match:
        return normalize_currency(match.group(1)), normalize_currency(match.group(2))

    match = _CURRENCY_TO_RE.search(text)
    if match:
        return normalize_currency(match.group(1)), normalize_currency(match.group(2))

    return None


def _parse_route(text: str) -> dict[str, str] | None:
    match = _FROM_TO_COUNTRY_RE.search(text)
    if not match:
        return None

    origin = _resolve_country(match.group(1))
    destination = _resolve_country(match.group(2))
    if origin is None or destination is None:
        return None

    return {
        "origin_country": origin,
        "destination_country": destination,
    }


def _resolve_country(value: str) -> str | None:
    normalized = " ".join(str(value).strip().lower().split())
    if not normalized:
        return None
    if normalized in _COUNTRY_ALIASES:
        return _COUNTRY_ALIASES[normalized]

    for alias, code in sorted(_COUNTRY_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in normalized:
            return code
    return None


def _build_message_template(
    *,
    metric: str,
    condition: str,
    threshold: float,
    timezone: str,
    schedule_cron: str,
    deliver: str,
) -> str:
    return (
        "Alert trigger: "
        f"{metric} {condition} {threshold}. "
        f"Schedule={schedule_cron}. "
        f"Timezone={timezone}. "
        f"Deliver={deliver}."
    )


def _to_float(raw: str) -> float:
    cleaned = raw.replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError as exc:
        raise AlertRuleParseError(f"Invalid numeric threshold: {raw!r}") from exc


def _utc_iso(value: datetime) -> str:
    dt_value = value
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=dt_timezone.utc)
    return dt_value.astimezone(dt_timezone.utc).isoformat().replace("+00:00", "Z")


def _require_non_blank(value: str, *, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise AlertRuleParseError(f"{name} must not be blank.")
    return text
