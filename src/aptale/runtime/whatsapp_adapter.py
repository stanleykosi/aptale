"""Hermes-facing adapter for driving Aptale's quote loop over WhatsApp events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from aptale.flows.invoice_intake import MultimodalExtractor
from aptale.flows.quote_loop import (
    DelegateTaskRunner,
    QuoteLoopResult,
    begin_invoice_quote_loop,
    complete_invoice_quote_loop,
)


class WhatsAppQuoteAdapterError(RuntimeError):
    """Raised when a WhatsApp quote-loop event cannot be processed safely."""


class QuoteLoopSessionStore(Protocol):
    """Storage contract for quote-loop per-session state."""

    def get(self, session_key: str) -> Mapping[str, Any] | None:
        ...

    def set(self, session_key: str, state: Mapping[str, Any]) -> None:
        ...

    def delete(self, session_key: str) -> None:
        ...


class InMemoryQuoteLoopSessionStore:
    """Ephemeral in-memory store for quote-loop session state."""

    def __init__(self) -> None:
        self._state_by_session: dict[str, dict[str, Any]] = {}

    def get(self, session_key: str) -> Mapping[str, Any] | None:
        state = self._state_by_session.get(session_key)
        if state is None:
            return None
        return dict(state)

    def set(self, session_key: str, state: Mapping[str, Any]) -> None:
        self._state_by_session[session_key] = dict(state)

    def delete(self, session_key: str) -> None:
        self._state_by_session.pop(session_key, None)


@dataclass(frozen=True)
class WhatsAppDispatchResult:
    """Adapter output that can be passed to the gateway delivery layer."""

    handled: bool
    status: str
    next_step: str
    user_message: str | None
    attachments: tuple[Mapping[str, Any], ...] = ()
    source_trail: Mapping[str, Any] | None = None
    landed_cost_output: Mapping[str, Any] | None = None
    invoice_extraction: Mapping[str, Any] | None = None
    sourcing_failures: tuple[Mapping[str, Any], ...] = ()

    def as_mapping(self) -> dict[str, Any]:
        return {
            "handled": self.handled,
            "status": self.status,
            "next_step": self.next_step,
            "user_message": self.user_message,
            "attachments": [dict(item) for item in self.attachments],
            "source_trail": self.source_trail,
            "landed_cost_output": self.landed_cost_output,
            "invoice_extraction": self.invoice_extraction,
            "sourcing_failures": [dict(item) for item in self.sourcing_failures],
        }


@dataclass
class HermesWhatsAppQuoteAdapter:
    """Stateful adapter that routes WhatsApp turns into the Aptale quote loop."""

    session_store: QuoteLoopSessionStore

    def handle_event(
        self,
        whatsapp_event: Mapping[str, Any],
        *,
        multimodal_extractor: MultimodalExtractor,
        delegate_task_runner: DelegateTaskRunner,
        user_profile: Mapping[str, Any],
        image_quality_score: float | None = None,
        hs_confidence_threshold: float = 0.8,
        recent_chat_context: Sequence[str] | None = None,
        subagent_model: str | None = None,
        export_format: str = "pdf",
        output_dir: str | Path = "/workspace",
        filename_stem: str | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> WhatsAppDispatchResult:
        """
        Handle one WhatsApp event and return deterministic loop dispatch output.

        Behavior:
        - New invoice image: runs intake + clarification prompt stage.
        - Clarification reply with pending extraction: runs full sourcing/export stage.
        - Route-followup reply after route-required: retries using saved extraction.
        """
        if not isinstance(whatsapp_event, Mapping):
            raise WhatsAppQuoteAdapterError("whatsapp_event must be a mapping.")
        if not isinstance(user_profile, Mapping):
            raise WhatsAppQuoteAdapterError("user_profile must be a mapping.")
        if not callable(multimodal_extractor):
            raise WhatsAppQuoteAdapterError("multimodal_extractor must be callable.")
        if not callable(delegate_task_runner):
            raise WhatsAppQuoteAdapterError("delegate_task_runner must be callable.")

        session_key = _resolve_session_key(whatsapp_event)
        pending = self.session_store.get(session_key)
        has_image = _has_image_payload(whatsapp_event)
        message_text = _extract_message_text(whatsapp_event)

        if has_image:
            begin = begin_invoice_quote_loop(
                whatsapp_event,
                multimodal_extractor=multimodal_extractor,
                user_profile=user_profile,
                image_quality_score=image_quality_score,
                hs_confidence_threshold=hs_confidence_threshold,
                now_fn=now_fn,
            )
            if begin.status == "awaiting_clarification" and begin.invoice_extraction is not None:
                self.session_store.set(
                    session_key,
                    {
                        "stage": "awaiting_clarification",
                        "invoice_extraction": begin.invoice_extraction,
                    },
                )
            else:
                self.session_store.delete(session_key)
            return _to_dispatch_result(handled=True, result=begin)

        if pending is None:
            return WhatsAppDispatchResult(
                handled=False,
                status="unhandled",
                next_step="pass_to_default_agent",
                user_message=None,
            )

        stage = str(pending.get("stage", "")).strip()
        extraction = pending.get("invoice_extraction")
        if not isinstance(extraction, Mapping):
            self.session_store.delete(session_key)
            raise WhatsAppQuoteAdapterError(
                "Pending session state is invalid: invoice_extraction missing."
            )

        if stage == "awaiting_clarification":
            if not message_text:
                return WhatsAppDispatchResult(
                    handled=True,
                    status="awaiting_clarification",
                    next_step="wait_for_user_confirmation",
                    user_message="Reply with `Confirmed` or explicit field corrections.",
                    invoice_extraction=extraction,
                )
            loop_result = complete_invoice_quote_loop(
                invoice_extraction=extraction,
                clarification_response=message_text,
                delegate_task_runner=delegate_task_runner,
                user_profile=user_profile,
                recent_chat_context=recent_chat_context or (),
                subagent_model=subagent_model,
                export_format=export_format,
                output_dir=output_dir,
                filename_stem=filename_stem,
                now_fn=now_fn,
            )
            if loop_result.status == "route_required" and loop_result.invoice_extraction is not None:
                self.session_store.set(
                    session_key,
                    {
                        "stage": "awaiting_route",
                        "invoice_extraction": loop_result.invoice_extraction,
                    },
                )
            else:
                self.session_store.delete(session_key)
            return _to_dispatch_result(handled=True, result=loop_result)

        if stage == "awaiting_route":
            if not message_text:
                return WhatsAppDispatchResult(
                    handled=True,
                    status="route_required",
                    next_step="request_route_details",
                    user_message=(
                        "Reply with missing route details: origin country/port and "
                        "destination country/port."
                    ),
                    invoice_extraction=extraction,
                )
            route_context = list(recent_chat_context or ())
            route_context.append(message_text)
            loop_result = complete_invoice_quote_loop(
                invoice_extraction=extraction,
                clarification_response="Confirmed",
                delegate_task_runner=delegate_task_runner,
                user_profile=user_profile,
                recent_chat_context=route_context,
                subagent_model=subagent_model,
                export_format=export_format,
                output_dir=output_dir,
                filename_stem=filename_stem,
                now_fn=now_fn,
            )
            if loop_result.status == "route_required" and loop_result.invoice_extraction is not None:
                self.session_store.set(
                    session_key,
                    {
                        "stage": "awaiting_route",
                        "invoice_extraction": loop_result.invoice_extraction,
                    },
                )
            else:
                self.session_store.delete(session_key)
            return _to_dispatch_result(handled=True, result=loop_result)

        self.session_store.delete(session_key)
        raise WhatsAppQuoteAdapterError(f"Unsupported pending session stage: {stage!r}.")


def _to_dispatch_result(*, handled: bool, result: QuoteLoopResult) -> WhatsAppDispatchResult:
    attachments: tuple[Mapping[str, Any], ...] = ()
    if result.export_response is not None:
        raw = result.export_response.get("attachments")
        if isinstance(raw, list):
            attachments = tuple(item for item in raw if isinstance(item, Mapping))
    return WhatsAppDispatchResult(
        handled=handled,
        status=result.status,
        next_step=result.next_step,
        user_message=result.user_message,
        attachments=attachments,
        source_trail=result.source_trail,
        landed_cost_output=result.landed_cost_output,
        invoice_extraction=result.invoice_extraction,
        sourcing_failures=result.sourcing_failures,
    )


def _resolve_session_key(event: Mapping[str, Any]) -> str:
    for key in ("session_key", "session_id", "chat_id", "user_id"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise WhatsAppQuoteAdapterError(
        "whatsapp_event must include one of: session_key, session_id, chat_id, user_id."
    )


def _has_image_payload(event: Mapping[str, Any]) -> bool:
    for key in ("image_base64", "media_base64", "image"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, Mapping):
            content = value.get("base64")
            if isinstance(content, str) and content.strip():
                return True

    message = event.get("message")
    if isinstance(message, Mapping):
        for key in ("image_base64", "media_base64", "image"):
            value = message.get(key)
            if isinstance(value, str) and value.strip():
                return True
            if isinstance(value, Mapping):
                content = value.get("base64")
                if isinstance(content, str) and content.strip():
                    return True

    attachments = event.get("attachments")
    if isinstance(attachments, list):
        for item in attachments:
            if not isinstance(item, Mapping):
                continue
            kind = str(item.get("type", "")).strip().lower()
            if kind != "image":
                continue
            payload = item.get("base64")
            if isinstance(payload, str) and payload.strip():
                return True
    return False


def _extract_message_text(event: Mapping[str, Any]) -> str:
    for key in ("text", "body", "caption"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    message = event.get("message")
    if isinstance(message, str) and message.strip():
        return message.strip()
    if isinstance(message, Mapping):
        for key in ("text", "body", "caption"):
            value = message.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""
