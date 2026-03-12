from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.alerts.schedule_trade_radar import (  # noqa: E402
    ScheduleTradeRadarError,
    build_schedule_trade_radar_plan,
    schedule_trade_radar,
)


def _fixed_now() -> datetime:
    return datetime(2026, 3, 11, 8, 0, 0, tzinfo=timezone.utc)


def test_build_schedule_trade_radar_plan_enforces_origin() -> None:
    plan = build_schedule_trade_radar_plan(
        "Track HS 850440 China->Nigeria, alert me daily at 8am Africa/Lagos.",
        user_id="user_001",
        sourcing_context={"lane": "CN->NG"},
        now_fn=_fixed_now,
        alert_id_factory=lambda: "trdr_001",
    )

    assert plan.schedule_cronjob_args["deliver"] == "origin"
    assert plan.schedule_cronjob_args["schedule"] == "0 8 * * *"
    assert "Trade Radar" in plan.schedule_cronjob_args["name"]


def test_schedule_trade_radar_calls_scheduler() -> None:
    captured: dict[str, object] = {}

    def _fake_schedule_cronjob(**kwargs):  # type: ignore[no-untyped-def]
        captured.update(kwargs)
        return {"job_id": "job_001", "status": "scheduled"}

    result = schedule_trade_radar(
        "Track HS 850440 China->Nigeria, alert me daily at 8am Africa/Lagos.",
        user_id="user_002",
        sourcing_context={"lane": "CN->NG"},
        schedule_cronjob=_fake_schedule_cronjob,
        now_fn=_fixed_now,
        alert_id_factory=lambda: "trdr_002",
    )

    assert captured["deliver"] == "origin"
    assert result.tool_response["job_id"] == "job_001"


def test_schedule_trade_radar_fails_when_scheduler_raises() -> None:
    def _failing_schedule_cronjob(**kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("scheduler unavailable")

    with pytest.raises(ScheduleTradeRadarError):
        schedule_trade_radar(
            "Track HS 850440 China->Nigeria, alert me daily at 8am Africa/Lagos.",
            user_id="user_003",
            sourcing_context={"lane": "CN->NG"},
            schedule_cronjob=_failing_schedule_cronjob,
            now_fn=_fixed_now,
            alert_id_factory=lambda: "trdr_003",
        )
