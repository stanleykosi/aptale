from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "hermes" / "hooks" / "whatsapp-monitor" / "handler.py"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("aptale_gateway_whatsapp_monitor", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load whatsapp-monitor handler module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_disconnect_event_triggers_critical_alert_with_repair_action() -> None:
    module = _load_hook_module()

    payload = module.build_alert_payload(
        event_type="session:start",
        context={
            "platform": "whatsapp",
            "session_id": "sess_drop_001",
            "reason": "connection lost after network drop",
            "status": "disconnected",
        },
    )

    assert payload is not None
    assert payload["severity"] == "critical"
    assert payload["reason"] == "whatsapp_session_disconnected_or_repair_required"
    assert "temporary disconnects may auto-recover" in payload["message"].lower()
    assert "hermes whatsapp" in payload["action_required"]


def test_recovery_event_does_not_trigger_alert() -> None:
    module = _load_hook_module()

    payload = module.build_alert_payload(
        event_type="session:start",
        context={
            "platform": "whatsapp",
            "session_id": "sess_recovered_001",
            "status": "connected",
            "message": "session healthy",
        },
    )

    assert payload is None


def test_non_whatsapp_session_disconnect_is_ignored() -> None:
    module = _load_hook_module()

    payload = module.build_alert_payload(
        event_type="session:start",
        context={
            "platform": "telegram",
            "reason": "connection lost",
        },
    )

    assert payload is None


def test_gateway_startup_without_whatsapp_emits_warning_alert() -> None:
    module = _load_hook_module()

    payload = module.build_alert_payload(
        event_type="gateway:startup",
        context={"platforms": ["telegram", "discord"]},
    )

    assert payload is not None
    assert payload["severity"] == "warning"
    assert payload["reason"] == "whatsapp_not_connected_on_startup"

