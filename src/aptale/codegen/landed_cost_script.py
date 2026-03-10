"""Execute-code script template for deterministic landed-cost exports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping

from aptale.calc.landed_cost import calculate_landed_cost
from aptale.contracts import validate_landed_cost_input

from .export_helpers import (
    ExportGenerationError,
    export_landed_cost_payload,
)


class LandedCostScriptTemplateError(RuntimeError):
    """Raised when execute-code script template rendering fails."""


def compute_and_export_landed_cost(
    landed_cost_input: Mapping[str, Any],
    *,
    output_dir: str = "/workspace",
    filename_stem: str | None = None,
    export_format: str = "json",
    now_fn: Callable[[], Any] | None = None,
) -> Path:
    """Compute deterministic landed cost and write output artifact."""
    output_payload = calculate_landed_cost(landed_cost_input, now_fn=now_fn)
    return export_landed_cost_payload(
        output_payload,
        output_dir=output_dir,
        filename_stem=filename_stem,
        export_format=export_format,
    )


def render_landed_cost_execute_code_script(
    landed_cost_input: Mapping[str, Any],
    *,
    output_dir: str = "/workspace",
    filename_stem: str | None = None,
    export_format: str = "json",
) -> str:
    """
    Render Python source for Hermes `execute_code`.

    The script performs deterministic math locally and writes an artifact file.
    It prints only the absolute output file path for attachment handoff.
    """
    if not Path(output_dir).is_absolute():
        raise LandedCostScriptTemplateError(
            f"output_dir must be absolute. Got: {output_dir!r}"
        )

    try:
        validated = validate_landed_cost_input(landed_cost_input)
    except Exception as exc:  # pragma: no cover - wrapped fail-fast behavior
        raise LandedCostScriptTemplateError("Invalid landed_cost_input payload.") from exc

    payload_literal = json.dumps(validated, ensure_ascii=True, sort_keys=True, indent=2)
    output_dir_literal = json.dumps(output_dir, ensure_ascii=True)
    filename_stem_literal = json.dumps(filename_stem, ensure_ascii=True)
    export_format_literal = json.dumps(export_format, ensure_ascii=True)

    return f"""from __future__ import annotations
import pathlib
import sys

ROOT = pathlib.Path.cwd()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.calc.landed_cost import calculate_landed_cost
from aptale.codegen.export_helpers import export_landed_cost_payload

LANDED_COST_INPUT = {payload_literal}
OUTPUT_DIR = {output_dir_literal}
FILENAME_STEM = {filename_stem_literal}
EXPORT_FORMAT = {export_format_literal}

output_payload = calculate_landed_cost(LANDED_COST_INPUT)
output_path = export_landed_cost_payload(
    output_payload,
    output_dir=OUTPUT_DIR,
    filename_stem=FILENAME_STEM,
    export_format=EXPORT_FORMAT,
)
if not output_path.is_absolute():
    raise RuntimeError("Output path must be absolute.")
print(str(output_path))
"""


__all__ = [
    "ExportGenerationError",
    "LandedCostScriptTemplateError",
    "compute_and_export_landed_cost",
    "render_landed_cost_execute_code_script",
]
