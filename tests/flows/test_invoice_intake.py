from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.flows.invoice_intake import (  # noqa: E402
    ExtractionOutputError,
    MissingImagePayloadError,
    orchestrate_invoice_intake,
)


def _valid_extraction_payload() -> dict:
    return {
        "source_language": "zh",
        "target_language": "en",
        "invoice_number": "INV-77",
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
                "description": "electronics",
                "quantity": 10,
                "unit": "carton",
                "unit_price": 100.0,
                "line_total": 1000.0,
                "weight_kg": 500.0,
                "country_of_origin": "CN",
                "hs_code": "851712",
                "hs_confidence": 0.9,
            }
        ],
        "extraction_confidence": 0.86,
        "needs_user_confirmation": True,
        "uncertainties": [],
    }


def test_orchestrate_invoice_intake_returns_clarification_handoff() -> None:
    calls = []

    def extractor(**kwargs):
        calls.append(kwargs)
        return _valid_extraction_payload()

    result = orchestrate_invoice_intake(
        {
            "message_id": "wamid.001",
            "user_id": "2348012345678",
            "image_base64": "ZmFrZQ==",
            "caption": "invoice photo",
        },
        multimodal_extractor=extractor,
        user_profile={"language": "en"},
        now_fn=lambda: datetime(2026, 3, 10, tzinfo=timezone.utc),
    )

    assert result.status == "awaiting_clarification"
    assert result.next_step == "clarify_extraction"
    assert result.clarify_required is True
    assert result.invoice_extraction["schema_version"] == "1.0"
    assert result.invoice_extraction["message_id"] == "wamid.001"
    assert len(calls) == 1
    assert calls[0]["context"]["channel"] == "whatsapp"
    assert "strict JSON" in calls[0]["extraction_prompt"]


def test_orchestrate_invoice_intake_fails_without_image() -> None:
    with pytest.raises(MissingImagePayloadError):
        orchestrate_invoice_intake(
            {"message_id": "wamid.002"},
            multimodal_extractor=lambda **_: _valid_extraction_payload(),
        )


def test_orchestrate_invoice_intake_fails_on_non_mapping_extractor_output() -> None:
    with pytest.raises(ExtractionOutputError):
        orchestrate_invoice_intake(
            {"message_id": "wamid.003", "image_base64": "ZmFrZQ=="},
            multimodal_extractor=lambda **_: "not-json",
        )


def test_orchestrate_invoice_intake_fails_on_invalid_schema_payload() -> None:
    bad_payload = _valid_extraction_payload()
    del bad_payload["items"]

    with pytest.raises(ExtractionOutputError):
        orchestrate_invoice_intake(
            {"message_id": "wamid.004", "image_base64": "ZmFrZQ=="},
            multimodal_extractor=lambda **_: bad_payload,
        )

