from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.formatters.extraction_summary import (  # noqa: E402
    CONFIRMATION_PHRASE,
    ExtractionSummaryError,
    render_extraction_summary,
)
from aptale.formatters.whatsapp_markdown import bullets, numbered, section  # noqa: E402


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
        "uncertainties": [],
    }


def test_render_extraction_summary_core_structure() -> None:
    text = render_extraction_summary(_sample_extraction_payload())

    assert "*Extraction Summary*" in text
    assert "*Line Items*" in text
    assert "*Next Step*" in text
    assert f"`{CONFIRMATION_PHRASE}`" in text
    assert "items[0].hs_code" in text


def test_render_extraction_summary_includes_uncertainties_when_present() -> None:
    payload = _sample_extraction_payload()
    payload["uncertainties"] = ["origin_port uncertain"]

    text = render_extraction_summary(payload)
    assert "*Needs Confirmation*" in text
    assert "origin_port uncertain" in text


def test_render_extraction_summary_fails_on_invalid_payload() -> None:
    payload = _sample_extraction_payload()
    del payload["items"]

    with pytest.raises(ExtractionSummaryError):
        render_extraction_summary(payload)


def test_whatsapp_markdown_helpers_render_expected_output() -> None:
    assert bullets(["A", "B"]) == "- A\n- B"
    assert numbered(["A", "B"]) == "1. A\n2. B"
    assert section("Header", "Body") == "*Header*\nBody"

