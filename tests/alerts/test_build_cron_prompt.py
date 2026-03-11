from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.alerts.build_cron_prompt import (  # noqa: E402
    CronPromptBuildError,
    build_alert_cron_prompt,
)


def _base_alert_rule(
    *,
    metric: str = "fx_parallel_rate",
    condition: str = "lt",
    threshold: float = 1400.0,
    deliver: str = "origin",
    route: dict | None = None,
    base_currency: str | None = "USD",
    quote_currency: str | None = "NGN",
) -> dict:
    return {
        "schema_version": "1.0",
        "alert_id": "alrt_001",
        "user_id": "user_001",
        "active": True,
        "metric": metric,
        "condition": condition,
        "threshold": threshold,
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "route": route,
        "schedule_cron": "0 8 * * *",
        "deliver": deliver,
        "message_template": "template",
        "created_at": "2026-03-11T00:00:00Z",
    }


def test_build_cron_prompt_includes_fresh_session_target_and_no_result_contract() -> None:
    prompt = build_alert_cron_prompt(
        _base_alert_rule(),
        timezone="Africa/Lagos",
        sourcing_context={
            "currency_pair": "USD/NGN",
            "source_policy": "web_search_then_web_extract",
        },
    )

    assert "This cron run starts with zero memory of prior chat." in prompt
    assert "Metric: Parallel FX rate (fx_parallel_rate)" in prompt
    assert "Trigger condition: current_value < 1400.0" in prompt
    assert "User timezone: Africa/Lagos" in prompt
    assert "Deliver to origin" in prompt
    assert '"currency_pair": "USD/NGN"' in prompt
    assert "return exactly: NO_ALERT" in prompt


def test_build_cron_prompt_for_platform_delivery_mentions_target() -> None:
    prompt = build_alert_cron_prompt(
        _base_alert_rule(deliver="telegram"),
        timezone="Europe/London",
        sourcing_context={"currency_pair": "USD/NGN"},
        no_result_token="SKIP_ALERT",
    )

    assert "Deliver to platform 'telegram'" in prompt
    assert "return exactly: SKIP_ALERT" in prompt


def test_build_cron_prompt_for_landed_cost_uses_metric_specific_steps() -> None:
    prompt = build_alert_cron_prompt(
        _base_alert_rule(
            metric="landed_cost_total",
            condition="gte",
            threshold=5200.0,
            base_currency=None,
            quote_currency=None,
            route={"origin_country": "CN", "destination_country": "NG"},
        ),
        timezone="Africa/Lagos",
        sourcing_context={"lane": "CN->NG", "incoterm": "FOB"},
    )

    assert "Metric: Total landed cost (landed_cost_total)" in prompt
    assert "Trigger condition: current_value >= 5200.0" in prompt
    assert "Compute landed cost total deterministically" in prompt
    assert '"lane": "CN->NG"' in prompt


def test_build_cron_prompt_fails_on_invalid_alert_rule() -> None:
    bad_rule = _base_alert_rule()
    del bad_rule["schedule_cron"]

    with pytest.raises(CronPromptBuildError):
        build_alert_cron_prompt(
            bad_rule,
            timezone="Africa/Lagos",
            sourcing_context={"currency_pair": "USD/NGN"},
        )


def test_build_cron_prompt_fails_on_invalid_timezone() -> None:
    with pytest.raises(CronPromptBuildError):
        build_alert_cron_prompt(
            _base_alert_rule(),
            timezone="UTC+1",
            sourcing_context={"currency_pair": "USD/NGN"},
        )


def test_build_cron_prompt_fails_on_empty_sourcing_context() -> None:
    with pytest.raises(CronPromptBuildError):
        build_alert_cron_prompt(
            _base_alert_rule(),
            timezone="Africa/Lagos",
            sourcing_context={},
        )


def test_build_cron_prompt_fails_on_blank_no_result_token() -> None:
    with pytest.raises(CronPromptBuildError):
        build_alert_cron_prompt(
            _base_alert_rule(),
            timezone="Africa/Lagos",
            sourcing_context={"currency_pair": "USD/NGN"},
            no_result_token="   ",
        )
