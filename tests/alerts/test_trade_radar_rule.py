from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.alerts.parse_trade_radar_rule import (  # noqa: E402
    TradeRadarRuleParseError,
    parse_trade_radar_rule_request,
)


def _fixed_now() -> datetime:
    return datetime(2026, 3, 11, 8, 0, 0, tzinfo=timezone.utc)


def test_parse_trade_radar_rule_request_success() -> None:
    result = parse_trade_radar_rule_request(
        "Track HS 850440 China->Nigeria, alert me daily at 8am Africa/Lagos.",
        user_id="user_001",
        now_fn=_fixed_now,
        alert_id_factory=lambda: "trdr_001",
    )

    rule = result.trade_radar_rule
    assert rule["alert_id"] == "trdr_001"
    assert rule["hs_code"] == "850440"
    assert rule["origin_country"] == "CN"
    assert rule["destination_country"] == "NG"
    assert rule["schedule_cron"] == "0 8 * * *"
    assert rule["timezone"] == "Africa/Lagos"
    assert rule["deliver"] == "origin"
    assert rule["created_at"] == "2026-03-11T08:00:00Z"


def test_parse_trade_radar_rule_requires_explicit_track_phrase() -> None:
    with pytest.raises(TradeRadarRuleParseError):
        parse_trade_radar_rule_request(
            "Alert me about HS 850440 China->Nigeria",
            user_id="user_002",
            default_timezone="Africa/Lagos",
        )


def test_parse_trade_radar_rule_requires_timezone() -> None:
    with pytest.raises(TradeRadarRuleParseError):
        parse_trade_radar_rule_request(
            "Track HS 850440 China->Nigeria daily at 8am",
            user_id="user_003",
        )
