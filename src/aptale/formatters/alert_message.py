"""WhatsApp formatter for triggered Aptale alert notifications."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Mapping, Sequence

from aptale.calc.landed_cost import DISCLAIMER_TEXT

from .whatsapp_markdown import bold, bullets, join_sections, section

_METRIC_LABEL = {
    "fx_parallel_rate": "Parallel FX Rate",
    "fx_official_rate": "Official FX Rate",
    "freight_quote_amount": "Freight Quote",
    "landed_cost_total": "Landed Cost",
}

_CONDITION_SYMBOL = {
    "lt": "<",
    "lte": "<=",
    "gt": ">",
    "gte": ">=",
    "eq": "==",
}

_TRADE_OPPORTUNITY_METRICS = frozenset(_METRIC_LABEL.keys())


class AlertMessageFormatError(ValueError):
    """Raised when triggered alert payload cannot be formatted safely."""


def render_alert_message(triggered_alert: Mapping[str, Any]) -> str:
    """Render a short WhatsApp alert message for a triggered threshold rule."""
    payload = _validate_payload(triggered_alert)

    metric = payload["metric"]
    condition = payload["condition"]
    threshold = payload["threshold"]
    current_value = payload["current_value"]
    source_urls = payload["source_urls"]

    head_lines = [
        f"{bold('Metric')}: {_METRIC_LABEL[metric]}{_metric_suffix(payload)}",
        f"{bold('Current Value')}: {_format_value(metric, current_value, payload)}",
        (
            f"{bold('Threshold Crossed')}: "
            f"{_format_condition(metric, condition, threshold, payload)}"
        ),
        f"{bold('Window')}: {payload.get('window_label') or 'latest run'}",
    ]
    if payload.get("triggered_at"):
        head_lines.append(f"{bold('Triggered At (UTC)')}: {payload['triggered_at']}")

    sections = [
        section("Alert Triggered", bullets(head_lines)),
        section("Sources", bullets(_format_sources(source_urls))),
        section("Recommended Action", _recommended_action(metric=metric, condition=condition)),
    ]
    if metric in _TRADE_OPPORTUNITY_METRICS:
        sections.append(section("Disclaimer", DISCLAIMER_TEXT))

    return join_sections(sections)


def _validate_payload(triggered_alert: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(triggered_alert, Mapping):
        raise AlertMessageFormatError("triggered_alert must be a mapping.")
    payload = dict(triggered_alert)

    metric = payload.get("metric")
    if metric not in _METRIC_LABEL:
        raise AlertMessageFormatError(
            f"Unsupported metric: {metric!r}. Expected one of: {', '.join(sorted(_METRIC_LABEL))}."
        )

    condition = payload.get("condition")
    if condition not in _CONDITION_SYMBOL:
        raise AlertMessageFormatError(
            f"Unsupported condition: {condition!r}. Expected one of: {', '.join(sorted(_CONDITION_SYMBOL))}."
        )

    for key in ("threshold", "current_value"):
        if key not in payload:
            raise AlertMessageFormatError(f"{key} is required.")
        payload[key] = _to_decimal(payload[key], field_name=key)

    source_urls = payload.get("source_urls")
    if not isinstance(source_urls, Sequence) or isinstance(
        source_urls, (str, bytes, bytearray)
    ):
        raise AlertMessageFormatError("source_urls must be a non-empty list of URLs.")
    cleaned_sources = [str(item).strip() for item in source_urls if str(item).strip()]
    if not cleaned_sources:
        raise AlertMessageFormatError("source_urls must include at least one URL.")
    payload["source_urls"] = cleaned_sources

    if metric in {"fx_parallel_rate", "fx_official_rate"}:
        base = str(payload.get("base_currency") or "").strip().upper()
        quote = str(payload.get("quote_currency") or "").strip().upper()
        if len(base) != 3 or len(quote) != 3:
            raise AlertMessageFormatError(
                "FX alert messages require base_currency and quote_currency (ISO-4217)."
            )
        payload["base_currency"] = base
        payload["quote_currency"] = quote
    else:
        currency = str(payload.get("quote_currency") or "").strip().upper()
        if len(currency) == 3:
            payload["quote_currency"] = currency
        else:
            payload["quote_currency"] = None

    if "window_label" in payload and str(payload["window_label"]).strip() == "":
        raise AlertMessageFormatError("window_label must not be blank when provided.")

    if "triggered_at" in payload and payload["triggered_at"] is not None:
        if str(payload["triggered_at"]).strip() == "":
            raise AlertMessageFormatError("triggered_at must not be blank when provided.")
        payload["triggered_at"] = str(payload["triggered_at"]).strip()

    return payload


def _metric_suffix(payload: Mapping[str, Any]) -> str:
    metric = payload["metric"]
    if metric in {"fx_parallel_rate", "fx_official_rate"}:
        return f" ({payload['base_currency']}/{payload['quote_currency']})"
    return ""


def _format_condition(
    metric: str, condition: str, threshold: Decimal, payload: Mapping[str, Any]
) -> str:
    symbol = _CONDITION_SYMBOL[condition]
    return f"current_value {symbol} {_format_value(metric, threshold, payload)}"


def _format_value(metric: str, value: Decimal, payload: Mapping[str, Any]) -> str:
    if metric in {"fx_parallel_rate", "fx_official_rate"}:
        quote = payload["quote_currency"]
        return f"{_fmt_number(value, places=4)} {quote}"
    quote = payload.get("quote_currency")
    if quote:
        return f"{_fmt_number(value, places=2)} {quote}"
    return _fmt_number(value, places=2)


def _format_sources(source_urls: Sequence[str]) -> list[str]:
    lines: list[str] = []
    for index, url in enumerate(source_urls[:3], start=1):
        lines.append(f"{index}. {url}")
    return lines


def _recommended_action(*, metric: str, condition: str) -> str:
    if metric in {"fx_parallel_rate", "fx_official_rate"}:
        if condition in {"lt", "lte"}:
            return (
                "Rate moved below your target. If your lane is ready, consider locking FX and re-running landed cost now."
            )
        return (
            "Rate moved above your target. Re-check margin tolerance before committing this cycle."
        )

    if metric == "freight_quote_amount":
        if condition in {"lt", "lte"}:
            return (
                "Freight is below target. Consider requesting a fresh booking quote while this window holds."
            )
        return (
            "Freight is above target. Compare alternate carriers/routes before booking."
        )

    if condition in {"lt", "lte"}:
        return "Landed cost is below target. Review quote and consider proceeding with sourcing."
    return "Landed cost is above target. Re-check duty/freight/FX assumptions before proceeding."


def _to_decimal(value: Any, *, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as exc:
        raise AlertMessageFormatError(f"{field_name} must be numeric.") from exc


def _fmt_number(value: Decimal, *, places: int) -> str:
    quant = Decimal("1").scaleb(-places)
    amount = value.quantize(quant, rounding=ROUND_HALF_UP)
    return format(amount, f",.{places}f")
