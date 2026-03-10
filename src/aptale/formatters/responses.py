"""Reusable WhatsApp-native response style helpers for Aptale."""

from __future__ import annotations

from typing import Iterable, Sequence

from aptale.calc.landed_cost import DISCLAIMER_TEXT

from .whatsapp_markdown import bullets, code_inline, join_sections, numbered, section


class ResponseFormatError(ValueError):
    """Raised when a response formatter receives invalid input."""


def render_short_broker_response(
    *,
    title: str,
    lines: Sequence[str],
    disclaimer: str | None = None,
) -> str:
    """Render a concise broker response for WhatsApp."""
    clean_title = _require_non_blank(title, name="title")
    clean_lines = _normalize_lines(lines, name="lines")

    sections = [section(clean_title, bullets(clean_lines))]
    if disclaimer is not None:
        sections.append(render_disclaimer(disclaimer_text=disclaimer))
    return join_sections(sections)


def render_detailed_broker_response(
    *,
    title: str,
    summary_lines: Sequence[str],
    detail_lines: Sequence[str],
    next_steps: Sequence[str] | None = None,
    disclaimer: str | None = None,
) -> str:
    """Render a detailed broker response with summary/details/next steps."""
    clean_title = _require_non_blank(title, name="title")
    clean_summary = _normalize_lines(summary_lines, name="summary_lines")
    clean_details = _normalize_lines(detail_lines, name="detail_lines")

    sections = [
        section(clean_title, bullets(clean_summary)),
        section("Details", bullets(clean_details)),
    ]
    if next_steps is not None:
        sections.append(section("Next Step", numbered(_normalize_lines(next_steps, name="next_steps"))))
    if disclaimer is not None:
        sections.append(render_disclaimer(disclaimer_text=disclaimer))
    return join_sections(sections)


def render_warning_response(
    *,
    title: str,
    issue: str,
    next_steps: Sequence[str],
) -> str:
    """Render warning/blocked-state response with explicit next steps."""
    clean_title = _require_non_blank(title, name="title")
    clean_issue = _require_non_blank(issue, name="issue")
    clean_next_steps = _normalize_lines(next_steps, name="next_steps")

    return join_sections(
        [
            section(clean_title, clean_issue),
            section("What You Can Send Next", bullets(clean_next_steps)),
        ]
    )


def render_disclaimer(*, disclaimer_text: str | None = None) -> str:
    """Render a disclaimer section using canonical text by default."""
    text = DISCLAIMER_TEXT if disclaimer_text is None else _require_non_blank(
        disclaimer_text, name="disclaimer_text"
    )
    return section("Disclaimer", text)


def render_correction_prompt(
    *,
    title: str,
    instructions: Sequence[str],
    example_edits: Sequence[str] | None = None,
    confirmation_phrase: str = "Confirmed",
) -> str:
    """Render correction guidance for WhatsApp clarification steps."""
    clean_title = _require_non_blank(title, name="title")
    clean_instructions = _normalize_lines(instructions, name="instructions")
    clean_confirmation_phrase = _require_non_blank(
        confirmation_phrase, name="confirmation_phrase"
    )

    steps = [
        f"Reply {code_inline(clean_confirmation_phrase)} if no changes are needed.",
        *clean_instructions,
    ]
    sections = [section(clean_title, numbered(steps))]

    if example_edits is not None:
        examples = [code_inline(item) for item in _normalize_lines(example_edits, name="example_edits")]
        sections.append(section("Correction Examples", bullets(examples)))
    return join_sections(sections)


def _require_non_blank(value: str, *, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ResponseFormatError(f"{name} must not be blank.")
    return text


def _normalize_lines(lines: Iterable[str], *, name: str) -> list[str]:
    normalized = [str(line).strip() for line in lines if str(line).strip()]
    if not normalized:
        raise ResponseFormatError(f"{name} must contain at least one non-empty entry.")
    return normalized
