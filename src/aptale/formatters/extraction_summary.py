"""Render canonical invoice extraction summaries for WhatsApp clarify flow."""

from __future__ import annotations

from typing import Any, Mapping

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError

from .whatsapp_markdown import bold, bullets, code_inline, join_sections, numbered, section

CONFIRMATION_PHRASE = "Confirmed"


class ExtractionSummaryError(ValueError):
    """Raised when extraction payload cannot be summarized safely."""


def render_extraction_summary(extraction_payload: Mapping[str, Any]) -> str:
    """
    Render a concise WhatsApp markdown extraction summary.

    This formatter is intended for clarify-gated user confirmation before any
    sourcing workflow begins.
    """
    if not isinstance(extraction_payload, Mapping):
        raise ExtractionSummaryError("Extraction payload must be a mapping.")

    try:
        payload = normalize_and_validate_payload("invoice_extraction", extraction_payload)
    except ContractsError as exc:
        raise ExtractionSummaryError(
            "Extraction payload is invalid for summary rendering."
        ) from exc

    meta_lines = [
        f"{bold('Invoice')}: {payload.get('invoice_number') or 'Not provided'}",
        f"{bold('Date')}: {payload.get('invoice_date') or 'Not provided'}",
        f"{bold('Route')}: {_route_text(payload)}",
        f"{bold('Currency')}: {payload['currency']}",
        f"{bold('Total')}: {_fmt_amount(payload['total'])}",
        f"{bold('Weight (kg)')}: {_fmt_optional_number(payload.get('total_weight_kg'))}",
        f"{bold('Incoterm')}: {payload.get('incoterm') or 'Not provided'}",
    ]

    item_lines = []
    for idx, item in enumerate(payload["items"], start=1):
        item_lines.append(
            (
                f"{idx}) {item['description']} | "
                f"qty {item['quantity']} {item['unit']} | "
                f"hs {code_inline(item['hs_code'] or 'unknown')}"
            )
        )

    sections = [
        section("Extraction Summary", bullets(meta_lines)),
        section("Line Items", "\n".join(item_lines)),
    ]

    uncertainties = payload.get("uncertainties") or []
    if uncertainties:
        sections.append(section("Needs Confirmation", bullets(uncertainties)))

    corrections_guidance = numbered(
        [
            f"Reply {code_inline(CONFIRMATION_PHRASE)} to proceed.",
            "Or send corrections using a field path and value.",
            f"Example: {code_inline('destination_port = \"Tin Can Island\"')}",
            f"Example: {code_inline('items[0].hs_code = \"851712\"')}",
        ]
    )
    sections.append(section("Next Step", corrections_guidance))

    return join_sections(sections)


def _fmt_amount(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:,.2f}"
    return str(value)


def _fmt_optional_number(value: Any) -> str:
    if value is None:
        return "Not provided"
    if isinstance(value, (int, float)):
        return f"{value:,.2f}"
    return str(value)


def _route_text(payload: Mapping[str, Any]) -> str:
    origin_country = payload.get("origin_country") or "??"
    destination_country = payload.get("destination_country") or "??"
    origin_port = payload.get("origin_port") or "unknown port"
    destination_port = payload.get("destination_port") or "unknown port"
    return (
        f"{origin_country} ({origin_port}) -> "
        f"{destination_country} ({destination_port})"
    )

