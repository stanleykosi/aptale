from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.flows.clarify_extraction import (  # noqa: E402
    ClarifyExtractionError,
    UnconfirmedExtractionError,
    assert_sourcing_allowed,
    begin_clarification,
    process_clarification_response,
)


def _sample_extraction_payload() -> dict:
    return {
        "schema_version": "1.0",
        "extraction_id": "invext_wamid.001",
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
        "uncertainties": ["destination_port needs verification"],
    }


def test_begin_clarification_blocks_sourcing_until_user_reply() -> None:
    result = begin_clarification(_sample_extraction_payload())

    assert result.status == "awaiting_clarification"
    assert result.can_source is False
    assert result.clarify_required is True
    assert "*Extraction Summary*" in result.clarify_message

    with pytest.raises(UnconfirmedExtractionError):
        assert_sourcing_allowed(result)


def test_process_clarification_response_accepts_explicit_confirmation() -> None:
    result = process_clarification_response(
        _sample_extraction_payload(),
        "Confirmed",
        now_fn=lambda: datetime(2026, 3, 10, tzinfo=timezone.utc),
    )

    assert result.status == "validated"
    assert result.can_source is True
    assert result.clarify_required is False
    assert result.invoice_correction is not None
    assert result.invoice_correction["confirmation_status"] == "confirmed"
    assert_sourcing_allowed(result)


def test_process_clarification_response_applies_field_corrections() -> None:
    result = process_clarification_response(
        _sample_extraction_payload(),
        'destination_port = "Tin Can Island"\nitems[0].hs_code = "850440"',
        now_fn=lambda: datetime(2026, 3, 10, tzinfo=timezone.utc),
    )

    assert result.status == "validated"
    assert result.can_source is True
    assert result.invoice_extraction["destination_port"] == "Tin Can Island"
    assert result.invoice_extraction["items"][0]["hs_code"] == "850440"
    assert result.invoice_correction is not None
    assert len(result.invoice_correction["corrections"]) == 2
    assert result.invoice_correction["corrections"][0]["path"] == "/destination_port"
    assert_sourcing_allowed(result)


def test_process_clarification_response_rejects_invalid_format() -> None:
    with pytest.raises(ClarifyExtractionError):
        process_clarification_response(
            _sample_extraction_payload(),
            "change destination_port to Tin Can Island",
        )

