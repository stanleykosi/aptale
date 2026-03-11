"""Self-contained cron prompt builder for Aptale alert monitoring."""

from __future__ import annotations

import json
from typing import Any, Mapping

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError
from aptale.memory.timezone import (
    TimezoneNormalizationError,
    normalize_timezone,
)


DEFAULT_NO_RESULT_TOKEN = "NO_ALERT"

_METRIC_LABEL = {
    "fx_parallel_rate": "Parallel FX rate",
    "fx_official_rate": "Official FX rate",
    "freight_quote_amount": "Freight quote amount",
    "landed_cost_total": "Total landed cost",
}

_CONDITION_SYMBOL = {
    "lt": "<",
    "lte": "<=",
    "gt": ">",
    "gte": ">=",
    "eq": "==",
}


class CronPromptBuildError(ValueError):
    """Raised when cron prompt inputs are invalid or incomplete."""


def build_alert_cron_prompt(
    alert_rule: Mapping[str, Any],
    *,
    timezone: str,
    sourcing_context: Mapping[str, Any],
    no_result_token: str = DEFAULT_NO_RESULT_TOKEN,
) -> str:
    """
    Build a self-contained cron prompt for alert monitoring.

    The output prompt is designed for Hermes cron fresh sessions, where the
    agent has no memory of prior chat state.
    """
    rule = _validate_alert_rule(alert_rule)
    tz = _normalize_timezone(timezone)
    context = _normalize_context(sourcing_context)
    token = _normalize_no_result_token(no_result_token)

    metric = rule["metric"]
    condition = rule["condition"]
    threshold = rule["threshold"]
    schedule = rule["schedule_cron"]
    deliver = rule["deliver"]
    condition_symbol = _CONDITION_SYMBOL[condition]

    context_json = json.dumps(context, indent=2, sort_keys=True, ensure_ascii=True)

    return (
        "You are running inside a Hermes scheduled cron execution for Aptale.\n\n"
        "*Fresh Session Constraint*\n"
        "- This cron run starts with zero memory of prior chat.\n"
        "- Use only the context provided in this prompt; do not ask the user follow-up questions.\n\n"
        "*Monitoring Target*\n"
        f"- Metric: {_METRIC_LABEL[metric]} ({metric})\n"
        f"- Trigger condition: current_value {condition_symbol} {threshold}\n"
        f"- Schedule (for audit): {schedule}\n"
        f"- User timezone: {tz}\n\n"
        "*Delivery Rule*\n"
        f"{_delivery_rule_text(deliver)}\n"
        "- Do not call send_message; Hermes gateway handles cron delivery.\n\n"
        "*Sourcing Context (Authoritative JSON)*\n"
        "```json\n"
        f"{context_json}\n"
        "```\n\n"
        "*Execution Steps*\n"
        f"{_metric_execution_steps(metric)}\n\n"
        "*Result Contract*\n"
        "- If trigger condition is met, return a concise WhatsApp-ready alert with:\n"
        "  current_value, threshold, condition, timezone, and source URLs.\n"
        f"- If trigger condition is NOT met, return exactly: {token}\n"
        "- When returning the no-result token, output only that token with no extra text."
    )


def _validate_alert_rule(alert_rule: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(alert_rule, Mapping):
        raise CronPromptBuildError("alert_rule must be a mapping.")
    try:
        return normalize_and_validate_payload("alert_rule", alert_rule)
    except ContractsError as exc:
        raise CronPromptBuildError(
            "alert_rule payload failed schema validation."
        ) from exc


def _normalize_timezone(value: str) -> str:
    try:
        return normalize_timezone(value)
    except TimezoneNormalizationError as exc:
        raise CronPromptBuildError("timezone must be a valid IANA timezone.") from exc


def _normalize_context(sourcing_context: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(sourcing_context, Mapping):
        raise CronPromptBuildError("sourcing_context must be a mapping.")
    context = dict(sourcing_context)
    if not context:
        raise CronPromptBuildError("sourcing_context must not be empty.")
    return context


def _normalize_no_result_token(value: str) -> str:
    token = str(value).strip()
    if not token:
        raise CronPromptBuildError("no_result_token must not be blank.")
    if any(ch.isspace() for ch in token):
        raise CronPromptBuildError("no_result_token must be a single token without whitespace.")
    return token


def _delivery_rule_text(deliver: str) -> str:
    if deliver == "origin":
        return (
            "- Deliver to origin: send the final cron response back to the exact chat where the rule was created."
        )
    if deliver == "local":
        return "- Deliver locally: write output to local cron output path only."
    return (
        f"- Deliver to platform '{deliver}': use Hermes platform delivery routing for that target."
    )


def _metric_execution_steps(metric: str) -> str:
    if metric == "fx_parallel_rate":
        return (
            "1. Fetch current official and parallel FX rates for the configured currency pair.\n"
            "2. Select the parallel rate as current_value and record source URLs.\n"
            "3. Evaluate trigger condition deterministically."
        )
    if metric == "fx_official_rate":
        return (
            "1. Fetch current official FX rate for the configured currency pair.\n"
            "2. Set official rate as current_value and record source URLs.\n"
            "3. Evaluate trigger condition deterministically."
        )
    if metric == "freight_quote_amount":
        return (
            "1. Source current freight quote amount for the configured route.\n"
            "2. Set normalized quote amount as current_value and record source URLs.\n"
            "3. Evaluate trigger condition deterministically."
        )
    if metric == "landed_cost_total":
        return (
            "1. Source required freight/customs/FX inputs from provided context lanes.\n"
            "2. Compute landed cost total deterministically.\n"
            "3. Set computed total as current_value, record source URLs, and evaluate trigger condition."
        )
    raise CronPromptBuildError(f"Unsupported metric for cron prompt: {metric!r}")
