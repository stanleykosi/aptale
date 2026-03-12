from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.calc.landed_cost import calculate_landed_cost  # noqa: E402
from aptale.formatters.quote_summary import render_quote_summary  # noqa: E402


def _fixed_now() -> datetime:
    return datetime(2026, 3, 10, 8, 30, 45, tzinfo=timezone.utc)


def _base_input() -> dict:
    return {
        "schema_version": "1.0",
        "extraction_id": "ext_001",
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
        "local_charges_currency": "NGN",
        "local_charges_amount": 0,
        "local_currency": "NGN",
        "profit_margin_pct": 20,
        "quote_ids": {
            "freight_quote_id": "fq_001",
            "customs_quote_id": "cq_001",
            "fx_quote_id": "xq_001",
            "local_charges_quote_id": "lq_001",
        },
        "requested_at": "2026-03-10T00:00:00Z",
    }


def test_render_quote_summary_renders_confidence_and_scenarios() -> None:
    output = calculate_landed_cost(_base_input(), now_fn=_fixed_now)
    text = render_quote_summary(
        output,
        quote_insights={
            "confidence_report": {
                "overall_score": 0.83,
                "overall_band": "high",
                "leg_scores": [
                    {"task_type": "freight", "score": 0.81, "band": "high"},
                ],
                "reasons": ["overall=0.83 (high)"],
            },
            "scenario_options": [
                {"name": "Fastest", "total_landed_cost": 170000.0, "delta_vs_balanced": 2000.0, "eta_days": 18},
                {"name": "Cheapest", "total_landed_cost": 160000.0, "delta_vs_balanced": -8000.0, "eta_days": 35},
                {"name": "Balanced", "total_landed_cost": 168000.0, "delta_vs_balanced": 0.0, "eta_days": 28},
            ],
            "advisory_failures": ["risk_notes: timeout"],
        },
    )

    assert "*Confidence*" in text
    assert "*Scenario Optimizer*" in text
    assert "*Advisory Warnings*" in text
