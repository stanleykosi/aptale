from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "hermes" / "hooks" / "whatsapp-monitor" / "handler.py"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("aptale_whatsapp_monitor_hook", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load whatsapp-monitor handler module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gateway_startup_without_whatsapp_triggers_alert_payload() -> None:
    module = _load_hook_module()

    payload = module.build_alert_payload(
        event_type="gateway:startup",
        context={"platforms": ["telegram"]},
    )

    assert payload is not None
    assert payload["reason"] == "whatsapp_not_connected_on_startup"
    assert payload["severity"] == "warning"
    assert "hermes whatsapp" in payload["action_required"]


def test_gateway_startup_with_whatsapp_has_no_alert() -> None:
    module = _load_hook_module()

    payload = module.build_alert_payload(
        event_type="gateway:startup",
        context={"platforms": ["whatsapp", "telegram"]},
    )

    assert payload is None


def test_session_start_disconnect_context_triggers_critical_alert() -> None:
    module = _load_hook_module()

    payload = module.build_alert_payload(
        event_type="session:start",
        context={
            "platform": "whatsapp",
            "session_id": "sess_123",
            "error": "Baileys disconnected, QR re-pair required",
        },
    )

    assert payload is not None
    assert payload["reason"] == "whatsapp_session_disconnected_or_repair_required"
    assert payload["severity"] == "critical"
    assert payload["context"]["session_id"] == "sess_123"


def test_handle_posts_to_webhook_on_alert(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_hook_module()
    monkeypatch.setenv("ADMIN_ALERT_WEBHOOK_URL", "https://alerts.example/webhook")

    captured: dict[str, object] = {}

    def _fake_post(*, payload, webhook_url, timeout=5):  # type: ignore[no-untyped-def]
        captured["payload"] = payload
        captured["webhook_url"] = webhook_url
        captured["timeout"] = timeout
        return 200

    monkeypatch.setattr(module, "post_admin_alert", _fake_post)

    asyncio.run(
        module.handle(
            "gateway:startup",
            {"platforms": ["discord"]},
        )
    )

    assert captured["webhook_url"] == "https://alerts.example/webhook"
    assert captured["payload"]["reason"] == "whatsapp_not_connected_on_startup"


def test_handle_fails_fast_if_webhook_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_hook_module()
    monkeypatch.delenv("ADMIN_ALERT_WEBHOOK_URL", raising=False)

    with pytest.raises(RuntimeError):
        asyncio.run(
            module.handle(
                "session:start",
                {"platform": "whatsapp", "reason": "connection closed"},
            )
        )
