"""Confirmation/correction gate for extracted invoice payloads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError
from aptale.formatters.extraction_summary import render_extraction_summary
from aptale.parsers.user_corrections import (
    CorrectionApplyError,
    CorrectionParseError,
    apply_invoice_corrections,
    parse_user_corrections,
)


class ClarifyExtractionError(RuntimeError):
    """Base error for clarification gating."""


class UnconfirmedExtractionError(ClarifyExtractionError):
    """Raised when downstream sourcing is attempted before validation."""


@dataclass(frozen=True)
class ClarifyExtractionResult:
    """Canonical result from clarification gating."""

    status: str
    next_step: str
    clarify_required: bool
    can_source: bool
    invoice_extraction: Mapping[str, Any]
    clarify_message: str
    invoice_correction: Mapping[str, Any] | None = None


def begin_clarification(extraction_payload: Mapping[str, Any]) -> ClarifyExtractionResult:
    """Prepare and return clarify-facing summary for user confirmation/corrections."""
    payload = _validate_extraction(extraction_payload)
    return ClarifyExtractionResult(
        status="awaiting_clarification",
        next_step="wait_for_user_confirmation",
        clarify_required=True,
        can_source=False,
        invoice_extraction=payload,
        clarify_message=render_extraction_summary(payload),
        invoice_correction=None,
    )


def process_clarification_response(
    extraction_payload: Mapping[str, Any],
    user_response: str,
    *,
    now_fn: Callable[[], datetime] | None = None,
) -> ClarifyExtractionResult:
    """
    Apply user confirmation/corrections and gate sourcing until validated.

    Returns a validated state only when user explicitly confirms or provides
    schema-valid corrections.
    """
    payload = _validate_extraction(extraction_payload)
    now = now_fn or (lambda: datetime.now(timezone.utc))

    try:
        correction = parse_user_corrections(
            user_response,
            extraction_id=payload["extraction_id"],
            now_fn=now,
        )
    except CorrectionParseError as exc:
        raise ClarifyExtractionError("Failed to parse clarification response.") from exc

    if correction["confirmation_status"] == "confirmed":
        return ClarifyExtractionResult(
            status="validated",
            next_step="ready_for_sourcing",
            clarify_required=False,
            can_source=True,
            invoice_extraction=payload,
            clarify_message=render_extraction_summary(payload),
            invoice_correction=correction,
        )

    try:
        corrected_payload = apply_invoice_corrections(payload, correction)
        validated_corrected = _validate_extraction(corrected_payload)
    except (CorrectionApplyError, ContractsError) as exc:
        raise ClarifyExtractionError(
            "Failed to apply corrections to extraction payload."
        ) from exc

    return ClarifyExtractionResult(
        status="validated",
        next_step="ready_for_sourcing",
        clarify_required=False,
        can_source=True,
        invoice_extraction=validated_corrected,
        clarify_message=render_extraction_summary(validated_corrected),
        invoice_correction=correction,
    )


def assert_sourcing_allowed(result: ClarifyExtractionResult) -> None:
    """Fail fast if downstream sourcing is attempted before validation."""
    if result.status != "validated" or not result.can_source:
        raise UnconfirmedExtractionError(
            "Invoice extraction is not validated. Clarification must complete first."
        )


def _validate_extraction(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ClarifyExtractionError("extraction_payload must be a mapping.")
    try:
        return normalize_and_validate_payload("invoice_extraction", payload)
    except ContractsError as exc:
        raise ClarifyExtractionError("Invalid invoice extraction payload.") from exc

