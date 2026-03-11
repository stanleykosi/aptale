from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.alerts.parse_rule import (  # noqa: E402
    AlertRuleParseError,
    parse_alert_rule_request,
)


PROMPT_PATH = ROOT / "src" / "aptale" / "prompts" / "alert_rule.md"


def _fixed_now() -> datetime:
    return datetime(2026, 3, 11, 8, 0, 0, tzinfo=timezone.utc)


def test_parse_fx_parallel_rule_with_explicit_pair_and_timezone() -> None:
    result = parse_alert_rule_request(
        (
            "Alert me when parallel FX rate USD/NGN is below 1,400 "
            "every day at 8am Africa/Lagos and send to origin."
        ),
        user_id="user_001",
        now_fn=_fixed_now,
        alert_id_factory=lambda: "alrt_test_001",
    )

    rule = result.alert_rule
    assert result.timezone == "Africa/Lagos"
    assert result.monitored_dimension == "fx_parallel_rate"
    assert result.comparison_operator == "lt"
    assert result.threshold == 1400.0
    assert result.schedule_cron == "0 8 * * *"
    assert rule["metric"] == "fx_parallel_rate"
    assert rule["condition"] == "lt"
    assert rule["threshold"] == 1400.0
    assert rule["base_currency"] == "USD"
    assert rule["quote_currency"] == "NGN"
    assert rule["deliver"] == "origin"
    assert rule["created_at"] == "2026-03-11T08:00:00Z"


def test_parse_fx_official_rule_uses_defaults_for_timezone_and_currencies() -> None:
    result = parse_alert_rule_request(
        (
            "Notify me when official exchange rate is at or below 1500 "
            "every weekday at 9:30 local time and deliver to telegram."
        ),
        user_id="user_002",
        default_timezone="Africa/Lagos",
        default_base_currency="USD",
        default_quote_currency="NGN",
        now_fn=_fixed_now,
        alert_id_factory=lambda: "alrt_test_002",
    )

    rule = result.alert_rule
    assert result.timezone == "Africa/Lagos"
    assert result.schedule_cron == "30 9 * * 1-5"
    assert result.deliver == "telegram"
    assert rule["metric"] == "fx_official_rate"
    assert rule["condition"] == "lte"
    assert rule["base_currency"] == "USD"
    assert rule["quote_currency"] == "NGN"


def test_parse_freight_rule_with_route_and_explicit_cron() -> None:
    result = parse_alert_rule_request(
        (
            "Track freight quote above 2200 from China to Nigeria on schedule 15 6 * * * "
            "timezone Africa/Lagos and deliver to whatsapp."
        ),
        user_id="user_003",
        now_fn=_fixed_now,
        alert_id_factory=lambda: "alrt_test_003",
    )

    rule = result.alert_rule
    assert result.monitored_dimension == "freight_quote_amount"
    assert result.comparison_operator == "gt"
    assert result.schedule_cron == "15 6 * * *"
    assert rule["route"] == {"origin_country": "CN", "destination_country": "NG"}
    assert rule["base_currency"] is None
    assert rule["quote_currency"] is None


def test_parse_landed_cost_rule_with_hourly_interval() -> None:
    result = parse_alert_rule_request(
        "Monitor landed cost exactly 5000 every 6 hours.",
        user_id="user_004",
        default_timezone="Europe/London",
        default_deliver="local",
        now_fn=_fixed_now,
        alert_id_factory=lambda: "alrt_test_004",
    )

    rule = result.alert_rule
    assert result.monitored_dimension == "landed_cost_total"
    assert result.comparison_operator == "eq"
    assert result.schedule_cron == "0 */6 * * *"
    assert result.deliver == "local"
    assert result.timezone == "Europe/London"
    assert rule["route"] is None


def test_parse_rule_fails_fast_when_threshold_missing() -> None:
    with pytest.raises(AlertRuleParseError):
        parse_alert_rule_request(
            (
                "Alert me when parallel FX rate USD/NGN goes below "
                "every day at 8am Africa/Lagos."
            ),
            user_id="user_005",
        )


def test_parse_rule_fails_when_timezone_missing() -> None:
    with pytest.raises(AlertRuleParseError):
        parse_alert_rule_request(
            "Alert me when freight quote is above 2100 from China to Nigeria.",
            user_id="user_006",
        )


def test_parse_rule_fails_when_fx_pair_missing() -> None:
    with pytest.raises(AlertRuleParseError):
        parse_alert_rule_request(
            "Alert me when parallel FX rate is below 1400 every day at 8am Africa/Lagos.",
            user_id="user_007",
        )


def test_alert_rule_prompt_contract() -> None:
    assert PROMPT_PATH.is_file()
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "monitored dimension" in content
    assert "comparison operator" in content
    assert "schedule_cron" in content
    assert "timezone" in content
    assert "deliver" in content
