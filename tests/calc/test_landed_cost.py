from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.calc.landed_cost import (  # noqa: E402
    LandedCostComputationError,
    calculate_landed_cost,
)
from aptale.contracts import validate_payload  # noqa: E402


def _base_input() -> dict:
    return {
        "schema_version": "1.0",
        "extraction_id": "ext-001",
        "invoice_currency": "USD",
        "invoice_total": 1000,
        "invoice_total_weight_kg": 500,
        "freight_currency": "USD",
        "freight_quote_amount": 200,
        "customs_lines": [
            {
                "line_id": "1",
                "hs_code": "851712",
                "duty_rate_pct": 10,
                "vat_rate_pct": 5,
                "additional_rate_pct": 2,
                "fixed_fee": 10,
                "fixed_fee_currency": "USD",
            }
        ],
        "fx_base_currency": "USD",
        "fx_quote_currency": "NGN",
        "fx_selected_rate_type": "parallel",
        "fx_selected_rate": 100,
        "local_currency": "NGN",
        "profit_margin_pct": 20,
        "quote_ids": {
            "freight_quote_id": "fq_001",
            "customs_quote_id": "cq_001",
            "fx_quote_id": "xq_001",
        },
        "requested_at": "2026-03-10T00:00:00Z",
    }


def _fixed_now() -> datetime:
    return datetime(2026, 3, 10, 8, 30, 45, tzinfo=timezone.utc)


def test_calculate_landed_cost_returns_expected_contract_values() -> None:
    output = calculate_landed_cost(_base_input(), now_fn=_fixed_now)
    validate_payload("landed_cost_output", output)

    assert output["calculation_id"] == "lc_ext_001_20260310083045"
    assert output["local_currency"] == "NGN"
    assert output["subtotal_before_margin"] == 138000.0
    assert output["profit_amount"] == 27600.0
    assert output["total_landed_cost"] == 165600.0
    assert output["cost_per_unit"] == 331.2
    assert output["breakdown"] == {
        "invoice_local": 100000.0,
        "freight_local": 20000.0,
        "customs_local": 18000.0,
        "margin_local": 27600.0,
    }
    assert output["source_quote_ids"] == ["fq_001", "cq_001", "xq_001"]
    assert (
        output["disclaimer"]
        == "Estimates only, subject to final customs assessment and market fluctuations."
    )
    assert output["computed_at"] == "2026-03-10T08:30:45Z"


def test_calculate_landed_cost_handles_null_weight_and_mixed_fixed_fee_currencies() -> None:
    payload = _base_input()
    payload["invoice_total"] = 500
    payload["invoice_total_weight_kg"] = None
    payload["freight_quote_amount"] = 100
    payload["fx_selected_rate"] = 10
    payload["profit_margin_pct"] = 10
    payload["customs_lines"] = [
        {
            "line_id": "1",
            "hs_code": "851712",
            "duty_rate_pct": 10,
            "vat_rate_pct": None,
            "additional_rate_pct": 0,
            "fixed_fee": 5,
            "fixed_fee_currency": "NGN",
        },
        {
            "line_id": "2",
            "hs_code": "852852",
            "duty_rate_pct": 20,
            "vat_rate_pct": 10,
            "additional_rate_pct": 0,
            "fixed_fee": 2,
            "fixed_fee_currency": "USD",
        },
    ]

    output = calculate_landed_cost(payload, now_fn=_fixed_now)

    assert output["subtotal_before_margin"] == 7025.0
    assert output["profit_amount"] == 702.5
    assert output["total_landed_cost"] == 7727.5
    assert output["cost_per_unit"] is None
    assert output["breakdown"]["customs_local"] == 1025.0


def test_calculate_landed_cost_fails_on_unsupported_fixed_fee_currency() -> None:
    payload = _base_input()
    payload["customs_lines"][0]["fixed_fee_currency"] = "EUR"

    with pytest.raises(LandedCostComputationError, match="Unsupported fixed_fee_currency"):
        calculate_landed_cost(payload, now_fn=_fixed_now)
