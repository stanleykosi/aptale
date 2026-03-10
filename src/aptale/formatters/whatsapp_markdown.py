"""Helpers for compact WhatsApp-friendly markdown rendering."""

from __future__ import annotations

from typing import Iterable


def bold(text: str) -> str:
    """Render bold text for WhatsApp markdown."""
    return f"*{_clean_inline(text)}*"


def code_inline(text: str) -> str:
    """Render inline code for WhatsApp markdown."""
    return f"`{_clean_inline(text)}`"


def bullets(lines: Iterable[str]) -> str:
    """Render a bullet list."""
    return "\n".join(f"- {line}" for line in _non_empty(lines))


def numbered(lines: Iterable[str], start: int = 1) -> str:
    """Render a numbered list."""
    items = []
    index = start
    for line in _non_empty(lines):
        items.append(f"{index}. {line}")
        index += 1
    return "\n".join(items)


def section(title: str, body: str) -> str:
    """Render a section with a bold heading."""
    heading = bold(title)
    body = body.strip()
    if not body:
        return heading
    return f"{heading}\n{body}"


def join_sections(sections: Iterable[str]) -> str:
    """Join sections with WhatsApp-friendly spacing."""
    return "\n\n".join(part.strip() for part in sections if part and part.strip())


def _clean_inline(text: str) -> str:
    return " ".join(str(text).replace("\n", " ").split()).strip()


def _non_empty(lines: Iterable[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        stripped = str(line).strip()
        if stripped:
            out.append(stripped)
    return out

