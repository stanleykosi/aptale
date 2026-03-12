"""Hermes-facing adapter for driving Aptale's quote loop over WhatsApp events."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
import re
from typing import Any, Callable, Mapping, Protocol, Sequence

from aptale.alerts.schedule_trade_radar import (
    ScheduleTradeRadarError,
    schedule_trade_radar,
)
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


class VoiceTranscriber(Protocol):
    """Callable contract for converting WhatsApp voice payload to text."""

    def __call__(self, *, audio_payload: str, context: Mapping[str, Any]) -> str:
        ...


class VoiceSynthesizer(Protocol):
    """Callable contract for creating short voice summary attachments."""

    def __call__(self, *, summary_text: str, context: Mapping[str, Any]) -> Mapping[str, Any] | None:
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
    confidence_report: Mapping[str, Any] | None = None
    scenario_options: tuple[Mapping[str, Any], ...] = ()
    disruption_report: Mapping[str, Any] | None = None

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
            "confidence_report": self.confidence_report,
            "scenario_options": [dict(item) for item in self.scenario_options],
            "disruption_report": self.disruption_report,
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
        voice_transcriber: VoiceTranscriber | None = None,
        voice_synthesizer: VoiceSynthesizer | None = None,
        schedule_cronjob: Callable[..., Any] | None = None,
    ) -> WhatsAppDispatchResult:
        """
        Handle one WhatsApp event and return deterministic loop dispatch output.

        Behavior:
        - New invoice image: runs intake + clarification prompt stage.
        - Clarification reply with pending extraction: runs full sourcing/export stage.
        - Route-followup reply after route-required: retries using saved extraction.
        - Explicit trade-radar intent: schedules daily HS-lane radar cron job.
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
        audio_payload = _extract_audio_payload(whatsapp_event)
        prefer_voice_reply = bool(str(audio_payload or "").strip())
        message_text = _extract_message_text(whatsapp_event)
        transcript = ""

        if audio_payload and callable(voice_transcriber):
            transcript = str(
                voice_transcriber(
                    audio_payload=audio_payload,
                    context={"session_key": session_key, "event": dict(whatsapp_event)},
                )
                or ""
            ).strip()
        if not message_text and transcript:
            message_text = transcript

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
                clarification_text = transcript.strip()
                if not clarification_text and _looks_like_clarification(message_text):
                    clarification_text = message_text
                # Voice + image can complete quote in one turn.
                if clarification_text:
                    loop_result = complete_invoice_quote_loop(
                        invoice_extraction=begin.invoice_extraction,
                        clarification_response=clarification_text,
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
                    return _to_dispatch_result(
                        handled=True,
                        result=loop_result,
                        voice_synthesizer=voice_synthesizer,
                        session_key=session_key,
                        prefer_voice_reply=prefer_voice_reply,
                    )

                self.session_store.set(
                    session_key,
                    {
                        "stage": "awaiting_clarification",
                        "invoice_extraction": begin.invoice_extraction,
                    },
                )
            else:
                self.session_store.delete(session_key)
            return _to_dispatch_result(
                handled=True,
                result=begin,
                voice_synthesizer=voice_synthesizer,
                session_key=session_key,
                prefer_voice_reply=prefer_voice_reply,
            )

        if pending is None:
            if message_text and _looks_like_trade_radar_intent(message_text):
                if schedule_cronjob is None:
                    return _maybe_add_voice_reply(
                        dispatch=WhatsAppDispatchResult(
                            handled=True,
                            status="trade_radar_blocked",
                            next_step="configure_scheduler",
                            user_message=(
                                "Trade Radar scheduling is not available because schedule_cronjob is missing."
                            ),
                        ),
                        voice_synthesizer=voice_synthesizer,
                        session_key=session_key,
                        prefer_voice_reply=prefer_voice_reply,
                    )
                return _maybe_add_voice_reply(
                    dispatch=_handle_trade_radar_request(
                        message_text=message_text,
                        user_id=str(whatsapp_event.get("user_id") or session_key),
                        user_profile=user_profile,
                        schedule_cronjob=schedule_cronjob,
                        now_fn=now_fn,
                    ),
                    voice_synthesizer=voice_synthesizer,
                    session_key=session_key,
                    prefer_voice_reply=prefer_voice_reply,
                )

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
                return _maybe_add_voice_reply(
                    dispatch=WhatsAppDispatchResult(
                        handled=True,
                        status="awaiting_clarification",
                        next_step="wait_for_user_confirmation",
                        user_message="Reply with `Confirmed` or explicit field corrections.",
                        invoice_extraction=extraction,
                    ),
                    voice_synthesizer=voice_synthesizer,
                    session_key=session_key,
                    prefer_voice_reply=prefer_voice_reply,
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
            return _to_dispatch_result(
                handled=True,
                result=loop_result,
                voice_synthesizer=voice_synthesizer,
                session_key=session_key,
                prefer_voice_reply=prefer_voice_reply,
            )

        if stage == "awaiting_route":
            if not message_text:
                return _maybe_add_voice_reply(
                    dispatch=WhatsAppDispatchResult(
                        handled=True,
                        status="route_required",
                        next_step="request_route_details",
                        user_message=(
                            "Reply with missing route details: origin country/port and "
                            "destination country/port."
                        ),
                        invoice_extraction=extraction,
                    ),
                    voice_synthesizer=voice_synthesizer,
                    session_key=session_key,
                    prefer_voice_reply=prefer_voice_reply,
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
            return _to_dispatch_result(
                handled=True,
                result=loop_result,
                voice_synthesizer=voice_synthesizer,
                session_key=session_key,
                prefer_voice_reply=prefer_voice_reply,
            )

        self.session_store.delete(session_key)
        raise WhatsAppQuoteAdapterError(f"Unsupported pending session stage: {stage!r}.")


def _to_dispatch_result(
    *,
    handled: bool,
    result: QuoteLoopResult,
    voice_synthesizer: VoiceSynthesizer | None = None,
    session_key: str,
    prefer_voice_reply: bool = False,
) -> WhatsAppDispatchResult:
    attachments: list[Mapping[str, Any]] = []
    if result.export_response is not None:
        raw = result.export_response.get("attachments")
        if isinstance(raw, list):
            attachments.extend(item for item in raw if isinstance(item, Mapping))
    dispatch = WhatsAppDispatchResult(
        handled=handled,
        status=result.status,
        next_step=result.next_step,
        user_message=result.user_message,
        attachments=tuple(attachments),
        source_trail=result.source_trail,
        landed_cost_output=result.landed_cost_output,
        invoice_extraction=result.invoice_extraction,
        sourcing_failures=result.sourcing_failures,
        confidence_report=result.confidence_report,
        scenario_options=result.scenario_options,
        disruption_report=result.disruption_report,
    )
    voice_text = _build_voice_summary(result) if result.status == "completed" else result.user_message
    return _maybe_add_voice_reply(
        dispatch=dispatch,
        voice_synthesizer=voice_synthesizer,
        session_key=session_key,
        prefer_voice_reply=prefer_voice_reply,
        voice_text=str(voice_text or ""),
    )


def _handle_trade_radar_request(
    *,
    message_text: str,
    user_id: str,
    user_profile: Mapping[str, Any],
    schedule_cronjob: Callable[..., Any],
    now_fn: Callable[[], datetime] | None,
) -> WhatsAppDispatchResult:
    default_timezone = user_profile.get("timezone") if isinstance(user_profile.get("timezone"), str) else None
    sourcing_context = {
        "default_country": user_profile.get("country"),
        "default_currency": user_profile.get("local_currency"),
    }

    try:
        result = schedule_trade_radar(
            message_text,
            user_id=user_id,
            sourcing_context=sourcing_context,
            schedule_cronjob=schedule_cronjob,
            default_timezone=default_timezone,
            now_fn=now_fn,
        )
    except ScheduleTradeRadarError as exc:
        return WhatsAppDispatchResult(
            handled=True,
            status="trade_radar_failed",
            next_step="fix_trade_radar_request",
            user_message=f"Trade Radar scheduling failed: {exc}",
        )

    rule = result.plan.trade_radar_rule
    text = (
        "*Trade Radar Scheduled*\n"
        f"- HS: {rule['hs_code']}\n"
        f"- Route: {rule['origin_country']} -> {rule['destination_country']}\n"
        f"- Schedule: {rule['schedule_cron']} ({result.plan.timezone})\n"
        "- Delivery: origin\n"
        "- Daily update policy: always send delta (including no-change summary)."
    )
    return WhatsAppDispatchResult(
        handled=True,
        status="trade_radar_scheduled",
        next_step="trade_radar_active",
        user_message=text,
    )


def _build_voice_summary(result: QuoteLoopResult) -> str:
    output = result.landed_cost_output or {}
    total = output.get("total_landed_cost")
    currency = output.get("local_currency")
    confidence = result.confidence_report or {}
    band = confidence.get("overall_band")

    parts = ["Quote ready."]
    if isinstance(total, (int, float)) and isinstance(currency, str):
        parts.append(f"Total landed cost is {total:,.2f} {currency}.")
    if isinstance(band, str) and band:
        parts.append(f"Confidence is {band}.")
    if result.scenario_options:
        parts.append("Three plans generated: Fastest, Cheapest, and Balanced.")
    return " ".join(parts)


def _maybe_add_voice_reply(
    *,
    dispatch: WhatsAppDispatchResult,
    voice_synthesizer: VoiceSynthesizer | None,
    session_key: str,
    prefer_voice_reply: bool,
    voice_text: str | None = None,
) -> WhatsAppDispatchResult:
    if not dispatch.handled or not prefer_voice_reply or not callable(voice_synthesizer):
        return dispatch

    summary_text = str(voice_text or dispatch.user_message or "").strip()
    if not summary_text:
        return dispatch

    synthesized = voice_synthesizer(
        summary_text=summary_text,
        context={"session_key": session_key, "status": dispatch.status},
    )
    if not isinstance(synthesized, Mapping):
        return dispatch

    attachments = list(dispatch.attachments)
    attachments.append(dict(synthesized))
    # Audio-in requests should receive voice-first responses.
    return replace(dispatch, user_message=None, attachments=tuple(attachments))


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


def _extract_audio_payload(event: Mapping[str, Any]) -> str | None:
    for key in ("audio_base64", "voice_base64", "audio"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, Mapping):
            content = value.get("base64")
            if isinstance(content, str) and content.strip():
                return content.strip()

    message = event.get("message")
    if isinstance(message, Mapping):
        for key in ("audio_base64", "voice_base64", "audio"):
            value = message.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, Mapping):
                content = value.get("base64")
                if isinstance(content, str) and content.strip():
                    return content.strip()

    attachments = event.get("attachments")
    if isinstance(attachments, list):
        for item in attachments:
            if not isinstance(item, Mapping):
                continue
            kind = str(item.get("type", "")).strip().lower()
            if kind not in {"audio", "voice"}:
                continue
            payload = item.get("base64")
            if isinstance(payload, str) and payload.strip():
                return payload.strip()
    return None


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


def _looks_like_trade_radar_intent(text: str) -> bool:
    candidate = str(text).strip().lower()
    if not candidate:
        return False
    if not re.search(r"\btrack\b", candidate):
        return False
    if not re.search(r"\bhs\s*[0-9]{4,10}\b", candidate):
        return False
    if not ("->" in candidate or " to " in candidate):
        return False
    return True


def _looks_like_clarification(text: str) -> bool:
    candidate = str(text).strip()
    if not candidate:
        return False
    lowered = candidate.lower()
    if lowered in {"confirmed", "confirm", "yes", "ok", "proceed"}:
        return True
    if "=" in candidate:
        return True
    if lowered.startswith("remove "):
        return True
    return False
