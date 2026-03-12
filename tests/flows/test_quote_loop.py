from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.flows.quote_loop import (  # noqa: E402
    begin_invoice_quote_loop,
    complete_invoice_quote_loop,
    run_invoice_quote_loop,
)


def _sample_extraction_payload() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "extraction_id": "invext_wamid.777",
        "message_id": "wamid.777",
        "extracted_at": "2026-03-11T08:00:00Z",
        "source_language": "zh",
        "target_language": "en",
        "invoice_number": "INV-777",
        "invoice_date": "2026-03-11",
        "incoterm": "FOB",
        "origin_country": "CN",
        "destination_country": "NG",
        "origin_port": "Guangzhou",
        "destination_port": "Lagos",
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


def _sample_event() -> dict[str, str]:
    return {
        "user_id": "2348011111111",
        "message_id": "wamid.777",
        "image_base64": "ZmFrZS1pbWFnZS1ieXRlcw==",
        "caption": "invoice image",
    }


def _user_profile() -> dict[str, Any]:
    return {
        "country": "NG",
        "profit_margin_pct": 18.0,
        "timezone": "Africa/Lagos",
        "local_currency": "NGN",
    }


def _fixed_now() -> datetime:
    return datetime(2026, 3, 11, 8, 0, 0, tzinfo=timezone.utc)


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

    return {
        "freight": json.dumps(freight_payload),
        "customs": json.dumps(customs_payload),
        "fx": json.dumps(fx_payload),
    }


def test_begin_invoice_quote_loop_returns_clarification_message() -> None:
    result = begin_invoice_quote_loop(
        _sample_event(),
        multimodal_extractor=_fake_multimodal_extractor,
        user_profile=_user_profile(),
        image_quality_score=0.9,
        now_fn=_fixed_now,
    )

    assert result.status == "awaiting_clarification"
    assert result.next_step == "wait_for_user_confirmation"
    assert "*Extraction Summary*" in result.user_message
    assert result.invoice_extraction is not None
    assert result.invoice_extraction["extraction_id"] == "invext_wamid.777"


def test_begin_invoice_quote_loop_fail_fast_on_blurry_image() -> None:
    result = begin_invoice_quote_loop(
        _sample_event(),
        multimodal_extractor=_fake_multimodal_extractor,
        user_profile=_user_profile(),
        image_quality_score=0.2,
        now_fn=_fixed_now,
    )

    assert result.status == "intake_blocked"
    assert result.next_step == "await_invoice_retry"
    assert "*Intake Blocked*" in result.user_message
    assert result.invoice_extraction is None


def test_complete_invoice_quote_loop_runs_to_export_and_source_trail(
    tmp_path: Path,
) -> None:
    extraction = _sample_extraction_payload()

    def delegate_runner(*, tasks: list[dict[str, Any]]) -> dict[str, str]:
        assert [task["task_type"] for task in tasks] == ["freight", "customs", "fx"]
        return _build_delegate_outputs(extraction=extraction, local_currency="NGN")

    result = complete_invoice_quote_loop(
        invoice_extraction=extraction,
        clarification_response="Confirmed",
        delegate_task_runner=delegate_runner,
        user_profile=_user_profile(),
        recent_chat_context=["from China to Nigeria"],
        export_format="csv",
        output_dir=tmp_path,
        now_fn=_fixed_now,
    )

    assert result.status == "completed"
    assert result.next_step == "send_whatsapp_export"
    assert "*Quote Summary*" in result.user_message
    assert result.route_status == "route_resolved"
    assert result.local_currency == "NGN"
    assert result.landed_cost_output is not None
    assert result.source_trail is not None
    assert len(result.source_trail["entries"]) >= 3
    assert result.export_response is not None
    attachment = result.export_response["attachments"][0]
    assert attachment["mime_type"] == "text/csv"
    assert Path(attachment["path"]).is_file()


def test_complete_invoice_quote_loop_returns_route_required_without_delegation() -> None:
    extraction = _sample_extraction_payload()
    extraction["destination_port"] = None
    called = {"value": False}

    def delegate_runner(*, tasks: list[dict[str, Any]]) -> dict[str, str]:
        called["value"] = True
        return {}

    result = complete_invoice_quote_loop(
        invoice_extraction=extraction,
        clarification_response="Confirmed",
        delegate_task_runner=delegate_runner,
        user_profile={
            "country": "NG",
            "profit_margin_pct": 18.0,
            "timezone": "Africa/Lagos",
        },
        recent_chat_context=[],
        now_fn=_fixed_now,
    )

    assert result.status == "route_required"
    assert result.next_step == "request_route_details"
    assert "*Route Required*" in result.user_message
    assert called["value"] is False


def test_complete_invoice_quote_loop_returns_sourcing_failure_message() -> None:
    extraction = _sample_extraction_payload()

    def delegate_runner(*, tasks: list[dict[str, Any]]) -> dict[str, str]:
        outputs = _build_delegate_outputs(extraction=extraction, local_currency="NGN")
        outputs["customs"] = "this is not strict JSON"
        return outputs

    result = complete_invoice_quote_loop(
        invoice_extraction=extraction,
        clarification_response="Confirmed",
        delegate_task_runner=delegate_runner,
        user_profile=_user_profile(),
        export_format="csv",
        output_dir=Path("/tmp"),
        now_fn=_fixed_now,
    )

    assert result.status == "sourcing_failed"
    assert result.next_step == "retry_failed_sourcing_legs"
    assert "Sourcing Leg Failed" in result.user_message
    assert len(result.sourcing_failures) == 1
    assert result.sourcing_failures[0]["task_type"] == "customs"
    assert result.sourcing_failures[0]["failure_code"] == "schema_violation"


def test_run_invoice_quote_loop_convenience_wrapper_completes(tmp_path: Path) -> None:
    result = run_invoice_quote_loop(
        _sample_event(),
        multimodal_extractor=_fake_multimodal_extractor,
        delegate_task_runner=lambda tasks: _build_delegate_outputs(
            extraction=_sample_extraction_payload(), local_currency="NGN"
        ),
        user_profile=_user_profile(),
        clarification_response="Confirmed",
        export_format="csv",
        output_dir=tmp_path,
        now_fn=_fixed_now,
    )

    assert result.status == "completed"
    assert result.export_response is not None
