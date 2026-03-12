from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.delegation.build_tasks import DelegationBuildError, build_sourcing_tasks  # noqa: E402


def _base_invoice_extraction() -> dict:
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
                "unit_price": 100.0,
                "line_total": 1000.0,
                "weight_kg": 500.0,
                "country_of_origin": "CN",
                "hs_code": "851712",
                "hs_confidence": 0.92,
            }
        ],
        "extraction_confidence": 0.88,
        "needs_user_confirmation": False,
        "uncertainties": [],
    }


def _user_profile() -> dict:
    return {
        "country": "NG",
        "profit_margin_pct": 18.5,
        "timezone": "Africa/Lagos",
    }


def test_build_sourcing_tasks_produces_five_exhaustive_tasks() -> None:
    tasks = build_sourcing_tasks(
        invoice_extraction=_base_invoice_extraction(),
        local_currency="NGN",
        user_profile=_user_profile(),
        extraction_status="validated",
        route_status="route_resolved",
        subagent_model="google/gemini-flash-2.0",
    )

    assert len(tasks) == 5
    assert [task["task_type"] for task in tasks] == [
        "freight",
        "customs",
        "fx",
        "local_charges",
        "risk_notes",
    ]
    assert tasks[0]["toolsets"] == ["browser", "web"]
    assert tasks[1]["toolsets"] == ["browser", "web"]
    assert tasks[2]["toolsets"] == ["web"]
    assert tasks[3]["toolsets"] == ["browser", "web"]
    assert tasks[4]["toolsets"] == ["web"]
    assert all(task["model"] == "google/gemini-flash-2.0" for task in tasks)

    for task in tasks:
        context = json.loads(task["context"])
        assert context["task_type"] == task["task_type"]
        assert context["input"]["invoice_extraction"]["extraction_id"] == "invext_wamid.001"
        assert context["input"]["user_profile"]["country"] == "NG"
        assert context["input"]["user_profile"]["profit_margin_pct"] == 18.5
        assert context["input"]["local_currency"] == "NGN"
        assert "clarify" in context["shared_rules"]
        assert "execute_code" in context["shared_rules"]


def test_build_sourcing_tasks_fails_if_extraction_not_validated() -> None:
    with pytest.raises(DelegationBuildError):
        build_sourcing_tasks(
            invoice_extraction=_base_invoice_extraction(),
            local_currency="NGN",
            user_profile=_user_profile(),
            extraction_status="awaiting_clarification",
            route_status="route_resolved",
        )


def test_build_sourcing_tasks_fails_if_route_unresolved() -> None:
    with pytest.raises(DelegationBuildError):
        build_sourcing_tasks(
            invoice_extraction=_base_invoice_extraction(),
            local_currency="NGN",
            user_profile=_user_profile(),
            extraction_status="validated",
            route_status="route_required",
        )


def test_build_sourcing_tasks_fails_without_default_margin() -> None:
    bad_profile = {"country": "NG"}
    with pytest.raises(DelegationBuildError):
        build_sourcing_tasks(
            invoice_extraction=_base_invoice_extraction(),
            local_currency="NGN",
            user_profile=bad_profile,
            extraction_status="validated",
            route_status="route_resolved",
        )
