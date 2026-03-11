from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.calc.landed_cost import calculate_landed_cost  # noqa: E402
from aptale.export.csv_export import BRANDED_FOOTER_TEXT as CSV_BRAND  # noqa: E402
from aptale.export.csv_export import export_landed_cost_csv  # noqa: E402
from aptale.export.pdf_export import BRANDED_FOOTER_TEXT as PDF_BRAND  # noqa: E402
from aptale.export.pdf_export import export_landed_cost_pdf  # noqa: E402


def _fixed_now() -> datetime:
    return datetime(2026, 3, 10, 8, 30, 45, tzinfo=timezone.utc)


def _base_landed_cost_input() -> dict:
    return {
        "schema_version": "1.0",
        "extraction_id": "ext-e2e-export-001",
        "invoice_currency": "USD",
        "invoice_total": 1000.0,
        "invoice_total_weight_kg": 500.0,
        "freight_currency": "USD",
        "freight_quote_amount": 200.0,
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
            "freight_quote_id": "fq_e2e_export_001",
            "customs_quote_id": "cq_e2e_export_001",
            "fx_quote_id": "xq_e2e_export_001",
        },
        "requested_at": "2026-03-10T00:00:00Z",
    }


def test_exports_end_to_end_include_branding_and_disclaimer(tmp_path: Path) -> None:
    output = calculate_landed_cost(_base_landed_cost_input(), now_fn=_fixed_now)

    csv_path = export_landed_cost_csv(output, output_dir=tmp_path, filename_stem="e2e_quote")
    assert csv_path.is_file()
    assert csv_path.name == "e2e_quote.csv"

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    footer_rows = [row for row in rows if row["row_key"] == "footer_brand"]
    disclaimer_rows = [row for row in rows if row["row_key"] == "liability_disclaimer"]
    assert len(footer_rows) == 1
    assert footer_rows[0]["value"] == CSV_BRAND
    assert len(disclaimer_rows) == 1
    assert disclaimer_rows[0]["value"] == output["disclaimer"]

    pdf_path = export_landed_cost_pdf(output, output_dir=tmp_path, filename_stem="e2e_quote")
    assert pdf_path.is_file()
    assert pdf_path.name == "e2e_quote.pdf"

    pdf_bytes = pdf_path.read_bytes()
    assert b"Aptale Landed Cost Quote" in pdf_bytes
    assert PDF_BRAND.encode("utf-8") in pdf_bytes
    assert b"TradeWeaver" in pdf_bytes
    assert output["disclaimer"].encode("utf-8") in pdf_bytes

