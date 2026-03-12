from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.delegation.parse_results import (  # noqa: E402
    PartialJSONOutputError,
    ProseSubagentOutputError,
    SubagentResultValidationError,
    parse_subagent_output,
    parse_subagent_outputs,
)
from aptale.delegation.result_models import MissingCitationError  # noqa: E402


def _freight_payload() -> dict:
    return {
        "schema_version": "1.0",
        "quote_id": " fq_001 ",
        "extraction_id": " invext_001 ",
        "provider_name": " ACME Forwarding ",
        "origin_country": " cn ",
        "destination_country": " ng ",
        "origin_port": " Guangzhou ",
        "destination_port": " Lagos ",
        "mode": " SEA ",
        "service_level": " STANDARD ",
        "transit_time_days": 32,
        "currency": " usd ",
        "quote_amount": 450.0,
        "charge_breakdown": [
            {"name": " Base Freight ", "amount": 400.0, "currency": " usd "},
            {"name": " Fuel Surcharge ", "amount": 50.0, "currency": " usd "},
        ],
        "valid_until": None,
        "source_type": " FORWARDER_PORTAL ",
        "sources": [
            {
                "source_url": " https://freight.example/quote/123 ",
                "source_title": " Freight Portal Quote ",
                "retrieved_at": " 2026-03-10T10:00:00Z ",
                "method": " BROWSERBASE ",
            }
        ],
        "captured_at": " 2026-03-10T10:00:00Z ",
    }


def _customs_payload() -> dict:
    return {
        "schema_version": "1.0",
        "quote_id": "cq_001",
        "extraction_id": "invext_001",
        "destination_country": "ng",
        "assessment_basis": "Invoice_Value",
        "lines": [
            {
                "line_id": "1",
                "hs_code": "85.17.12",
                "duty_rate_pct": 10.0,
                "vat_rate_pct": 7.5,
                "additional_rate_pct": 1.0,
                "fixed_fee": None,
                "fixed_fee_currency": None,
                "legal_reference": " Section A ",
            }
        ],
        "source_type": "GOVERNMENT_PORTAL",
        "sources": [
            {
                "source_url": "https://customs.example/tariff/851712",
                "source_title": "Nigeria Customs Tariff",
                "retrieved_at": "2026-03-10T10:00:00Z",
                "method": "WEB_EXTRACT",
            }
        ],
        "captured_at": "2026-03-10T10:00:00Z",
    }


def _fx_payload() -> dict:
    return {
        "schema_version": "1.0",
        "quote_id": "xq_001",
        "extraction_id": "invext_001",
        "base_currency": "usd",
        "quote_currency": "ngn",
        "official_rate": {
            "rate": 1505.2,
            "provider_name": "CBN",
            "as_of": "2026-03-10T10:00:00Z",
            "source_url": "https://fx.example/official",
        },
        "parallel_rate": None,
        "spread_pct": None,
        "selected_rate_type": "OFFICIAL",
        "selected_rate": 1505.2,
        "sources": [
            {
                "source_url": "https://fx.example/official",
                "source_title": "Official Rate",
                "retrieved_at": "2026-03-10T10:00:00Z",
                "method": "WEB_SEARCH",
                "rate_type": "OFFICIAL",
            }
        ],
        "captured_at": "2026-03-10T10:00:00Z",
    }


def _local_charges_payload() -> dict:
    return {
        "schema_version": "1.0",
        "quote_id": "lq_001",
        "extraction_id": "invext_001",
        "destination_country": "ng",
        "currency": "ngn",
        "total_amount": 5000.0,
        "lines": [
            {
                "name": "terminal",
                "amount": 5000.0,
                "currency": "ngn",
                "notes": None,
            }
        ],
        "source_type": "official_portal",
        "sources": [
            {
                "source_url": "https://local.example/charges",
                "source_title": "Local Charges",
                "retrieved_at": "2026-03-10T10:00:00Z",
                "method": "web_extract",
            }
        ],
        "captured_at": "2026-03-10T10:00:00Z",
    }


def _risk_notes_payload() -> dict:
    return {
        "schema_version": "1.0",
        "quote_id": "rq_001",
        "extraction_id": "invext_001",
        "destination_country": "ng",
        "risk_level": "medium",
        "notes": [
            {
                "code": "port_congestion",
                "title": "Port Congestion",
                "description": "Congestion expected.",
                "impact_level": "medium",
                "recommendation": "Book slot early.",
            }
        ],
        "source_type": "trade_advisory",
        "sources": [
            {
                "source_url": "https://risk.example/advisory",
                "source_title": "Trade Advisory",
                "retrieved_at": "2026-03-10T10:05:00Z",
                "method": "web_search",
            }
        ],
        "captured_at": "2026-03-10T10:05:00Z",
    }


def test_parse_subagent_output_normalizes_and_validates_freight() -> None:
    raw_output = json.dumps(_freight_payload())
    result = parse_subagent_output(task_type="freight", raw_output=raw_output)

    assert result.task_type == "freight"
    assert result.schema_name == "freight_quote"
    assert result.payload["currency"] == "USD"
    assert result.payload["origin_country"] == "CN"
    assert result.payload["destination_country"] == "NG"
    assert result.payload["mode"] == "sea"
    assert result.payload["service_level"] == "standard"
    assert result.payload["source_type"] == "forwarder_portal"
    assert result.payload["sources"][0]["method"] == "browserbase"


def test_parse_subagent_output_rejects_prose_wrapped_json() -> None:
    raw_output = "Here is the result:\n" + json.dumps(_freight_payload())
    with pytest.raises(ProseSubagentOutputError):
        parse_subagent_output(task_type="freight", raw_output=raw_output)


def test_parse_subagent_output_rejects_partial_json() -> None:
    raw_output = json.dumps(_freight_payload())[:-1]
    with pytest.raises(PartialJSONOutputError):
        parse_subagent_output(task_type="freight", raw_output=raw_output)


def test_parse_subagent_output_rejects_missing_citations() -> None:
    payload = _freight_payload()
    payload["sources"] = []
    with pytest.raises(MissingCitationError):
        parse_subagent_output(task_type="freight", raw_output=json.dumps(payload))


def test_parse_subagent_output_rejects_schema_invalid_payload() -> None:
    payload = _customs_payload()
    del payload["quote_id"]
    with pytest.raises(SubagentResultValidationError):
        parse_subagent_output(task_type="customs", raw_output=json.dumps(payload))


def test_parse_subagent_outputs_parses_five_leg_mapping() -> None:
    parsed = parse_subagent_outputs(
        {
            "freight": json.dumps(_freight_payload()),
            "customs": json.dumps(_customs_payload()),
            "fx": json.dumps(_fx_payload()),
            "local_charges": json.dumps(_local_charges_payload()),
            "risk_notes": json.dumps(_risk_notes_payload()),
        }
    )

    assert set(parsed.keys()) == {"freight", "customs", "fx", "local_charges", "risk_notes"}
    assert parsed["customs"].payload["destination_country"] == "NG"
    assert parsed["customs"].payload["assessment_basis"] == "invoice_value"
    assert parsed["customs"].payload["lines"][0]["hs_code"] == "851712"
    assert parsed["fx"].payload["base_currency"] == "USD"
    assert parsed["fx"].payload["quote_currency"] == "NGN"
    assert parsed["fx"].payload["selected_rate_type"] == "official"
    assert parsed["local_charges"].payload["currency"] == "NGN"
    assert parsed["risk_notes"].payload["risk_level"] == "medium"
