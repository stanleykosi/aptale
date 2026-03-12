"""Scheduling pathway for Aptale HS-lane Trade Radar cron jobs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Mapping

from .build_trade_radar_cron_prompt import (
    TradeRadarCronPromptError,
    build_trade_radar_cron_prompt,
)
from .parse_trade_radar_rule import (
    TradeRadarRuleParseError,
    TradeRadarRuleParseResult,
    parse_trade_radar_rule_request,
)


class ScheduleTradeRadarError(RuntimeError):
    """Raised when trade radar scheduling fails."""


@dataclass(frozen=True)
class ScheduleTradeRadarPlan:
    """Prepared schedule_cronjob payload for trade radar."""

    trade_radar_rule: dict[str, Any]
    timezone: str
    cron_prompt: str
    schedule_cronjob_args: dict[str, Any]


@dataclass(frozen=True)
class ScheduleTradeRadarResult:
    """Result of scheduling trade radar cron job."""

    plan: ScheduleTradeRadarPlan
    tool_response: Any


def build_schedule_trade_radar_plan(
    request_text: str,
    *,
    user_id: str,
    sourcing_context: Mapping[str, Any],
    default_timezone: str | None = None,
    now_fn: Callable[[], datetime] | None = None,
    alert_id_factory: Callable[[], str] | None = None,
) -> ScheduleTradeRadarPlan:
    try:
        parsed = parse_trade_radar_rule_request(
            request_text,
            user_id=user_id,
            default_timezone=default_timezone,
            now_fn=now_fn,
            alert_id_factory=alert_id_factory,
        )
    except TradeRadarRuleParseError as exc:
        raise ScheduleTradeRadarError("Failed to parse trade radar request.") from exc

    _ensure_origin_delivery(parsed)

    try:
        cron_prompt = build_trade_radar_cron_prompt(
            parsed.trade_radar_rule,
            sourcing_context=sourcing_context,
        )
    except TradeRadarCronPromptError as exc:
        raise ScheduleTradeRadarError("Failed to build trade radar cron prompt.") from exc

    schedule_args = {
        "prompt": cron_prompt,
        "schedule": parsed.trade_radar_rule["schedule_cron"],
        "name": _build_job_name(parsed),
        "deliver": "origin",
    }
    return ScheduleTradeRadarPlan(
        trade_radar_rule=dict(parsed.trade_radar_rule),
        timezone=parsed.timezone,
        cron_prompt=cron_prompt,
        schedule_cronjob_args=schedule_args,
    )


def schedule_trade_radar(
    request_text: str,
    *,
    user_id: str,
    sourcing_context: Mapping[str, Any],
    schedule_cronjob: Callable[..., Any],
    default_timezone: str | None = None,
    now_fn: Callable[[], datetime] | None = None,
    alert_id_factory: Callable[[], str] | None = None,
) -> ScheduleTradeRadarResult:
    if not callable(schedule_cronjob):
        raise ScheduleTradeRadarError("schedule_cronjob must be callable.")

    plan = build_schedule_trade_radar_plan(
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
        raise ScheduleTradeRadarError("schedule_cronjob invocation failed.") from exc

    return ScheduleTradeRadarResult(plan=plan, tool_response=response)


def _ensure_origin_delivery(parsed: TradeRadarRuleParseResult) -> None:
    deliver = parsed.trade_radar_rule.get("deliver")
    if deliver != "origin":
        raise ScheduleTradeRadarError("Trade radar requires deliver='origin'.")


def _build_job_name(parsed: TradeRadarRuleParseResult) -> str:
    rule = parsed.trade_radar_rule
    return (
        "Aptale Trade Radar: "
        f"HS {rule['hs_code']} {rule['origin_country']}->{rule['destination_country']} "
        f"({parsed.timezone})"
    )
