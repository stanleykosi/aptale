from __future__ import annotations

import asyncio
import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "hermes" / "hooks" / "pii-redactor" / "handler.py"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("aptale_pii_redactor_hook", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load pii-redactor handler module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_agent_end_redacts_sensitive_fields_without_mutating_context(tmp_path: Path) -> None:
    module = _load_hook_module()
    module.LOG_FILE = tmp_path / "activity.log"

    context = {
        "platform": "whatsapp",
        "user_id": "2348012345678",
        "message": (
            "Supplier: Acme Imports Ltd; invoice number: INV-2026-9001; "
            "pickup at 742 Evergreen Road, Springfield; total: USD 12340.50"
        ),
        "supplier_name": "Acme Imports Ltd",
        "invoice_number": "INV-2026-9001",
        "supplier_address": "742 Evergreen Road, Springfield",
        "total_amount": 12340.50,
        "response": (
            "Invoice INV-2026-9001 total $12,340.50 for Acme Imports Ltd"
        ),
    }

    original = copy.deepcopy(context)
    asyncio.run(module.handle("agent:end", context))

    assert context == original
    entries = _read_jsonl(module.LOG_FILE)
    assert len(entries) == 1

    logged_context = entries[0]["context"]
    assert logged_context["supplier_name"] == module.REDACTED_SUPPLIER
    assert logged_context["invoice_number"] == module.REDACTED_INVOICE
    assert logged_context["supplier_address"] == module.REDACTED_ADDRESS
    assert logged_context["total_amount"] == module.REDACTED_PRICE
    assert module.REDACTED_SUPPLIER in logged_context["response"]
    assert module.REDACTED_INVOICE in logged_context["response"]
    assert module.REDACTED_PRICE in logged_context["response"]
    assert module.REDACTED_PRICE in logged_context["message"]

    serialized = json.dumps(entries[0], ensure_ascii=False)
    assert "Acme Imports Ltd" not in serialized
    assert "742 Evergreen Road" not in serialized
    assert "INV-2026-9001" not in serialized
    assert "$12,340.50" not in serialized


def test_agent_step_redacts_nested_pricing_and_supplier_fields(tmp_path: Path) -> None:
    module = _load_hook_module()
    module.LOG_FILE = tmp_path / "activity.log"

    context = {
        "platform": "whatsapp",
        "iteration": 2,
        "tool_names": ["browser_navigate", "web_search"],
        "extraction": {
            "supplier_name": "Global Seller LLC",
            "line_items": [
                {"description": "Widget A", "unit_price": 98.2},
                {"description": "Widget B", "unit_price": 45.0},
            ],
        },
    }

    asyncio.run(module.handle("agent:step", context))
    entries = _read_jsonl(module.LOG_FILE)

    assert len(entries) == 1
    logged_context = entries[0]["context"]
    assert logged_context["extraction"]["supplier_name"] == module.REDACTED_SUPPLIER
    assert logged_context["extraction"]["line_items"][0]["unit_price"] == module.REDACTED_PRICE
    assert logged_context["extraction"]["line_items"][1]["unit_price"] == module.REDACTED_PRICE


def test_unsupported_events_are_ignored(tmp_path: Path) -> None:
    module = _load_hook_module()
    module.LOG_FILE = tmp_path / "activity.log"

    asyncio.run(module.handle("agent:start", {"message": "hello"}))

    assert not module.LOG_FILE.exists()
