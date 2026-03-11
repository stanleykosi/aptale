from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.alerts.schedule_alert import (  # noqa: E402
    ScheduleAlertError,
    build_schedule_alert_plan,
    schedule_alert,
)


def _fixed_now() -> datetime:
    return datetime(2026, 3, 11, 8, 0, 0, tzinfo=timezone.utc)


def test_build_schedule_alert_plan_enforces_origin_and_embeds_timezone() -> None:
    plan = build_schedule_alert_plan(
        (
            "Alert me when parallel FX rate USD/NGN is below 1400 "
            "every day at 8am Africa/Lagos and deliver to origin."
        ),
        user_id="user_001",
        sourcing_context={"currency_pair": "USD/NGN", "source_policy": "web_search"},
        now_fn=_fixed_now,
        alert_id_factory=lambda: "alrt_test_001",
    )

    assert plan.schedule_cronjob_args["deliver"] == "origin"
    assert plan.schedule_cronjob_args["schedule"] == "0 8 * * *"
    assert plan.schedule_cronjob_args["name"].startswith("Aptale Alert:")
    assert "User timezone: Africa/Lagos" in plan.cron_prompt
    assert "This cron run starts with zero memory of prior chat." in plan.cron_prompt


def test_schedule_alert_calls_schedule_cronjob_with_canonical_args() -> None:
    captured: dict[str, object] = {}

    def _fake_schedule_cronjob(**kwargs):  # type: ignore[no-untyped-def]
        captured.update(kwargs)
        return {"job_id": "job_123", "status": "scheduled"}

    result = schedule_alert(
        (
            "Alert me when official exchange rate USD/NGN is at or below 1500 "
            "every weekday at 9:30 Africa/Lagos and deliver to origin."
        ),
        user_id="user_002",
        sourcing_context={"currency_pair": "USD/NGN"},
        schedule_cronjob=_fake_schedule_cronjob,
        now_fn=_fixed_now,
        alert_id_factory=lambda: "alrt_test_002",
    )

    assert captured["deliver"] == "origin"
    assert captured["schedule"] == "30 9 * * 1-5"
    assert "User timezone: Africa/Lagos" in str(captured["prompt"])
    assert result.tool_response["job_id"] == "job_123"


def test_schedule_alert_fails_fast_on_non_origin_delivery_request() -> None:
    with pytest.raises(ScheduleAlertError):
        build_schedule_alert_plan(
            (
                "Alert me when parallel FX rate USD/NGN is below 1400 "
                "every day at 8am Africa/Lagos and deliver to telegram."
            ),
            user_id="user_003",
            sourcing_context={"currency_pair": "USD/NGN"},
            now_fn=_fixed_now,
            alert_id_factory=lambda: "alrt_test_003",
        )


def test_schedule_alert_fails_when_schedule_cronjob_raises() -> None:
    def _failing_schedule_cronjob(**kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("scheduler unavailable")

    with pytest.raises(ScheduleAlertError):
        schedule_alert(
            (
                "Alert me when parallel FX rate USD/NGN is below 1400 "
                "every day at 8am Africa/Lagos and deliver to origin."
            ),
            user_id="user_004",
            sourcing_context={"currency_pair": "USD/NGN"},
            schedule_cronjob=_failing_schedule_cronjob,
            now_fn=_fixed_now,
            alert_id_factory=lambda: "alrt_test_004",
        )
