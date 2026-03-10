"""Final quote response assembly for WhatsApp export delivery."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from aptale.contracts import validate_payload
from aptale.contracts.errors import ContractsError
from aptale.export.csv_export import CsvExportError, export_landed_cost_csv
from aptale.export.pdf_export import PdfExportError, export_landed_cost_pdf
from aptale.formatters.quote_summary import QuoteSummaryError, render_quote_summary


class SendExportError(RuntimeError):
    """Raised when WhatsApp export response assembly fails."""


class UnsupportedExportFormatError(SendExportError):
    """Raised when an unsupported export format is requested."""


@dataclass(frozen=True)
class ExportAttachment:
    """Document attachment metadata for WhatsApp delivery."""

    type: str
    path: str
    filename: str
    mime_type: str

    def as_mapping(self) -> dict[str, str]:
        return {
            "type": self.type,
            "path": self.path,
            "filename": self.filename,
            "mime_type": self.mime_type,
        }


@dataclass(frozen=True)
class SendExportResult:
    """Assembled outgoing WhatsApp response with document attachment."""

    message_markdown: str
    attachments: tuple[ExportAttachment, ...]

    def as_mapping(self) -> dict[str, Any]:
        return {
            "message_markdown": self.message_markdown,
            "attachments": [item.as_mapping() for item in self.attachments],
        }


def assemble_whatsapp_export_response(
    landed_cost_output: Mapping[str, Any],
    *,
    export_format: str,
    output_dir: str | Path = "/workspace",
    filename_stem: str | None = None,
) -> SendExportResult:
    """
    Build quote message and one export document attachment.

    The disclaimer is always included in message_markdown in addition to any
    file-level disclaimer/footer content.
    """
    if not isinstance(landed_cost_output, Mapping):
        raise SendExportError("landed_cost_output must be a mapping.")

    try:
        validated = validate_payload("landed_cost_output", landed_cost_output)
    except ContractsError as exc:
        raise SendExportError("Invalid landed_cost_output payload.") from exc

    fmt = str(export_format).strip().lower()
    path = _build_export_file(
        payload=validated,
        export_format=fmt,
        output_dir=output_dir,
        filename_stem=filename_stem,
    )

    if not path.is_absolute() or not path.is_file():
        raise SendExportError("Export attachment path must exist and be absolute.")

    try:
        message = render_quote_summary(validated)
    except QuoteSummaryError as exc:
        raise SendExportError("Failed to render WhatsApp quote summary.") from exc

    attachment = ExportAttachment(
        type="document",
        path=str(path),
        filename=path.name,
        mime_type=_mime_type_for_format(fmt),
    )
    return SendExportResult(message_markdown=message, attachments=(attachment,))


def _build_export_file(
    *,
    payload: Mapping[str, Any],
    export_format: str,
    output_dir: str | Path,
    filename_stem: str | None,
) -> Path:
    if export_format == "csv":
        try:
            return export_landed_cost_csv(
                payload, output_dir=output_dir, filename_stem=filename_stem
            )
        except CsvExportError as exc:
            raise SendExportError("CSV export generation failed.") from exc

    if export_format == "pdf":
        try:
            return export_landed_cost_pdf(
                payload, output_dir=output_dir, filename_stem=filename_stem
            )
        except PdfExportError as exc:
            raise SendExportError("PDF export generation failed.") from exc

    raise UnsupportedExportFormatError(
        f"Unsupported export_format {export_format!r}. Expected 'pdf' or 'csv'."
    )


def _mime_type_for_format(export_format: str) -> str:
    if export_format == "pdf":
        return "application/pdf"
    if export_format == "csv":
        return "text/csv"
    raise UnsupportedExportFormatError(
        f"Unsupported export_format {export_format!r}. Expected 'pdf' or 'csv'."
    )
