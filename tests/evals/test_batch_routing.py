from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.delegation.build_tasks import build_sourcing_tasks  # noqa: E402
from aptale.delegation.parse_results import parse_subagent_outputs  # noqa: E402
from aptale.flows.clarify_extraction import (  # noqa: E402
    ClarifyExtractionError,
    process_clarification_response,
)
from aptale.flows.route_inference import infer_route_context  # noqa: E402


@dataclass
class MetricCounter:
    passed: int = 0
    failed: int = 0

    def mark(self, ok: bool) -> None:
        if ok:
            self.passed += 1
        else:
            self.failed += 1

    def as_dict(self) -> dict[str, int]:
        return {"pass": self.passed, "fail": self.failed}


def test_batch_routing_harness_records_pass_fail_metrics() -> None:
    dataset_file = Path(
        os.environ.get("APTALE_BATCH_ROUTING_DATASET", str(ROOT / "data" / "eval_invoices.jsonl"))
    ).resolve()
    metrics_path = Path(
        os.environ.get(
            "APTALE_BATCH_ROUTING_METRICS_PATH",
            str(ROOT / "runtime" / "evals" / "batch_routing_metrics.json"),
        )
    ).resolve()

    if not dataset_file.is_file():
        raise AssertionError(f"Dataset file not found: {dataset_file}")

    rows = _load_dataset_rows(dataset_file)
    target_rows = [row for row in rows if row.get("stage") in {"clarification", "routing_readiness"}]
    assert target_rows, "No clarification/routing_readiness rows found in evaluation dataset."

    extraction_confirmation = MetricCounter()
    sourcing_readiness = MetricCounter()
    delegation_trigger = MetricCounter()
    subagent_json_shape = MetricCounter()
    case_results: list[dict[str, Any]] = []

    for row in target_rows:
        row_id = str(row.get("id", "<missing-id>"))
        fixture_ref = row.get("fixture")
        if not isinstance(fixture_ref, str) or not fixture_ref.strip():
            raise AssertionError(f"{row_id}: fixture field is missing.")

        fixture_path = (ROOT / fixture_ref).resolve()
        if not fixture_path.is_file():
            raise AssertionError(f"{row_id}: fixture file not found: {fixture_path}")
        fixture = _read_json(fixture_path)

        expected_extraction = fixture.get("expected_invoice_extraction")
        if not isinstance(expected_extraction, Mapping):
            raise AssertionError(f"{row_id}: missing expected_invoice_extraction object in fixture.")

        clarification = fixture.get("clarification")
        if not isinstance(clarification, Mapping):
            raise AssertionError(f"{row_id}: missing clarification object in fixture.")
        user_reply = clarification.get("user_reply")
        if not isinstance(user_reply, str) or not user_reply.strip():
            raise AssertionError(f"{row_id}: clarification.user_reply is missing.")

        confirmation_ok = False
        readiness_ok = False
        delegation_ok = False
        subagent_shape_ok = False

        try:
            clarify_result = process_clarification_response(
                expected_extraction,
                user_reply,
                now_fn=_fixed_now,
            )
            confirmation_ok = clarify_result.status == "validated" and bool(clarify_result.can_source)
            extraction_confirmation.mark(confirmation_ok)

            profile = _build_eval_user_profile(fixture)
            route_result = infer_route_context(
                clarify_result.invoice_extraction,
                user_profile=profile,
                recent_chat_context=[],
            )
            readiness_ok = (
                route_result.status == "route_resolved"
                and bool(route_result.can_source)
                and isinstance(route_result.local_currency, str)
                and bool(route_result.local_currency.strip())
            )
            sourcing_readiness.mark(readiness_ok)

            if readiness_ok:
                tasks = build_sourcing_tasks(
                    invoice_extraction=route_result.invoice_extraction,
                    local_currency=str(route_result.local_currency),
                    user_profile=profile,
                    extraction_status="validated",
                    route_status=route_result.status,
                )
                expected_task_types = ["freight", "customs", "fx"]
                delegation_ok = [task.get("task_type") for task in tasks] == expected_task_types
                delegation_trigger.mark(delegation_ok)

                if delegation_ok:
                    raw_outputs = _build_stub_subagent_outputs(
                        extraction=route_result.invoice_extraction,
                        local_currency=str(route_result.local_currency),
                    )
                    parsed = parse_subagent_outputs(raw_outputs)
                    subagent_shape_ok = set(parsed.keys()) == {"freight", "customs", "fx"}
                    subagent_json_shape.mark(subagent_shape_ok)
                else:
                    subagent_json_shape.mark(False)
            else:
                delegation_trigger.mark(False)
                subagent_json_shape.mark(False)

        except ClarifyExtractionError:
            extraction_confirmation.mark(False)
            sourcing_readiness.mark(False)
            delegation_trigger.mark(False)
            subagent_json_shape.mark(False)

        case_results.append(
            {
                "id": row_id,
                "stage": row.get("stage"),
                "fixture": fixture_ref,
                "extraction_confirmation": confirmation_ok,
                "sourcing_readiness": readiness_ok,
                "delegation_triggered": delegation_ok,
                "subagent_json_shape_valid": subagent_shape_ok,
            }
        )

    metrics = {
        "dataset_file": str(dataset_file),
        "evaluated_cases": len(target_rows),
        "extraction_confirmation": extraction_confirmation.as_dict(),
        "sourcing_readiness": sourcing_readiness.as_dict(),
        "delegation_trigger": delegation_trigger.as_dict(),
        "subagent_json_shape": subagent_json_shape.as_dict(),
        "cases": case_results,
    }
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    assert extraction_confirmation.failed == 0, json.dumps(metrics, indent=2)
    assert sourcing_readiness.failed == 0, json.dumps(metrics, indent=2)
    assert delegation_trigger.failed == 0, json.dumps(metrics, indent=2)
    assert subagent_json_shape.failed == 0, json.dumps(metrics, indent=2)


def _load_dataset_rows(dataset_file: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with dataset_file.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AssertionError(f"Invalid JSONL at line {line_no} in {dataset_file}: {exc}") from exc
            if not isinstance(row, dict):
                raise AssertionError(f"Line {line_no} is not a JSON object.")
            prompt = row.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                raise AssertionError(f"Line {line_no} missing required non-empty prompt field.")
            rows.append(row)
    return rows


def _build_eval_user_profile(fixture: Mapping[str, Any]) -> dict[str, Any]:
    routing = fixture.get("routing_expectations")
    destination_country = None
    if isinstance(routing, Mapping):
        destination_country = routing.get("destination_country")
    if not isinstance(destination_country, str) or not destination_country.strip():
        destination_country = "NG"

    local_currency = _local_currency_for_country(destination_country.strip().upper())
    return {
        "country": destination_country.strip().upper(),
        "profit_margin_pct": 18.0,
        "timezone": "Africa/Lagos",
        "local_currency": local_currency,
    }


def _local_currency_for_country(country_code: str) -> str:
    mapping = {
        "NG": "NGN",
        "CN": "CNY",
        "TR": "TRY",
        "FR": "EUR",
        "IN": "INR",
        "BR": "BRL",
    }
    return mapping.get(country_code, "USD")


def _build_stub_subagent_outputs(
    *,
    extraction: Mapping[str, Any],
    local_currency: str,
) -> dict[str, str]:
    extraction_id = str(extraction["extraction_id"])
    origin_country = str(extraction["origin_country"])
    destination_country = str(extraction["destination_country"])
    origin_port = extraction.get("origin_port")
    destination_port = extraction.get("destination_port")
    base_currency = str(extraction["currency"])

    freight_payload = {
        "schema_version": "1.0",
        "quote_id": f"fq_{extraction_id}",
        "extraction_id": extraction_id,
        "provider_name": "Synthetic Freight Provider",
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
                "source_url": "https://freight.example/synthetic-quote",
                "source_title": "Synthetic Freight Quote",
                "retrieved_at": "2026-03-10T10:00:00Z",
                "method": "browserbase",
            }
        ],
        "captured_at": "2026-03-10T10:00:00Z",
    }

    hs_code = "851712"
    items = extraction.get("items")
    if isinstance(items, list) and items and isinstance(items[0], Mapping):
        value = items[0].get("hs_code")
        if isinstance(value, str) and value.strip():
            hs_code = value.strip()

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
                "legal_reference": "Synthetic Tariff Schedule",
            }
        ],
        "source_type": "government_portal",
        "sources": [
            {
                "source_url": "https://customs.example/synthetic-tariff",
                "source_title": "Synthetic Customs Tariff",
                "retrieved_at": "2026-03-10T10:00:00Z",
                "method": "web_extract",
            }
        ],
        "captured_at": "2026-03-10T10:00:00Z",
    }

    fx_payload = {
        "schema_version": "1.0",
        "quote_id": f"xq_{extraction_id}",
        "extraction_id": extraction_id,
        "base_currency": base_currency,
        "quote_currency": local_currency,
        "official_rate": {
            "rate": 100.0,
            "provider_name": "Synthetic Central Bank",
            "as_of": "2026-03-10T10:00:00Z",
            "source_url": "https://fx.example/synthetic-official",
        },
        "parallel_rate": None,
        "spread_pct": None,
        "selected_rate_type": "official",
        "selected_rate": 100.0,
        "sources": [
            {
                "source_url": "https://fx.example/synthetic-official",
                "source_title": "Synthetic Official FX",
                "retrieved_at": "2026-03-10T10:00:00Z",
                "method": "web_search",
                "rate_type": "official",
            }
        ],
        "captured_at": "2026-03-10T10:00:00Z",
    }

    return {
        "freight": json.dumps(freight_payload),
        "customs": json.dumps(customs_payload),
        "fx": json.dumps(fx_payload),
    }


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object at the root.")
    return data


def _fixed_now() -> datetime:
    return datetime(2026, 3, 11, 8, 0, 0, tzinfo=timezone.utc)
