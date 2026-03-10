"""Persistence helpers for Aptale user preference updates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .memory_policy import (
    MemoryPolicyError,
    PreferenceSnapshot,
    resolve_hermes_memory_dir,
    sanitize_preference_update,
)

USER_FILENAME = "USER.md"
MEMORY_FILENAME = "MEMORY.md"

_USER_BLOCK_START = "<!-- APTALE_USER_PREFERENCES_START -->"
_USER_BLOCK_END = "<!-- APTALE_USER_PREFERENCES_END -->"
_MEMORY_BLOCK_START = "<!-- APTALE_MEMORY_POLICY_START -->"
_MEMORY_BLOCK_END = "<!-- APTALE_MEMORY_POLICY_END -->"


class ProfileUpdateError(RuntimeError):
    """Raised when preference persistence update cannot be completed."""


@dataclass(frozen=True)
class ProfileUpdateResult:
    """Result of writing sanitized preference updates into Hermes memory files."""

    user_path: Path
    memory_path: Path
    snapshot: PreferenceSnapshot


def apply_preference_profile_updates(
    preferences: Mapping[str, Any],
    *,
    memory_dir: str | Path | None = None,
    now_fn: Callable[[], datetime] | None = None,
) -> ProfileUpdateResult:
    """
    Persist durable preference data into USER.md and MEMORY.md.

    Only sanitized, non-PII preference fields are written.
    """
    try:
        snapshot = sanitize_preference_update(preferences)
    except MemoryPolicyError as exc:
        raise ProfileUpdateError("Preference update payload violates memory policy.") from exc

    target_dir = resolve_hermes_memory_dir(memory_dir=memory_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    user_path = target_dir / USER_FILENAME
    memory_path = target_dir / MEMORY_FILENAME
    now = now_fn or (lambda: datetime.now(timezone.utc))
    updated_at = _utc_iso(now())

    _write_managed_block(
        user_path,
        start_marker=_USER_BLOCK_START,
        end_marker=_USER_BLOCK_END,
        content=_render_user_preferences_block(snapshot),
        default_header="# USER.md\n\n",
    )
    _write_managed_block(
        memory_path,
        start_marker=_MEMORY_BLOCK_START,
        end_marker=_MEMORY_BLOCK_END,
        content=_render_memory_policy_block(snapshot, updated_at=updated_at),
        default_header="# MEMORY.md\n\n",
    )

    return ProfileUpdateResult(
        user_path=user_path,
        memory_path=memory_path,
        snapshot=snapshot,
    )


def _render_user_preferences_block(snapshot: PreferenceSnapshot) -> str:
    route_lines = _route_bullets(snapshot)
    return "\n".join(
        [
            "## Aptale Persistent Preferences (Non-PII)",
            "",
            f"- Local currency (ISO 4217): `{snapshot.local_currency}`",
            f"- Default profit margin percent: `{snapshot.profit_margin_display}`",
            f"- Local timezone (IANA): `{snapshot.timezone}`",
            "- Preferred routes:",
            *route_lines,
            "",
            "- Persistence scope: Durable preference data only. Do not store raw invoice values or supplier details.",
        ]
    ).strip()


def _render_memory_policy_block(snapshot: PreferenceSnapshot, *, updated_at: str) -> str:
    route_lines = _route_bullets(snapshot)
    return "\n".join(
        [
            "## Aptale Memory Policy Snapshot",
            "",
            "- Policy: Persist only durable preference data and operational notes.",
            "- Prohibited: Raw invoice totals, supplier names, line-item pricing, and invoice identifiers.",
            f"- Last profile update (UTC): `{updated_at}`",
            f"- Persisted local currency: `{snapshot.local_currency}`",
            f"- Persisted default profit margin percent: `{snapshot.profit_margin_display}`",
            f"- Persisted local timezone (IANA): `{snapshot.timezone}`",
            "- Persisted preferred routes:",
            *route_lines,
        ]
    ).strip()


def _route_bullets(snapshot: PreferenceSnapshot) -> list[str]:
    if not snapshot.preferred_routes:
        return ["  - None configured."]
    return [f"  - {route.as_display_line()}" for route in snapshot.preferred_routes]


def _write_managed_block(
    path: Path,
    *,
    start_marker: str,
    end_marker: str,
    content: str,
    default_header: str,
) -> None:
    block = f"{start_marker}\n{content}\n{end_marker}\n"
    if path.exists():
        original = path.read_text(encoding="utf-8")
    else:
        original = default_header

    updated = _upsert_block(
        original,
        start_marker=start_marker,
        end_marker=end_marker,
        block=block,
    )
    path.write_text(updated, encoding="utf-8")


def _upsert_block(
    original: str,
    *,
    start_marker: str,
    end_marker: str,
    block: str,
) -> str:
    start_idx = original.find(start_marker)
    end_idx = original.find(end_marker)

    if start_idx == -1 and end_idx == -1:
        text = original.rstrip()
        if text:
            text += "\n\n"
        return text + block

    if (start_idx == -1) != (end_idx == -1):
        raise ProfileUpdateError(
            "Managed memory block markers are malformed; both start and end markers are required."
        )
    if end_idx < start_idx:
        raise ProfileUpdateError("Managed memory block markers are out of order.")

    end_tail = end_idx + len(end_marker)
    if end_tail < len(original) and original[end_tail] == "\n":
        end_tail += 1
    return original[:start_idx] + block + original[end_tail:]


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
