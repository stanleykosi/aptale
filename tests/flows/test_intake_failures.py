from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.errors.intake_errors import (  # noqa: E402
    BlurryImageFailure,
    MissingRouteFailure,
    UncertainHSCodeFailure,
    UnreadableTotalsFailure,
    detect_intake_failures,
    ensure_intake_ready_for_clarification,
)
from aptale.flows.intake_failure_responses import (  # noqa: E402
    build_intake_failure_response,
    render_intake_failure_response,
)


def _valid_payload() -> dict:
    return {
        "schema_version": "1.0",
        "extraction_id": "invext_001",
        "message_id": "wamid.001",
        "extracted_at": "2026-03-10T00:00:00Z",
        "source_language": "zh",
        "target_language": "en",
        "invoice_number": "INV-501",
        "invoice_date": "2026-03-10",
        "incoterm": "FOB",
        "origin_country": "CN",
        "destination_country": "NG",
        "origin_port": "Guangzhou",
        "destination_port": "Lagos",
        "currency": "USD",
        "subtotal": 1000.0,
        "total": 1100.0,
        "total_weight_kg": 500.0,
        "items": [
            {
                "line_id": "1",
                "description": "Electronics batch",
                "quantity": 10,
                "unit": "carton",
                "unit_price": 100.0,
                "line_total": 1000.0,
                "weight_kg": 500.0,
                "country_of_origin": "CN",
                "hs_code": "851712",
                "hs_confidence": 0.92,
            }
        ],
        "extraction_confidence": 0.88,
        "needs_user_confirmation": True,
        "uncertainties": [],
    }


def test_detect_blurry_image_failure() -> None:
    failures = detect_intake_failures(_valid_payload(), image_quality_score=0.3)
    assert isinstance(failures[0], BlurryImageFailure)


def test_detect_missing_route_failure() -> None:
    payload = _valid_payload()
    payload["destination_port"] = None
    failures = detect_intake_failures(payload)
    assert any(isinstance(failure, MissingRouteFailure) for failure in failures)


def test_detect_unreadable_totals_failure() -> None:
    payload = _valid_payload()
    payload["total"] = None
    failures = detect_intake_failures(payload)
    assert any(isinstance(failure, UnreadableTotalsFailure) for failure in failures)


def test_detect_uncertain_hs_code_failure() -> None:
    payload = _valid_payload()
    payload["items"][0]["hs_confidence"] = 0.2
    failures = detect_intake_failures(payload)
    assert any(isinstance(failure, UncertainHSCodeFailure) for failure in failures)


def test_ensure_intake_ready_raises_first_failure_fail_fast() -> None:
    with pytest.raises(BlurryImageFailure):
        ensure_intake_ready_for_clarification(_valid_payload(), image_quality_score=0.2)


def test_render_failure_response_requests_clearer_upload_or_manual_details() -> None:
    text = render_intake_failure_response(BlurryImageFailure())
    assert "*Intake Blocked*" in text
    assert "Upload a clearer invoice photo" in text
    assert "type the missing route and totals manually" in text


def test_build_failure_response_returns_none_when_no_failures() -> None:
    assert build_intake_failure_response(_valid_payload()) is None


def test_build_failure_response_prefers_first_failure_ordering() -> None:
    payload = _valid_payload()
    payload["destination_port"] = None
    text = build_intake_failure_response(payload, image_quality_score=0.2)
    assert text is not None
    # Blurry image is higher-priority than missing route.
    assert "too blurry" in text.lower()

