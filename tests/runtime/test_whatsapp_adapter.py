from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.runtime.whatsapp_adapter import (  # noqa: E402
    HermesWhatsAppQuoteAdapter,
    InMemoryQuoteLoopSessionStore,
    WhatsAppQuoteAdapterError,
)


def _fixed_now() -> datetime:
    return datetime(2026, 3, 11, 8, 0, 0, tzinfo=timezone.utc)


def _user_profile() -> dict[str, Any]:
    return {
        "country": "NG",
        "profit_margin_pct": 18.0,
        "timezone": "Africa/Lagos",
        "local_currency": "NGN",
    }


def _sample_event() -> dict[str, str]:
    return {
        "user_id": "2348011111111",
        "message_id": "wamid.888",
        "image_base64": "ZmFrZS1pbWFnZS1ieXRlcw==",
        "caption": "invoice image",
    }


def _sample_extraction_payload(*, missing_destination_port: bool = False) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "extraction_id": "invext_wamid.888",
        "message_id": "wamid.888",
        "extracted_at": "2026-03-11T08:00:00Z",
        "source_language": "zh",
        "target_language": "en",
        "invoice_number": "INV-888",
        "invoice_date": "2026-03-11",
        "incoterm": "FOB",
        "origin_country": "CN",
        "destination_country": "NG",
        "origin_port": "Guangzhou",
        "destination_port": None if missing_destination_port else "Lagos",
        "currency": "USD",
        "subtotal": 1000.0,
        "total": 1100.0,
        "total_weight_kg": 500.0,
        "items": [
            {
                "line_id": "1",
                "description": "Electronics batch",
                "quantity": 10,
                "unit": "carton",
                "unit_price": 110.0,
                "line_total": 1100.0,
                "weight_kg": 500.0,
                "country_of_origin": "CN",
                "hs_code": "851712",
                "hs_confidence": 0.93,
            }
        ],
        "extraction_confidence": 0.9,
        "needs_user_confirmation": True,
        "uncertainties": [],
    }


def _fake_multimodal_extractor(
    *,
    image_payload: str,
    extraction_prompt: str,
    translation_prompt: str,
    context: Mapping[str, Any],
) -> Mapping[str, Any]:
    assert image_payload
    assert extraction_prompt
    assert translation_prompt
    assert context["channel"] == "whatsapp"
    return _sample_extraction_payload()


def _fake_multimodal_extractor_missing_route(
    *,
    image_payload: str,
    extraction_prompt: str,
    translation_prompt: str,
    context: Mapping[str, Any],
) -> Mapping[str, Any]:
    assert image_payload
    assert extraction_prompt
    assert translation_prompt
    assert context["channel"] == "whatsapp"
    return _sample_extraction_payload(missing_destination_port=True)


def _build_delegate_outputs(
    *,
    extraction: Mapping[str, Any],
    local_currency: str,
) -> dict[str, str]:
    extraction_id = str(extraction["extraction_id"])
    base_currency = str(extraction["currency"])
    origin_country = str(extraction["origin_country"])
    destination_country = str(extraction["destination_country"])
    origin_port = extraction.get("origin_port")
    destination_port = extraction.get("destination_port")
    hs_code = str(extraction["items"][0]["hs_code"])

    freight_payload = {
        "schema_version": "1.0",
        "quote_id": f"fq_{extraction_id}",
        "extraction_id": extraction_id,
        "provider_name": "Freight Test Provider",
        "origin_country": origin_country,
        "destination_country": destination_country,
        "origin_port": origin_port,
        "destination_port": destination_port,
        "mode": "sea",
        "service_level": "standard",
        "transit_time_days": 28,
        "currency": base_currency,
        "quote_amount": 420.0,
        "charge_breakdown": [
            {"name": "base_freight", "amount": 420.0, "currency": base_currency}
        ],
        "valid_until": "2026-03-20T00:00:00Z",
        "source_type": "forwarder_portal",
        "sources": [
            {
                "source_url": "https://freight.example/quote",
                "source_title": "Freight Portal Quote",
                "retrieved_at": "2026-03-11T07:55:00Z",
                "method": "browserbase",
            }
        ],
        "captured_at": "2026-03-11T07:56:00Z",
    }

    customs_payload = {
        "schema_version": "1.0",
        "quote_id": f"cq_{extraction_id}",
        "extraction_id": extraction_id,
        "destination_country": destination_country,
        "assessment_basis": "invoice_value",
        "lines": [
            {
                "line_id": "1",
                "hs_code": hs_code,
                "duty_rate_pct": 10.0,
                "vat_rate_pct": 7.5,
                "additional_rate_pct": 1.0,
                "fixed_fee": None,
                "fixed_fee_currency": None,
                "legal_reference": "Tariff notice",
            }
        ],
        "source_type": "government_portal",
        "sources": [
            {
                "source_url": "https://customs.example/tariff",
                "source_title": "Customs Tariff",
                "retrieved_at": "2026-03-11T07:57:00Z",
                "method": "web_extract",
            }
        ],
        "captured_at": "2026-03-11T07:58:00Z",
    }

    fx_payload = {
        "schema_version": "1.0",
        "quote_id": f"xq_{extraction_id}",
        "extraction_id": extraction_id,
        "base_currency": base_currency,
        "quote_currency": local_currency,
        "official_rate": {
            "rate": 100.0,
            "provider_name": "CBN Test",
            "as_of": "2026-03-11T07:59:00Z",
            "source_url": "https://fx.example/official",
        },
        "parallel_rate": None,
        "spread_pct": None,
        "selected_rate_type": "official",
        "selected_rate": 100.0,
        "sources": [
            {
                "source_url": "https://fx.example/official",
                "source_title": "Official FX",
                "retrieved_at": "2026-03-11T07:59:00Z",
                "method": "web_search",
                "rate_type": "official",
            }
        ],
        "captured_at": "2026-03-11T08:00:00Z",
    }

    local_charges_payload = {
        "schema_version": "1.0",
        "quote_id": f"lq_{extraction_id}",
        "extraction_id": extraction_id,
        "destination_country": destination_country,
        "currency": local_currency,
        "total_amount": 5000.0,
        "lines": [
            {
                "name": "terminal_handling",
                "amount": 5000.0,
                "currency": local_currency,
                "notes": None,
            }
        ],
        "source_type": "official_portal",
        "sources": [
            {
                "source_url": "https://local.example/charges",
                "source_title": "Local Charges",
                "retrieved_at": "2026-03-11T08:00:00Z",
                "method": "web_extract",
            }
        ],
        "captured_at": "2026-03-11T08:00:00Z",
    }

    risk_notes_payload = {
        "schema_version": "1.0",
        "quote_id": f"rq_{extraction_id}",
        "extraction_id": extraction_id,
        "destination_country": destination_country,
        "risk_level": "medium",
        "notes": [
            {
                "code": "port_congestion",
                "title": "Port Congestion",
                "description": "Moderate congestion expected this week.",
                "impact_level": "medium",
                "recommendation": "Book discharge slots early.",
            }
        ],
        "source_type": "trade_advisory",
        "sources": [
            {
                "source_url": "https://risk.example/advisory",
                "source_title": "Trade Advisory",
                "retrieved_at": "2026-03-11T08:01:00Z",
                "method": "web_search",
            }
        ],
        "captured_at": "2026-03-11T08:01:00Z",
    }

    return {
        "freight": json.dumps(freight_payload),
        "customs": json.dumps(customs_payload),
        "fx": json.dumps(fx_payload),
        "local_charges": json.dumps(local_charges_payload),
        "risk_notes": json.dumps(risk_notes_payload),
    }


def test_handle_event_starts_quote_on_invoice_image() -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )

    result = adapter.handle_event(
        _sample_event(),
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: {},
        user_profile=_user_profile(),
        now_fn=_fixed_now,
    )

    assert result.handled is True
    assert result.status == "awaiting_clarification"
    assert result.next_step == "wait_for_user_confirmation"
    assert "*Extraction Summary*" in str(result.user_message)


def test_handle_event_confirmation_completes_quote_and_returns_attachment(
    tmp_path: Path,
) -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )

    adapter.handle_event(
        _sample_event(),
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: {},
        user_profile=_user_profile(),
        now_fn=_fixed_now,
    )

    result = adapter.handle_event(
        {"user_id": "2348011111111", "text": "Confirmed"},
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: _build_delegate_outputs(
            extraction=_sample_extraction_payload(),
            local_currency="NGN",
        ),
        user_profile=_user_profile(),
        export_format="csv",
        output_dir=tmp_path,
        now_fn=_fixed_now,
    )

    assert result.handled is True
    assert result.status == "completed"
    assert result.next_step == "send_whatsapp_export"
    assert result.user_message is not None and "*Quote Summary*" in result.user_message
    assert len(result.attachments) == 1
    assert result.attachments[0]["mime_type"] == "text/csv"
    assert Path(result.attachments[0]["path"]).is_file()


def test_handle_event_without_pending_state_is_unhandled() -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )
    result = adapter.handle_event(
        {"user_id": "2348000000000", "text": "hello"},
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: {},
        user_profile=_user_profile(),
        now_fn=_fixed_now,
    )
    assert result.handled is False
    assert result.status == "unhandled"
    assert result.next_step == "pass_to_default_agent"


def test_route_required_state_retries_with_route_followup(tmp_path: Path) -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )
    delegate_called = {"count": 0}

    adapter.session_store.set(
        "2348011111111",
        {
            "stage": "awaiting_route",
            "invoice_extraction": _sample_extraction_payload(missing_destination_port=True),
        },
    )

    def _delegate_runner(tasks: list[Mapping[str, Any]]) -> Mapping[str, str]:
        delegate_called["count"] += 1
        return _build_delegate_outputs(
            extraction={
                **_sample_extraction_payload(missing_destination_port=True),
                "destination_port": "Lagos",
            },
            local_currency="NGN",
        )

    completed_result = adapter.handle_event(
        {"user_id": "2348011111111", "text": "to Lagos port"},
        multimodal_extractor=_fake_multimodal_extractor_missing_route,
        delegate_task_runner=_delegate_runner,
        user_profile={
            "country": "NG",
            "profit_margin_pct": 18.0,
            "timezone": "Africa/Lagos",
            "local_currency": "NGN",
        },
        export_format="csv",
        output_dir=tmp_path,
        now_fn=_fixed_now,
    )
    assert delegate_called["count"] == 2
    assert completed_result.status == "completed"
    assert completed_result.next_step == "send_whatsapp_export"


def test_empty_clarification_reply_returns_prompt() -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )
    adapter.handle_event(
        _sample_event(),
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: {},
        user_profile=_user_profile(),
        now_fn=_fixed_now,
    )

    result = adapter.handle_event(
        {"user_id": "2348011111111", "text": "  "},
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: {},
        user_profile=_user_profile(),
        now_fn=_fixed_now,
    )
    assert result.status == "awaiting_clarification"
    assert "Reply with `Confirmed`" in str(result.user_message)


def test_missing_session_key_fails_fast() -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )
    with pytest.raises(WhatsAppQuoteAdapterError):
        adapter.handle_event(
            {"text": "hello"},
            multimodal_extractor=_fake_multimodal_extractor,
            delegate_task_runner=lambda tasks: {},
            user_profile=_user_profile(),
            now_fn=_fixed_now,
        )


def test_audio_followup_uses_transcript_and_returns_voice_reply(tmp_path: Path) -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )
    adapter.handle_event(
        _sample_event(),
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: {},
        user_profile=_user_profile(),
        now_fn=_fixed_now,
    )

    result = adapter.handle_event(
        {"user_id": "2348011111111", "audio": "/tmp/voice.ogg"},
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: _build_delegate_outputs(
            extraction=_sample_extraction_payload(),
            local_currency="NGN",
        ),
        user_profile=_user_profile(),
        export_format="csv",
        output_dir=tmp_path,
        now_fn=_fixed_now,
        voice_transcriber=lambda **_: "Confirmed",
        voice_synthesizer=lambda **_: {
            "type": "audio",
            "path": "/tmp/reply.ogg",
            "mime_type": "audio/ogg",
            "audio_as_voice": True,
        },
    )

    assert result.status == "completed"
    assert result.user_message is None
    assert any(item.get("type") == "audio" for item in result.attachments)


def test_text_followup_stays_text_even_with_voice_synthesizer(tmp_path: Path) -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )
    adapter.handle_event(
        _sample_event(),
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: {},
        user_profile=_user_profile(),
        now_fn=_fixed_now,
    )

    result = adapter.handle_event(
        {"user_id": "2348011111111", "text": "Confirmed"},
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: _build_delegate_outputs(
            extraction=_sample_extraction_payload(),
            local_currency="NGN",
        ),
        user_profile=_user_profile(),
        export_format="csv",
        output_dir=tmp_path,
        now_fn=_fixed_now,
        voice_synthesizer=lambda **_: {
            "type": "audio",
            "path": "/tmp/should-not-be-used.ogg",
            "mime_type": "audio/ogg",
            "audio_as_voice": True,
        },
    )

    assert result.status == "completed"
    assert result.user_message is not None
    assert not any(item.get("path") == "/tmp/should-not-be-used.ogg" for item in result.attachments)


def test_trade_radar_audio_request_returns_voice_reply() -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )

    result = adapter.handle_event(
        {"user_id": "2348011111111", "audio": "/tmp/request.ogg"},
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: {},
        user_profile=_user_profile(),
        now_fn=_fixed_now,
        voice_transcriber=lambda **_: "Track HS 850440 China->Nigeria, alert me daily 8am",
        voice_synthesizer=lambda **_: {
            "type": "audio",
            "path": "/tmp/radar.ogg",
            "mime_type": "audio/ogg",
            "audio_as_voice": True,
        },
        schedule_cronjob=lambda **_: {"job_id": "job-1", "status": "scheduled"},
    )

    assert result.status == "trade_radar_scheduled"
    assert result.user_message is None
    assert any(item.get("path") == "/tmp/radar.ogg" for item in result.attachments)


def test_trade_radar_detects_from_to_text_without_arrow() -> None:
    adapter = HermesWhatsAppQuoteAdapter(
        session_store=InMemoryQuoteLoopSessionStore(),
    )

    result = adapter.handle_event(
        {"user_id": "2348011111111", "text": "Track HS 850440 from China to Nigeria, alert me daily 8am"},
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: {},
        user_profile=_user_profile(),
        now_fn=_fixed_now,
        schedule_cronjob=lambda **_: {"job_id": "job-1", "status": "scheduled"},
    )

    assert result.handled is True
    assert result.status == "trade_radar_scheduled"
