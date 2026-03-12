from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.alerts.build_trade_radar_cron_prompt import (  # noqa: E402
    TradeRadarCronPromptError,
    build_trade_radar_cron_prompt,
)


def _base_rule() -> dict:
    return {
        "schema_version": "1.0",
        "alert_id": "trdr_001",
        "user_id": "user_001",
        "hs_code": "850440",
        "origin_country": "CN",
        "destination_country": "NG",
        "schedule_cron": "0 8 * * *",
        "timezone": "Africa/Lagos",
        "deliver": "origin",
        "active": True,
        "created_at": "2026-03-11T08:00:00Z",
    }


def test_build_trade_radar_prompt_includes_daily_delta_contract() -> None:
    prompt = build_trade_radar_cron_prompt(
        _base_rule(),
        sourcing_context={"lane": "CN->NG", "hs": "850440"},
    )

    assert "This cron run starts with zero memory of prior chat." in prompt
    assert "daily delta update that always sends" in prompt
    assert "No material changes since last run." in prompt


def test_build_trade_radar_prompt_fails_on_empty_context() -> None:
    with pytest.raises(TradeRadarCronPromptError):
        build_trade_radar_cron_prompt(_base_rule(), sourcing_context={})
