"""Scheduling pathway for Aptale arbitrage/threshold alerts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Mapping

from .build_cron_prompt import (
    CronPromptBuildError,
    build_alert_cron_prompt,
)
from .parse_rule import (
    AlertRuleParseError,
    AlertRuleParseResult,
    parse_alert_rule_request,
)


class ScheduleAlertError(RuntimeError):
    """Raised when alert scheduling flow cannot complete safely."""


@dataclass(frozen=True)
class ScheduleAlertPlan:
    """Prepared schedule_cronjob tool call payload for one alert rule."""

    alert_rule: dict[str, Any]
    timezone: str
    cron_prompt: str
    schedule_cronjob_args: dict[str, Any]


@dataclass(frozen=True)
class ScheduleAlertResult:
    """Result of executing schedule_cronjob for a prepared alert plan."""

    plan: ScheduleAlertPlan
    tool_response: Any


def build_schedule_alert_plan(
    request_text: str,
    *,
    user_id: str,
    sourcing_context: Mapping[str, Any],
    default_timezone: str | None = None,
    now_fn: Callable[[], datetime] | None = None,
    alert_id_factory: Callable[[], str] | None = None,
) -> ScheduleAlertPlan:
    """
    Build a canonical schedule_cronjob invocation for an alert request.

    Step-42 canonical behavior enforces `deliver="origin"` so alert output
    returns to the same WhatsApp chat where the alert was configured.
    """
    try:
        parsed = parse_alert_rule_request(
            request_text,
            user_id=user_id,
            default_timezone=default_timezone,
            default_deliver="origin",
            now_fn=now_fn,
            alert_id_factory=alert_id_factory,
        )
    except AlertRuleParseError as exc:
        raise ScheduleAlertError("Failed to parse alert rule request.") from exc

    _ensure_origin_delivery(parsed)

    try:
        cron_prompt = build_alert_cron_prompt(
            parsed.alert_rule,
            timezone=parsed.timezone,
            sourcing_context=sourcing_context,
        )
    except CronPromptBuildError as exc:
        raise ScheduleAlertError("Failed to build cron prompt for alert scheduling.") from exc

    schedule_args = {
        "prompt": cron_prompt,
        "schedule": parsed.schedule_cron,
        "name": _build_job_name(parsed),
        "deliver": "origin",
    }
    return ScheduleAlertPlan(
        alert_rule=dict(parsed.alert_rule),
        timezone=parsed.timezone,
        cron_prompt=cron_prompt,
        schedule_cronjob_args=schedule_args,
    )


def schedule_alert(
    request_text: str,
    *,
    user_id: str,
    sourcing_context: Mapping[str, Any],
    schedule_cronjob: Callable[..., Any],
    default_timezone: str | None = None,
    now_fn: Callable[[], datetime] | None = None,
    alert_id_factory: Callable[[], str] | None = None,
) -> ScheduleAlertResult:
    """
    Parse + build + execute alert scheduling using the schedule_cronjob tool.
    """
    if not callable(schedule_cronjob):
        raise ScheduleAlertError("schedule_cronjob must be callable.")

    plan = build_schedule_alert_plan(
        request_text,
        user_id=user_id,
        sourcing_context=sourcing_context,
        default_timezone=default_timezone,
        now_fn=now_fn,
        alert_id_factory=alert_id_factory,
    )

    try:
        response = schedule_cronjob(**plan.schedule_cronjob_args)
    except Exception as exc:
        raise ScheduleAlertError("schedule_cronjob invocation failed.") from exc

    return ScheduleAlertResult(plan=plan, tool_response=response)


def _ensure_origin_delivery(parsed: AlertRuleParseResult) -> None:
    if parsed.deliver != "origin":
        raise ScheduleAlertError(
            "Aptale alert scheduling currently requires deliver='origin' "
            "so alerts return to the originating WhatsApp chat."
        )


def _build_job_name(parsed: AlertRuleParseResult) -> str:
    return (
        "Aptale Alert: "
        f"{parsed.monitored_dimension} {parsed.comparison_operator} {parsed.threshold} "
        f"({parsed.timezone})"
    )
