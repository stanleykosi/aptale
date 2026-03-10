from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.flows.hs_code_inference import HSCodeInferenceError, infer_hs_codes  # noqa: E402


def _base_payload() -> dict:
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
                "description": "Smartphone accessories",
                "quantity": 10,
                "unit": "carton",
                "unit_price": 100.0,
                "line_total": 1000.0,
                "weight_kg": 500.0,
                "country_of_origin": "CN",
                "hs_code": None,
                "hs_confidence": None,
            }
        ],
        "extraction_confidence": 0.88,
        "needs_user_confirmation": True,
        "uncertainties": [],
    }


def test_infer_hs_codes_sets_high_confidence_code() -> None:
    def engine(**_: object) -> dict:
        return {"hs_code": "85.17.12", "confidence": 0.93, "reason": "telecom parts"}

    out = infer_hs_codes(_base_payload(), inference_engine=engine, confidence_threshold=0.8)

    assert out["items"][0]["hs_code"] == "851712"
    assert out["items"][0]["hs_confidence"] == 0.93
    assert out["needs_user_confirmation"] is False
    assert out["uncertainties"] == []


def test_infer_hs_codes_flags_low_confidence_for_confirmation() -> None:
    def engine(**_: object) -> dict:
        return {"hs_code": "851712", "confidence": 0.41}

    out = infer_hs_codes(_base_payload(), inference_engine=engine, confidence_threshold=0.8)

    assert out["items"][0]["hs_code"] == "851712"
    assert out["needs_user_confirmation"] is True
    assert any("hs_code_low_confidence" in value for value in out["uncertainties"])


def test_infer_hs_codes_flags_missing_code_for_confirmation() -> None:
    def engine(**_: object) -> dict:
        return {"hs_code": None, "confidence": None}

    out = infer_hs_codes(_base_payload(), inference_engine=engine, confidence_threshold=0.8)

    assert out["items"][0]["hs_code"] is None
    assert out["needs_user_confirmation"] is True
    assert any("hs_code_missing_or_unknown" in value for value in out["uncertainties"])


def test_infer_hs_codes_rejects_invalid_engine_output() -> None:
    def engine(**_: object) -> dict:
        return {"hs_code": "851712", "confidence": 4.2}

    with pytest.raises(HSCodeInferenceError):
        infer_hs_codes(_base_payload(), inference_engine=engine)

