"""User-facing fail-fast WhatsApp responses for intake failures."""

from __future__ import annotations

from typing import Any, Mapping

from aptale.errors.intake_errors import (
    BlurryImageFailure,
    IntakeFailure,
    MissingRouteFailure,
    UncertainHSCodeFailure,
    UnreadableTotalsFailure,
    detect_intake_failures,
)
from aptale.formatters.whatsapp_markdown import bullets, join_sections, section


def render_intake_failure_response(failure: IntakeFailure) -> str:
    """Render deterministic WhatsApp markdown for an intake failure."""
    if isinstance(failure, BlurryImageFailure):
        return _render_template(
            title="Intake Blocked",
            problem=(
                "The invoice image is too blurry to reliably extract route, totals, and item details."
            ),
            next_steps=[
                "Upload a clearer invoice photo (well-lit, full page, no cropping).",
                "Or type the missing route and totals manually.",
            ],
        )

    if isinstance(failure, MissingRouteFailure):
        return _render_template(
            title="Intake Blocked",
            problem="Origin or destination details are missing from the extraction.",
            next_steps=[
                "Reply with origin country/port and destination country/port.",
                "Or upload a clearer invoice image that shows route details.",
            ],
        )

    if isinstance(failure, UnreadableTotalsFailure):
        return _render_template(
            title="Intake Blocked",
            problem="Invoice subtotal or total could not be read reliably.",
            next_steps=[
                "Reply with subtotal and total values plus currency.",
                "Or upload a clearer image where totals are visible.",
            ],
        )

    if isinstance(failure, UncertainHSCodeFailure):
        return _render_template(
            title="Intake Blocked",
            problem="HS code inference is uncertain and cannot be used for sourcing.",
            next_steps=[
                "Reply with the correct HS code(s) for each line item.",
                "Or provide clearer item descriptions/spec sheets for re-extraction.",
            ],
        )

    return _render_template(
        title="Intake Blocked",
        problem=failure.user_message,
        next_steps=[
            "Upload a clearer invoice image.",
            "Or provide the missing details manually.",
        ],
    )


def build_intake_failure_response(
    extraction_payload: Mapping[str, Any],
    *,
    image_quality_score: float | None = None,
    hs_confidence_threshold: float = 0.8,
) -> str | None:
    """Return first fail-fast response text, or None when intake is safe to continue."""
    failures = detect_intake_failures(
        extraction_payload,
        image_quality_score=image_quality_score,
        hs_confidence_threshold=hs_confidence_threshold,
    )
    if not failures:
        return None
    return render_intake_failure_response(failures[0])


def _render_template(title: str, problem: str, next_steps: list[str]) -> str:
    sections = [
        section(title, problem),
        section("What You Can Send Next", bullets(next_steps)),
    ]
    return join_sections(sections)

