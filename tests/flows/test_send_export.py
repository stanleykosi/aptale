from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.calc.landed_cost import calculate_landed_cost  # noqa: E402
from aptale.flows.send_export import (  # noqa: E402
    SendExportError,
    UnsupportedExportFormatError,
    assemble_whatsapp_export_response,
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


def _fixed_now() -> datetime:
    return datetime(2026, 3, 10, 8, 30, 45, tzinfo=timezone.utc)


def test_assemble_whatsapp_export_response_pdf_includes_disclaimer_and_attachment(
    tmp_path: Path,
) -> None:
    payload = calculate_landed_cost(_base_input(), now_fn=_fixed_now)

    result = assemble_whatsapp_export_response(
        payload,
        export_format="pdf",
        output_dir=tmp_path,
    )

    assert "*Quote Summary*" in result.message_markdown
    assert "*Disclaimer*" in result.message_markdown
    assert payload["disclaimer"] in result.message_markdown

    assert len(result.attachments) == 1
    attachment = result.attachments[0]
    assert attachment.type == "document"
    assert attachment.mime_type == "application/pdf"
    assert attachment.filename.endswith(".pdf")
    assert Path(attachment.path).is_absolute()
    assert Path(attachment.path).is_file()


def test_assemble_whatsapp_export_response_csv_attachment(tmp_path: Path) -> None:
    payload = calculate_landed_cost(_base_input(), now_fn=_fixed_now)

    result = assemble_whatsapp_export_response(
        payload,
        export_format="csv",
        output_dir=tmp_path,
        filename_stem="quote_001",
    )

    assert len(result.attachments) == 1
    attachment = result.attachments[0]
    assert attachment.type == "document"
    assert attachment.mime_type == "text/csv"
    assert attachment.filename == "quote_001.csv"
    assert Path(attachment.path).is_file()


def test_assemble_whatsapp_export_response_fails_on_unsupported_export_format(
    tmp_path: Path,
) -> None:
    payload = calculate_landed_cost(_base_input(), now_fn=_fixed_now)
    with pytest.raises(UnsupportedExportFormatError):
        assemble_whatsapp_export_response(
            payload,
            export_format="xlsx",
            output_dir=tmp_path,
        )


def test_assemble_whatsapp_export_response_fails_on_invalid_payload(
    tmp_path: Path,
) -> None:
    payload = calculate_landed_cost(_base_input(), now_fn=_fixed_now)
    del payload["disclaimer"]

    with pytest.raises(SendExportError, match="Invalid landed_cost_output payload"):
        assemble_whatsapp_export_response(
            payload,
            export_format="pdf",
            output_dir=tmp_path,
        )
