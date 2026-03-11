"""Centralized user-facing outage/degraded-mode responses for Aptale."""

from __future__ import annotations

from enum import Enum

from aptale.formatters.whatsapp_markdown import bullets, join_sections, section


class UserMessageCode(str, Enum):
    """Canonical user-visible degraded-mode message codes."""

    PORTAL_OUTAGE = "portal_outage"
    PERSISTENT_CAPTCHA = "persistent_captcha"
    UNSUPPORTED_ROUTE = "unsupported_route"
    MISSING_FX_SOURCES = "missing_fx_sources"
    EXPORT_GENERATION_FAILURE = "export_generation_failure"
    WHATSAPP_ATTACHMENT_FAILURE = "whatsapp_attachment_failure"


class UserMessageError(ValueError):
    """Raised when an unknown user-message code is requested."""


_TEMPLATES: dict[UserMessageCode, dict[str, object]] = {
    UserMessageCode.PORTAL_OUTAGE: {
        "title": "Sourcing Blocked",
        "problem": "A required freight/customs portal is currently offline or unavailable.",
        "next_steps": (
            "Switch this leg to open-web search now.",
            "Retry official portal sourcing later.",
        ),
    },
    UserMessageCode.PERSISTENT_CAPTCHA: {
        "title": "Sourcing Blocked",
        "problem": "Portal sourcing is blocked by a persistent CAPTCHA challenge.",
        "next_steps": (
            "Switch this leg to open-web search now.",
            "Retry official portal sourcing later.",
        ),
    },
    UserMessageCode.UNSUPPORTED_ROUTE: {
        "title": "Route Unsupported",
        "problem": "This lane is not supported by the current routing coverage.",
        "next_steps": (
            "Send exact origin/destination countries and ports for open-web discovery.",
            "Share preferred freight/customs source hints for this route.",
        ),
    },
    UserMessageCode.MISSING_FX_SOURCES: {
        "title": "FX Sourcing Blocked",
        "problem": "No reliable FX sources were found for this run.",
        "next_steps": (
            "Retry with explicit base/quote currencies (for example: USD/NGN).",
            "Specify whether you want official rate, parallel rate, or both.",
        ),
    },
    UserMessageCode.EXPORT_GENERATION_FAILURE: {
        "title": "Export Failed",
        "problem": "The cost breakdown file could not be generated.",
        "next_steps": (
            "Retry export as CSV or PDF.",
            "Receive the cost breakdown inline in WhatsApp while export is retried.",
        ),
    },
    UserMessageCode.WHATSAPP_ATTACHMENT_FAILURE: {
        "title": "Delivery Failed",
        "problem": "The export file is ready, but WhatsApp attachment delivery failed.",
        "next_steps": (
            "Retry attachment delivery now.",
            "Receive a text summary while attachment delivery is retried.",
        ),
    },
}


def render_user_message(code: UserMessageCode | str, *, detail: str | None = None) -> str:
    """Render deterministic WhatsApp markdown for known degraded-mode failures."""
    resolved_code = _coerce_code(code)
    template = _TEMPLATES[resolved_code]

    sections = [
        section(
            str(template["title"]),
            f"{template['problem']} No estimate was guessed.",
        ),
    ]
    if detail is not None and str(detail).strip():
        sections.append(section("Observed Detail", _clean_detail(str(detail))))
    sections.append(
        section(
            "What You Can Do Next",
            bullets(list(template["next_steps"])),  # type: ignore[arg-type]
        )
    )
    return join_sections(sections)


def _coerce_code(code: UserMessageCode | str) -> UserMessageCode:
    if isinstance(code, UserMessageCode):
        return code
    try:
        return UserMessageCode(str(code).strip().lower())
    except Exception as exc:
        allowed = ", ".join(item.value for item in UserMessageCode)
        raise UserMessageError(
            f"Unknown user-message code: {code!r}. Allowed: {allowed}."
        ) from exc


def _clean_detail(detail: str) -> str:
    compact = " ".join(detail.split()).strip()
    if len(compact) <= 240:
        return compact
    return compact[:237] + "..."
