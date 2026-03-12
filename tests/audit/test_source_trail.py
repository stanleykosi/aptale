from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.audit.source_trail import SourceTrailError, assemble_source_trail  # noqa: E402
from aptale.delegation.result_models import ParsedSubagentResult  # noqa: E402


def _parsed_result(task_type: str, payload: dict) -> ParsedSubagentResult:
    schema_name_by_task = {
        "freight": "freight_quote",
        "customs": "customs_quote",
        "fx": "fx_quote",
        "local_charges": "local_charge_quote",
        "risk_notes": "risk_note_quote",
    }
    return ParsedSubagentResult(
        task_type=task_type,
        schema_name=schema_name_by_task[task_type],
        payload=payload,
    )


def _freight_payload() -> dict:
    return {
        "quote_id": "fq_001",
        "extraction_id": "invext_001",
        "source_type": "forwarder_portal",
        "captured_at": "2026-03-10T09:00:00Z",
        "sources": [
            {
                "source_url": "https://freight.example/quotes/1",
                "retrieved_at": "2026-03-10T08:55:00Z",
                "method": "browserbase",
            }
        ],
    }


def _customs_payload() -> dict:
    return {
        "quote_id": "cq_001",
        "extraction_id": "invext_001",
        "source_type": "open_web",
        "captured_at": "2026-03-10T09:10:00Z",
        "sources": [
            {
                "source_url": "https://customs.example/tariff/851712",
                "retrieved_at": "2026-03-10T09:08:00Z",
                "method": "web_extract",
            }
        ],
    }


def _fx_payload() -> dict:
    return {
        "quote_id": "xq_001",
        "extraction_id": "invext_001",
        "captured_at": "2026-03-10T09:20:00Z",
        "sources": [
            {
                "source_url": "https://fx.example/official",
                "retrieved_at": "2026-03-10T09:18:00Z",
                "method": "web_search",
                "rate_type": "official",
            },
            {
                "source_url": "https://fx.example/parallel",
                "retrieved_at": "2026-03-10T09:19:00Z",
                "method": "web_extract",
                "rate_type": "parallel",
            },
        ],
    }


def _local_charges_payload() -> dict:
    return {
        "quote_id": "lq_001",
        "extraction_id": "invext_001",
        "source_type": "official_portal",
        "captured_at": "2026-03-10T09:22:00Z",
        "sources": [
            {
                "source_url": "https://local.example/charges",
                "retrieved_at": "2026-03-10T09:21:00Z",
                "method": "web_extract",
            }
        ],
    }


def test_assemble_source_trail_includes_urls_timestamps_types_and_discovery_channel() -> None:
    parsed_results = {
        "freight": _parsed_result("freight", _freight_payload()),
        "customs": _parsed_result("customs", _customs_payload()),
        "fx": _parsed_result("fx", _fx_payload()),
        "local_charges": _parsed_result("local_charges", _local_charges_payload()),
    }

    trail = assemble_source_trail(parsed_results, assembled_at="2026-03-11T12:00:00Z")

    assert trail.extraction_id == "invext_001"
    assert trail.assembled_at == "2026-03-11T12:00:00Z"
    assert len(trail.entries) == 5

    freight_entry = next(entry for entry in trail.entries if entry.task_type == "freight")
    customs_entry = next(entry for entry in trail.entries if entry.task_type == "customs")
    fx_entries = [entry for entry in trail.entries if entry.task_type == "fx"]
    local_entry = next(entry for entry in trail.entries if entry.task_type == "local_charges")

    assert freight_entry.source_url == "https://freight.example/quotes/1"
    assert freight_entry.retrieved_at == "2026-03-10T08:55:00Z"
    assert freight_entry.source_type == "forwarder_portal"
    assert freight_entry.discovery_channel == "official_portal"

    assert customs_entry.source_type == "open_web"
    assert customs_entry.discovery_channel == "open_web"

    assert {entry.source_type for entry in fx_entries} == {"official_rate", "parallel_rate"}
    assert {entry.discovery_channel for entry in fx_entries} == {"official_portal", "open_web"}
    assert local_entry.discovery_channel == "official_portal"

    mapping = trail.as_mapping()
    assert mapping["extraction_id"] == "invext_001"
    assert len(mapping["entries"]) == 5


def test_assemble_source_trail_fails_when_required_task_is_missing() -> None:
    parsed_results = {
        "freight": _parsed_result("freight", _freight_payload()),
        "customs": _parsed_result("customs", _customs_payload()),
        "local_charges": _parsed_result("local_charges", _local_charges_payload()),
    }

    with pytest.raises(SourceTrailError):
        assemble_source_trail(parsed_results)


def test_assemble_source_trail_fails_on_mismatched_extraction_ids() -> None:
    customs_payload = _customs_payload()
    customs_payload["extraction_id"] = "invext_other"
    parsed_results = {
        "freight": _parsed_result("freight", _freight_payload()),
        "customs": _parsed_result("customs", customs_payload),
        "fx": _parsed_result("fx", _fx_payload()),
        "local_charges": _parsed_result("local_charges", _local_charges_payload()),
    }

    with pytest.raises(SourceTrailError):
        assemble_source_trail(parsed_results)


def test_assemble_source_trail_fails_on_unsupported_source_type() -> None:
    customs_payload = _customs_payload()
    customs_payload["source_type"] = "legacy_portal"
    parsed_results = {
        "freight": _parsed_result("freight", _freight_payload()),
        "customs": _parsed_result("customs", customs_payload),
        "fx": _parsed_result("fx", _fx_payload()),
        "local_charges": _parsed_result("local_charges", _local_charges_payload()),
    }

    with pytest.raises(SourceTrailError):
        assemble_source_trail(parsed_results)
