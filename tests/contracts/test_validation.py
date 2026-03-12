from __future__ import annotations

import math
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.contracts import (  # noqa: E402
    MalformedPayloadError,
    PartialPayloadError,
    SchemaValidationError,
    normalize_and_validate_payload,
    normalize_currency,
    normalize_incoterm,
    normalize_weight_to_kg,
    validate_landed_cost_input,
    validate_payload,
)


def _valid_invoice_extraction() -> dict:
    return {
        "schema_version": "1.0",
        "extraction_id": "ext_001",
        "message_id": "msg_001",
        "extracted_at": "2026-03-10T00:00:00Z",
        "source_language": "zh",
        "target_language": "en",
        "invoice_number": "INV-1001",
        "invoice_date": "2026-03-10",
        "incoterm": "cif",
        "origin_country": "cn",
        "destination_country": "ng",
        "origin_port": "Guangzhou",
        "destination_port": "Lagos",
        "currency": "usd",
        "subtotal": 1000,
        "total": 1100,
        "total_weight_kg": "500",
        "items": [
            {
                "line_id": "1",
                "description": "Consumer electronics",
                "quantity": 10,
                "unit": "carton",
                "unit_price": 100,
                "line_total": 1000,
                "weight_kg": "500",
                "country_of_origin": "cn",
                "hs_code": "85.17.12",
                "hs_confidence": 0.92,
            }
        ],
        "extraction_confidence": 0.88,
        "needs_user_confirmation": True,
        "uncertainties": ["hs_code_confirm"],
    }


def _valid_landed_cost_input() -> dict:
    return {
        "schema_version": "1.0",
        "extraction_id": "ext_001",
        "invoice_currency": "usd",
        "invoice_total": 1100,
        "invoice_total_weight_kg": 500,
        "freight_currency": "usd",
        "freight_quote_amount": 300,
        "customs_lines": [
            {
                "line_id": "1",
                "hs_code": "851712",
                "duty_rate_pct": 10,
                "vat_rate_pct": 7.5,
                "additional_rate_pct": 2,
                "fixed_fee": None,
                "fixed_fee_currency": None,
            }
        ],
        "fx_base_currency": "usd",
        "fx_quote_currency": "ngn",
        "fx_selected_rate_type": "parallel",
        "fx_selected_rate": 1450.25,
        "local_charges_currency": "ngn",
        "local_charges_amount": 0,
        "local_currency": "ngn",
        "profit_margin_pct": 15,
        "quote_ids": {
            "freight_quote_id": "fq_001",
            "customs_quote_id": "cq_001",
            "fx_quote_id": "xq_001",
            "local_charges_quote_id": "lq_001",
        },
        "requested_at": "2026-03-10T00:00:00Z",
    }


def test_normalizers_currency_incoterm_weight() -> None:
    assert normalize_currency(" usd ") == "USD"
    assert normalize_incoterm(" cif ") == "CIF"
    assert math.isclose(normalize_weight_to_kg("2.2046226218", "lb"), 1.0, rel_tol=1e-9)


def test_validate_payload_accepts_valid_invoice_extraction() -> None:
    payload = _valid_invoice_extraction()
    validated = normalize_and_validate_payload("invoice_extraction", payload)
    assert validated["currency"] == "USD"
    assert validated["incoterm"] == "CIF"
    assert validated["items"][0]["hs_code"] == "851712"


def test_validate_payload_rejects_missing_required_field() -> None:
    payload = _valid_invoice_extraction()
    del payload["items"]
    with pytest.raises(SchemaValidationError):
        validate_payload("invoice_extraction", payload)


def test_validate_payload_rejects_non_finite_number() -> None:
    payload = _valid_invoice_extraction()
    payload["total"] = float("nan")
    with pytest.raises(MalformedPayloadError):
        validate_payload("invoice_extraction", payload)


def test_validate_landed_cost_input_rejects_partial_currency_context() -> None:
    payload = _valid_landed_cost_input()
    payload["freight_currency"] = "eur"
    with pytest.raises(PartialPayloadError):
        validate_landed_cost_input(payload)


def test_validate_landed_cost_input_rejects_partial_fixed_fee_pair() -> None:
    payload = _valid_landed_cost_input()
    payload["customs_lines"][0]["fixed_fee"] = 15
    payload["customs_lines"][0]["fixed_fee_currency"] = None
    with pytest.raises(PartialPayloadError):
        validate_landed_cost_input(payload)
