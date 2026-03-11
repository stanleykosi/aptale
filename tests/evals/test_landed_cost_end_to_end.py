from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.calc.landed_cost import DISCLAIMER_TEXT, calculate_landed_cost  # noqa: E402
from aptale.contracts import validate_payload  # noqa: E402


def _fixed_now() -> datetime:
    return datetime(2026, 3, 10, 8, 30, 45, tzinfo=timezone.utc)


def _base_landed_cost_input() -> dict:
    return {
        "schema_version": "1.0",
        "extraction_id": "ext-e2e-001",
        "invoice_currency": "USD",
        "invoice_total": 1250.0,
        "invoice_total_weight_kg": 500.0,
        "freight_currency": "USD",
        "freight_quote_amount": 320.0,
        "customs_lines": [
            {
                "line_id": "1",
                "hs_code": "851712",
                "duty_rate_pct": 10.0,
                "vat_rate_pct": 5.0,
                "additional_rate_pct": 2.0,
                "fixed_fee": 10.0,
                "fixed_fee_currency": "USD",
            }
        ],
        "fx_base_currency": "USD",
        "fx_quote_currency": "NGN",
        "fx_selected_rate_type": "official",
        "fx_selected_rate": 100.0,
        "local_currency": "NGN",
        "profit_margin_pct": 20.0,
        "quote_ids": {
            "freight_quote_id": "fq_e2e_001",
            "customs_quote_id": "cq_e2e_001",
            "fx_quote_id": "xq_e2e_001",
        },
        "requested_at": "2026-03-10T00:00:00Z",
    }


def test_landed_cost_end_to_end_is_deterministic_and_schema_valid() -> None:
    output = calculate_landed_cost(_base_landed_cost_input(), now_fn=_fixed_now)
    validate_payload("landed_cost_output", output)

    assert output["calculation_id"] == "lc_ext_e2e_001_20260310083045"
    assert output["computed_at"] == "2026-03-10T08:30:45Z"
    assert output["local_currency"] == "NGN"
    assert output["subtotal_before_margin"] == 179250.0
    assert output["profit_amount"] == 35850.0
    assert output["total_landed_cost"] == 215100.0
    assert output["cost_per_unit"] == 430.2

    assert output["breakdown"] == {
        "invoice_local": 125000.0,
        "freight_local": 32000.0,
        "customs_local": 22250.0,
        "margin_local": 35850.0,
    }
    assert output["source_quote_ids"] == ["fq_e2e_001", "cq_e2e_001", "xq_e2e_001"]
    assert output["disclaimer"] == DISCLAIMER_TEXT
