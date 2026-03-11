from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.calc.landed_cost import DISCLAIMER_TEXT  # noqa: E402
from aptale.formatters.alert_message import (  # noqa: E402
    AlertMessageFormatError,
    render_alert_message,
)


def test_render_fx_alert_message_includes_rate_window_sources_action_and_disclaimer() -> None:
    text = render_alert_message(
        {
            "metric": "fx_parallel_rate",
            "condition": "lt",
            "threshold": 1400,
            "current_value": 1378.25,
            "base_currency": "USD",
            "quote_currency": "NGN",
            "window_label": "latest run (24h)",
            "triggered_at": "2026-03-11T08:00:00Z",
            "source_urls": [
                "https://example.com/fx-source-1",
                "https://example.com/fx-source-2",
            ],
        }
    )

    assert "*Alert Triggered*" in text
    assert "Parallel FX Rate (USD/NGN)" in text
    assert "Current Value" in text
    assert "1,378.2500 NGN" in text
    assert "current_value < 1,400.0000 NGN" in text
    assert "latest run (24h)" in text
    assert "*Sources*" in text
    assert "https://example.com/fx-source-1" in text
    assert "*Recommended Action*" in text
    assert "*Disclaimer*" in text
    assert DISCLAIMER_TEXT in text


def test_render_freight_alert_message_uses_currency_format_and_disclaimer() -> None:
    text = render_alert_message(
        {
            "metric": "freight_quote_amount",
            "condition": "gt",
            "threshold": 2200,
            "current_value": 2455.5,
            "quote_currency": "USD",
            "window_label": "today",
            "source_urls": ["https://example.com/freight-source-1"],
        }
    )

    assert "Freight Quote" in text
    assert "2,455.50 USD" in text
    assert "current_value > 2,200.00 USD" in text
    assert "Compare alternate carriers/routes before booking." in text
    assert DISCLAIMER_TEXT in text


def test_render_alert_message_truncates_sources_to_top_three() -> None:
    text = render_alert_message(
        {
            "metric": "landed_cost_total",
            "condition": "lte",
            "threshold": 5000,
            "current_value": 4950.4,
            "quote_currency": "NGN",
            "source_urls": [
                "https://source-1.example",
                "https://source-2.example",
                "https://source-3.example",
                "https://source-4.example",
            ],
        }
    )

    assert "https://source-1.example" in text
    assert "https://source-3.example" in text
    assert "https://source-4.example" not in text


def test_render_alert_message_fails_on_invalid_metric() -> None:
    with pytest.raises(AlertMessageFormatError):
        render_alert_message(
            {
                "metric": "fx_rate_delta",
                "condition": "lt",
                "threshold": 1400,
                "current_value": 1300,
                "source_urls": ["https://example.com"],
            }
        )


def test_render_alert_message_fails_when_source_urls_missing() -> None:
    with pytest.raises(AlertMessageFormatError):
        render_alert_message(
            {
                "metric": "fx_parallel_rate",
                "condition": "lt",
                "threshold": 1400,
                "current_value": 1378.25,
                "base_currency": "USD",
                "quote_currency": "NGN",
                "source_urls": [],
            }
        )


def test_render_alert_message_fails_for_fx_without_currency_pair() -> None:
    with pytest.raises(AlertMessageFormatError):
        render_alert_message(
            {
                "metric": "fx_official_rate",
                "condition": "gte",
                "threshold": 1500,
                "current_value": 1510,
                "source_urls": ["https://example.com"],
            }
        )
