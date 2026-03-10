from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.delegation.error_policy import (  # noqa: E402
    SourcingFailureCode,
    SourcingLegFailureError,
    classify_execution_error,
    resolve_sourcing_leg,
)
from aptale.formatters.source_failures import (  # noqa: E402
    render_source_failure,
    render_source_failures,
)


def _freight_payload() -> dict:
    return {
        "schema_version": "1.0",
        "quote_id": "fq_001",
        "extraction_id": "invext_001",
        "provider_name": "ACME Forwarding",
        "origin_country": "CN",
        "destination_country": "NG",
        "origin_port": "Guangzhou",
        "destination_port": "Lagos",
        "mode": "sea",
        "service_level": "standard",
        "transit_time_days": 32,
        "currency": "USD",
        "quote_amount": 450.0,
        "charge_breakdown": [
            {"name": "Base Freight", "amount": 450.0, "currency": "USD"},
        ],
        "valid_until": None,
        "source_type": "forwarder_portal",
        "sources": [
            {
                "source_url": "https://freight.example/quote/123",
                "source_title": "Freight Portal Quote",
                "retrieved_at": "2026-03-10T10:00:00Z",
                "method": "browserbase",
            }
        ],
        "captured_at": "2026-03-10T10:00:00Z",
    }


def test_resolve_sourcing_leg_returns_validated_result() -> None:
    parsed = resolve_sourcing_leg(
        task_type="freight",
        raw_output=json.dumps(_freight_payload()),
    )
    assert parsed.task_type == "freight"
    assert parsed.payload["quote_id"] == "fq_001"


def test_resolve_sourcing_leg_detects_timeout_and_allows_open_web_switch() -> None:
    with pytest.raises(SourcingLegFailureError) as exc:
        resolve_sourcing_leg(
            task_type="freight",
            execution_error=TimeoutError("browser task timed out after 120 seconds"),
        )

    failure = exc.value.failure
    assert failure.code == SourcingFailureCode.TIMEOUT
    assert failure.can_switch_to_open_web_search is True
    assert "timed out" in failure.detail


def test_resolve_sourcing_leg_detects_portal_outage() -> None:
    with pytest.raises(SourcingLegFailureError) as exc:
        resolve_sourcing_leg(
            task_type="customs",
            execution_error=RuntimeError("503 service unavailable from customs portal"),
        )

    failure = exc.value.failure
    assert failure.code == SourcingFailureCode.PORTAL_OUTAGE
    assert failure.can_switch_to_open_web_search is True


def test_resolve_sourcing_leg_detects_captcha_failure() -> None:
    with pytest.raises(SourcingLegFailureError) as exc:
        resolve_sourcing_leg(
            task_type="customs",
            execution_error=RuntimeError("CAPTCHA challenge blocked scraping"),
        )

    failure = exc.value.failure
    assert failure.code == SourcingFailureCode.CAPTCHA_FAILURE
    assert failure.can_switch_to_open_web_search is True


def test_resolve_sourcing_leg_detects_empty_result() -> None:
    with pytest.raises(SourcingLegFailureError) as exc:
        resolve_sourcing_leg(
            task_type="freight",
            raw_output="   ",
        )

    failure = exc.value.failure
    assert failure.code == SourcingFailureCode.EMPTY_RESULT
    assert failure.can_switch_to_open_web_search is True


def test_resolve_sourcing_leg_detects_schema_violation() -> None:
    bad_payload = _freight_payload()
    bad_payload.pop("quote_id")

    with pytest.raises(SourcingLegFailureError) as exc:
        resolve_sourcing_leg(
            task_type="freight",
            raw_output=json.dumps(bad_payload),
        )

    failure = exc.value.failure
    assert failure.code == SourcingFailureCode.SCHEMA_VIOLATION
    assert failure.can_switch_to_open_web_search is False


def test_classify_execution_error_fx_does_not_offer_open_web_switch() -> None:
    failure = classify_execution_error(
        task_type="fx",
        error=TimeoutError("request timeout"),
    )
    assert failure.code == SourcingFailureCode.TIMEOUT
    assert failure.can_switch_to_open_web_search is False


def test_render_source_failure_includes_leg_and_open_web_availability() -> None:
    with pytest.raises(SourcingLegFailureError) as exc:
        resolve_sourcing_leg(
            task_type="freight",
            execution_error=RuntimeError("portal offline"),
        )
    text = render_source_failure(exc.value.failure)
    assert "*Failed leg*: Freight sourcing" in text
    assert "*Open-web search path*: Available" in text


def test_render_source_failures_formats_multiple_failures() -> None:
    freight_failure = classify_execution_error(
        task_type="freight",
        error=RuntimeError("portal offline"),
    )
    fx_failure = classify_execution_error(
        task_type="fx",
        error=RuntimeError("output timeout"),
    )
    text = render_source_failures([freight_failure, fx_failure])
    assert "*Sourcing Failures*" in text
    assert "Freight sourcing" in text
    assert "FX sourcing" in text
