from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.calc.landed_cost import calculate_landed_cost  # noqa: E402
from aptale.export.csv_export import (  # noqa: E402
    BRANDED_FOOTER_TEXT,
    CSV_COLUMNS,
    CsvExportError,
    export_landed_cost_csv,
)


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


def test_export_landed_cost_csv_writes_canonical_columns_and_footer_rows(
    tmp_path: Path,
) -> None:
    output_payload = calculate_landed_cost(_base_input(), now_fn=_fixed_now)
    csv_path = export_landed_cost_csv(output_payload, output_dir=tmp_path)

    assert csv_path.is_absolute()
    assert csv_path.suffix == ".csv"

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == CSV_COLUMNS
        rows = list(reader)

    assert rows[-2]["row_type"] == "metadata"
    assert rows[-2]["row_key"] == "footer_brand"
    assert rows[-2]["value"] == BRANDED_FOOTER_TEXT
    assert rows[-1]["row_type"] == "disclaimer"
    assert rows[-1]["row_key"] == "liability_disclaimer"
    assert rows[-1]["value"] == output_payload["disclaimer"]


def test_export_landed_cost_csv_leaves_cost_per_unit_empty_when_null(
    tmp_path: Path,
) -> None:
    payload = calculate_landed_cost(_base_input(), now_fn=_fixed_now)
    payload["cost_per_unit"] = None

    csv_path = export_landed_cost_csv(payload, output_dir=tmp_path)
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    matching = [row for row in rows if row["row_key"] == "cost_per_unit"]
    assert len(matching) == 1
    assert matching[0]["amount"] == ""


def test_export_landed_cost_csv_rejects_relative_output_dir() -> None:
    payload = calculate_landed_cost(_base_input(), now_fn=_fixed_now)
    with pytest.raises(CsvExportError, match="output_dir must be absolute"):
        export_landed_cost_csv(payload, output_dir="runtime/exports/csv")


def test_export_landed_cost_csv_rejects_invalid_payload(tmp_path: Path) -> None:
    payload = calculate_landed_cost(_base_input(), now_fn=_fixed_now)
    del payload["breakdown"]

    with pytest.raises(CsvExportError, match="Invalid landed_cost_output payload"):
        export_landed_cost_csv(payload, output_dir=tmp_path)
