"""Reusable WhatsApp-native privacy notice and retention policy responses."""

from __future__ import annotations

from .whatsapp_markdown import bullets, code_inline, join_sections, section

DEFAULT_LOG_RETENTION_INTERVAL = "7 days"
SUPPORTED_PRIVACY_TRIGGERS = frozenset({"first_invoice_upload", "data_handling_request"})


class PrivacyNoticeError(ValueError):
    """Raised when privacy notice formatting input is invalid."""


def render_privacy_notice(
    *,
    trigger: str,
    log_retention_interval: str = DEFAULT_LOG_RETENTION_INTERVAL,
) -> str:
    """Render the Aptale privacy notice for first upload or data-handling requests."""
    trigger_key = _normalize_trigger(trigger)
    retention = _require_non_blank(log_retention_interval, name="log_retention_interval")

    sections = [
        section("Privacy Notice", _intro_for_trigger(trigger_key)),
        section(
            "Sensitive Data Boundaries",
            bullets(
                [
                    "Supplier names, invoice numbers, and raw pricing are treated as sensitive.",
                    "Sensitive invoice details are not written to broad operational logs.",
                    "The PII redaction hook sanitizes step/end activity logs before persistence.",
                ]
            ),
        ),
        section(
            "Retention & Flushing",
            bullets(
                [
                    f"Sanitized operational logs are flushed on a `{retention}` interval.",
                    "Durable memory stores broker preferences only (currency, route preferences, profit margin, timezone).",
                    "You can request a data-handling summary at any time.",
                ]
            ),
        ),
        section(
            "Need Help",
            (
                "Reply with "
                f"{code_inline('privacy')} or {code_inline('How do you handle my invoice data?')} "
                "for this notice again."
            ),
        ),
    ]
    return join_sections(sections)


def _normalize_trigger(trigger: str) -> str:
    key = str(trigger).strip().lower()
    if key not in SUPPORTED_PRIVACY_TRIGGERS:
        raise PrivacyNoticeError(
            "Unsupported privacy notice trigger. Expected one of: "
            + ", ".join(sorted(SUPPORTED_PRIVACY_TRIGGERS))
            + "."
        )
    return key


def _intro_for_trigger(trigger: str) -> str:
    if trigger == "first_invoice_upload":
        return (
            "Before I process your first invoice, here is how Aptale handles sensitive trade data."
        )
    return "Here is Aptale's data-handling policy for invoices, logs, and retained preferences."


def _require_non_blank(value: str, *, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise PrivacyNoticeError(f"{name} must not be blank.")
    return text
