from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.flows.route_inference import infer_route_context  # noqa: E402


def _base_payload() -> dict:
    return {
        "schema_version": "1.0",
        "extraction_id": "invext_wamid.001",
        "message_id": "wamid.001",
        "extracted_at": "2026-03-10T00:00:00Z",
        "source_language": "zh",
        "target_language": "en",
        "invoice_number": "INV-501",
        "invoice_date": "2026-03-10",
        "incoterm": "FOB",
        "origin_country": None,
        "destination_country": None,
        "origin_port": None,
        "destination_port": None,
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
                "unit_price": 100.0,
                "line_total": 1000.0,
                "weight_kg": 500.0,
                "country_of_origin": "CN",
                "hs_code": "851712",
                "hs_confidence": 0.92,
            }
        ],
        "extraction_confidence": 0.88,
        "needs_user_confirmation": True,
        "uncertainties": [],
    }


def test_infer_route_from_profile_defaults() -> None:
    payload = _base_payload()
    result = infer_route_context(
        payload,
        user_profile={
            "origin_country": "CN",
            "destination_country": "NG",
            "origin_port": "Guangzhou",
            "destination_port": "Lagos",
            "local_currency": "NGN",
        },
    )

    assert result.status == "route_resolved"
    assert result.can_source is True
    assert result.local_currency == "NGN"
    assert result.invoice_extraction["origin_country"] == "CN"
    assert result.invoice_extraction["destination_port"] == "Lagos"
    assert result.route_required_prompt is None


def test_infer_route_from_recent_chat_context() -> None:
    payload = _base_payload()
    result = infer_route_context(
        payload,
        recent_chat_context=[
            "Please quote from Guangzhou port, China to Lagos, Nigeria."
        ],
    )

    assert result.status == "route_resolved"
    assert result.invoice_extraction["origin_country"] == "CN"
    assert result.invoice_extraction["destination_country"] == "NG"
    assert result.invoice_extraction["origin_port"] == "Guangzhou"
    assert result.invoice_extraction["destination_port"] == "Lagos"
    assert result.local_currency == "NGN"


def test_route_required_prompt_when_unresolved() -> None:
    payload = _base_payload()
    result = infer_route_context(payload, recent_chat_context=["Need shipping estimate"])

    assert result.status == "route_required"
    assert result.can_source is False
    assert result.route_required_prompt is not None
    assert "Route Required" in result.route_required_prompt
    assert "origin_country" in result.route_required_prompt
    assert "local_currency" in result.route_required_prompt
    assert len(result.missing_fields) > 0


def test_existing_route_is_preserved() -> None:
    payload = _base_payload()
    payload["origin_country"] = "TR"
    payload["destination_country"] = "NG"
    payload["origin_port"] = "Istanbul"
    payload["destination_port"] = "Lagos"

    result = infer_route_context(
        payload,
        user_profile={
            "origin_country": "CN",
            "destination_country": "NG",
            "origin_port": "Guangzhou",
            "destination_port": "Lagos",
            "local_currency": "NGN",
        },
    )

    assert result.status == "route_resolved"
    assert result.invoice_extraction["origin_country"] == "TR"
    assert result.invoice_extraction["origin_port"] == "Istanbul"
    assert result.local_currency == "NGN"

