"""Helpers for execute_code export artifacts in the canonical Aptale path."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Mapping


SUPPORTED_EXPORT_FORMATS = frozenset({"json"})


class ExportGenerationError(RuntimeError):
    """Raised when export artifact generation cannot proceed safely."""


def resolve_workspace_dir(output_dir: str | Path = "/workspace") -> Path:
    """Return an absolute workspace path, creating it when missing."""
    workspace = Path(output_dir)
    if not workspace.is_absolute():
        raise ExportGenerationError(
            f"output_dir must be absolute. Got: {output_dir!r}"
        )

    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def build_export_stem(extraction_id: str) -> str:
    """Build a filesystem-safe default filename stem."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", extraction_id).strip("_")
    if not slug:
        slug = "unknown"
    return f"landed_cost_{slug}"


def export_landed_cost_payload(
    payload: Mapping[str, Any],
    *,
    output_dir: str | Path = "/workspace",
    filename_stem: str | None = None,
    export_format: str = "json",
) -> Path:
    """
    Write landed-cost output artifact and return absolute path.

    Step 28 supports JSON output only. CSV/PDF are introduced in later steps.
    """
    if export_format not in SUPPORTED_EXPORT_FORMATS:
        raise ExportGenerationError(
            "Unsupported export_format: "
            f"{export_format!r}. Supported: {sorted(SUPPORTED_EXPORT_FORMATS)}"
        )

    workspace = resolve_workspace_dir(output_dir)
    extraction_id = str(payload.get("extraction_id", "unknown"))
    stem = filename_stem or build_export_stem(extraction_id)
    output_path = (workspace / f"{stem}.{export_format}").resolve()

    output_path.write_text(
        json.dumps(dict(payload), ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path
