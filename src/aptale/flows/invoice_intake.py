"""Invoice intake orchestration for WhatsApp image events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from uuid import uuid4

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import MalformedPayloadError, SchemaValidationError

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


class InvoiceIntakeError(RuntimeError):
    """Base error for invoice intake orchestration."""


class MissingImagePayloadError(InvoiceIntakeError):
    """Raised when a WhatsApp invoice event has no image attachment."""


class ExtractionOutputError(InvoiceIntakeError):
    """Raised when multimodal extraction output is malformed."""


class MultimodalExtractor(Protocol):
    """Callable contract used to trigger multimodal invoice extraction."""

    def __call__(
        self,
        *,
        image_payload: str,
        extraction_prompt: str,
        translation_prompt: str,
        context: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        ...


@dataclass(frozen=True)
class InvoiceIntakeResult:
    """Canonical result from the intake stage before sourcing."""

    status: str
    next_step: str
    clarify_required: bool
    invoice_extraction: Mapping[str, Any]


def orchestrate_invoice_intake(
    whatsapp_event: Mapping[str, Any],
    *,
    multimodal_extractor: MultimodalExtractor,
    user_profile: Mapping[str, Any] | None = None,
    now_fn: Callable[[], datetime] | None = None,
) -> InvoiceIntakeResult:
    """
    Run invoice intake through extraction + contract validation.

    This function explicitly stops at clarification handoff. It does not perform
    delegated sourcing.
    """
    if not isinstance(whatsapp_event, Mapping):
        raise MalformedPayloadError("whatsapp_event must be a mapping.")
    if not callable(multimodal_extractor):
        raise InvoiceIntakeError("multimodal_extractor must be callable.")

    now = now_fn or (lambda: datetime.now(timezone.utc))
    image_payload = _require_image_payload(whatsapp_event)
    context = build_intake_context(whatsapp_event, user_profile=user_profile)

    extraction_prompt = _load_prompt("invoice_extraction.md")
    translation_prompt = _load_prompt("language_detection_translation.md")
    raw_output = multimodal_extractor(
        image_payload=image_payload,
        extraction_prompt=extraction_prompt,
        translation_prompt=translation_prompt,
        context=context,
    )

    if not isinstance(raw_output, Mapping):
        raise ExtractionOutputError(
            "multimodal extractor must return a JSON-like object mapping."
        )

    candidate = dict(raw_output)
    candidate.setdefault("schema_version", "1.0")
    candidate.setdefault("extraction_id", _build_extraction_id(whatsapp_event))
    candidate.setdefault("extracted_at", _utc_iso(now()))

    message_id = whatsapp_event.get("message_id")
    if isinstance(message_id, str) and message_id.strip():
        candidate.setdefault("message_id", message_id.strip())

    try:
        validated = normalize_and_validate_payload("invoice_extraction", candidate)
    except (MalformedPayloadError, SchemaValidationError) as exc:
        raise ExtractionOutputError(
            "invoice extraction output failed canonical schema validation."
        ) from exc

    return InvoiceIntakeResult(
        status="awaiting_clarification",
        next_step="clarify_extraction",
        clarify_required=True,
        invoice_extraction=validated,
    )


def build_intake_context(
    whatsapp_event: Mapping[str, Any], user_profile: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Build focused context passed to multimodal extraction."""
    profile = dict(user_profile or {})
    preferred_language = (
        profile.get("language")
        or profile.get("locale")
        or whatsapp_event.get("target_language")
        or "en"
    )

    return {
        "channel": "whatsapp",
        "user_id": whatsapp_event.get("user_id"),
        "message_id": whatsapp_event.get("message_id"),
        "caption": whatsapp_event.get("caption"),
        "target_language": str(preferred_language).strip(),
        "source_language_hint": whatsapp_event.get("source_language"),
    }


def _load_prompt(filename: str) -> str:
    path = _PROMPTS_DIR / filename
    if not path.is_file():
        raise InvoiceIntakeError(f"Required prompt file missing: {path}")
    return path.read_text(encoding="utf-8").strip()


def _require_image_payload(whatsapp_event: Mapping[str, Any]) -> str:
    for key in ("image_base64", "media_base64", "image"):
        value = whatsapp_event.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise MissingImagePayloadError(
        "WhatsApp invoice intake requires an image payload (image_base64/media_base64)."
    )


def _build_extraction_id(whatsapp_event: Mapping[str, Any]) -> str:
    message_id = whatsapp_event.get("message_id")
    if isinstance(message_id, str) and message_id.strip():
        return f"invext_{message_id.strip()}"
    return f"invext_{uuid4().hex}"


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

