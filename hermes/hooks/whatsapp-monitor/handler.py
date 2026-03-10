"""Hermes hook for WhatsApp/Baileys session health monitoring."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from typing import Any, Mapping
from urllib.request import Request, urlopen

REPAIR_COMMAND = "hermes whatsapp"
WEBHOOK_ENV_VAR = "ADMIN_ALERT_WEBHOOK_URL"

_DISCONNECT_MARKERS = (
    "disconnect",
    "disconnected",
    "connection closed",
    "connection lost",
    "logged out",
    "restart required",
)
_REPAIR_MARKERS = (
    "re-pair",
    "repair",
    "pairing",
    "qr",
    "link a device",
    "pair again",
)


async def handle(event_type: str, context: dict) -> None:
    """Send an admin alert when WhatsApp session health indicates re-pair risk."""
    payload = build_alert_payload(event_type=event_type, context=context)
    if payload is None:
        return

    webhook_url = os.getenv(WEBHOOK_ENV_VAR, "").strip()
    if not webhook_url:
        raise RuntimeError(
            f"{WEBHOOK_ENV_VAR} is required for whatsapp-monitor hook alerts."
        )

    post_admin_alert(payload=payload, webhook_url=webhook_url)


def build_alert_payload(
    *, event_type: str, context: Mapping[str, Any] | None
) -> dict[str, Any] | None:
    """Build a webhook payload when a WhatsApp disconnect/re-pair condition is detected."""
    ctx = dict(context or {})

    if _gateway_started_without_whatsapp(event_type=event_type, context=ctx):
        return _payload(
            event_type=event_type,
            reason="whatsapp_not_connected_on_startup",
            severity="warning",
            message=(
                "Gateway started without an active WhatsApp platform. "
                "If this persists, a re-pair is likely required."
            ),
            detail="No 'whatsapp' entry present in gateway startup platforms.",
            context=ctx,
        )

    if _indicates_disconnect_or_repair(event_type=event_type, context=ctx):
        return _payload(
            event_type=event_type,
            reason="whatsapp_session_disconnected_or_repair_required",
            severity="critical",
            message=(
                "WhatsApp session health indicates disconnect/re-pair is required. "
                "Temporary disconnects may auto-recover, but persistent failures require manual re-pairing."
            ),
            detail=_extract_detail(ctx),
            context=ctx,
        )

    return None


def post_admin_alert(*, payload: Mapping[str, Any], webhook_url: str, timeout: int = 5) -> int:
    """POST alert payload to admin webhook. Raises on HTTP errors."""
    request = Request(
        webhook_url,
        data=json.dumps(dict(payload), ensure_ascii=True).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        status = int(getattr(response, "status", response.getcode()))
    if status >= 400:
        raise RuntimeError(f"Admin webhook returned non-success status: {status}")
    return status


def _gateway_started_without_whatsapp(
    *, event_type: str, context: Mapping[str, Any]
) -> bool:
    if event_type != "gateway:startup":
        return False
    platforms = context.get("platforms")
    if not isinstance(platforms, list):
        return True

    normalized = {str(item).strip().lower() for item in platforms if str(item).strip()}
    return "whatsapp" not in normalized


def _indicates_disconnect_or_repair(
    *, event_type: str, context: Mapping[str, Any]
) -> bool:
    platform = str(context.get("platform", "")).strip().lower()
    if event_type == "session:start" and platform and platform != "whatsapp":
        return False

    text = f"{event_type} {_extract_detail(context)}".lower()
    has_disconnect = any(marker in text for marker in _DISCONNECT_MARKERS)
    has_repair = any(marker in text for marker in _REPAIR_MARKERS)
    return has_disconnect or has_repair


def _extract_detail(context: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key in ("error", "reason", "message", "exception", "status", "state"):
        value = context.get(key)
        if value is None:
            continue
        compact = " ".join(str(value).split()).strip()
        if compact:
            parts.append(f"{key}={compact}")
    return "; ".join(parts) if parts else "No detail provided by event context."


def _payload(
    *,
    event_type: str,
    reason: str,
    severity: str,
    message: str,
    detail: str,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "source": "aptale.whatsapp-monitor",
        "event_type": event_type,
        "reason": reason,
        "severity": severity,
        "message": message,
        "detail": detail,
        "action_required": f"Run `{REPAIR_COMMAND}` and re-pair the WhatsApp session if failures persist.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {
            "platform": context.get("platform"),
            "session_id": context.get("session_id"),
            "platforms": context.get("platforms"),
        },
    }
