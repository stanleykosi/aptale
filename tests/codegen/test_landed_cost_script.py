from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.codegen.export_helpers import ExportGenerationError  # noqa: E402
from aptale.codegen.landed_cost_script import (  # noqa: E402
    compute_and_export_landed_cost,
    render_landed_cost_execute_code_script,
)
from aptale.contracts import validate_payload  # noqa: E402


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


def test_compute_and_export_landed_cost_writes_contract_file(tmp_path: Path) -> None:
    output_path = compute_and_export_landed_cost(
        _base_input(),
        output_dir=str(tmp_path),
        now_fn=_fixed_now,
    )

    assert output_path.is_absolute()
    assert output_path.parent == tmp_path
    assert output_path.suffix == ".json"

    output_payload = json.loads(output_path.read_text(encoding="utf-8"))
    validate_payload("landed_cost_output", output_payload)
    assert output_payload["computed_at"] == "2026-03-10T08:30:45Z"


def test_render_script_contains_workspace_and_no_external_api_calls() -> None:
    script = render_landed_cost_execute_code_script(
        _base_input(),
        output_dir="/workspace",
        export_format="json",
    )

    assert 'OUTPUT_DIR = "/workspace"' in script
    assert "print(str(output_path))" in script
    assert "web_search" not in script
    assert "web_extract" not in script
    assert "requests" not in script
    assert "urllib" not in script


def test_rendered_script_executes_and_prints_absolute_output_path(
    tmp_path: Path,
) -> None:
    script = render_landed_cost_execute_code_script(
        _base_input(),
        output_dir=str(tmp_path),
        filename_stem="quote_001",
        export_format="json",
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(ROOT),
        check=True,
        text=True,
        capture_output=True,
    )

    output_path = Path(result.stdout.strip())
    assert output_path.is_absolute()
    assert output_path == (tmp_path / "quote_001.json")
    assert output_path.is_file()

    output_payload = json.loads(output_path.read_text(encoding="utf-8"))
    validate_payload("landed_cost_output", output_payload)


def test_compute_and_export_fails_fast_on_unsupported_export_format(
    tmp_path: Path,
) -> None:
    with pytest.raises(ExportGenerationError, match="Unsupported export_format"):
        compute_and_export_landed_cost(
            _base_input(),
            output_dir=str(tmp_path),
            export_format="csv",
            now_fn=_fixed_now,
        )
