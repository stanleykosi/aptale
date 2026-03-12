"""Context packaging utilities for delegated sourcing subagents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError
from aptale.contracts.normalize import normalize_currency

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"

_OUTPUT_SCHEMA_BY_TASK = {
    "freight": "freight_quote",
    "customs": "customs_quote",
    "fx": "fx_quote",
    "local_charges": "local_charge_quote",
    "risk_notes": "risk_note_quote",
}


class DelegationContextError(RuntimeError):
    """Raised when delegation context cannot be built safely."""


def build_subagent_context(
    *,
    task_type: str,
    invoice_extraction: Mapping[str, Any],
    local_currency: str,
    user_profile: Mapping[str, Any],
    route_status: str,
) -> str:
    """
    Build exhaustive JSON context for a subagent delegation task.

    Subagents have no memory of parent context, so this payload includes all
    required inputs and output contract expectations.
    """
    if task_type not in _OUTPUT_SCHEMA_BY_TASK:
        raise DelegationContextError(f"Unsupported task_type: {task_type!r}")
    if route_status != "route_resolved":
        raise DelegationContextError("Route must be resolved before building delegation context.")
    if not isinstance(user_profile, Mapping):
        raise DelegationContextError("user_profile must be a mapping.")

    try:
        extraction = normalize_and_validate_payload("invoice_extraction", invoice_extraction)
    except ContractsError as exc:
        raise DelegationContextError("invoice_extraction payload is invalid.") from exc

    country = _extract_user_country(user_profile, extraction)
    margin = _extract_profit_margin(user_profile)
    timezone = _extract_timezone(user_profile)
    local = normalize_currency(local_currency)
    shared_rules = load_subagent_shared_rules()

    payload = {
        "schema_version": "1.0",
        "task_type": task_type,
        "required_output_schema": _OUTPUT_SCHEMA_BY_TASK[task_type],
        "shared_rules": shared_rules,
        "input": {
            "invoice_extraction": extraction,
            "route": {
                "origin_country": extraction.get("origin_country"),
                "destination_country": extraction.get("destination_country"),
                "origin_port": extraction.get("origin_port"),
                "destination_port": extraction.get("destination_port"),
            },
            "local_currency": local,
            "user_profile": {
                "country": country,
                "profit_margin_pct": margin,
                "timezone": timezone,
            },
        },
    }
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)


def load_subagent_shared_rules() -> str:
    """Load shared rules prompt for delegated sourcing subagents."""
    path = _PROMPTS_DIR / "subagent_shared_rules.md"
    if not path.is_file():
        raise DelegationContextError(f"Required prompt file missing: {path}")
    return path.read_text(encoding="utf-8").strip()


def _extract_user_country(
    user_profile: Mapping[str, Any], extraction: Mapping[str, Any]
) -> str:
    candidates = (
        user_profile.get("country"),
        user_profile.get("home_country"),
        extraction.get("destination_country"),
    )
    for candidate in candidates:
        if isinstance(candidate, str) and len(candidate.strip()) == 2:
            return candidate.strip().upper()
    raise DelegationContextError(
        "User country is required for delegation context (profile or destination_country)."
    )


def _extract_profit_margin(user_profile: Mapping[str, Any]) -> float:
    for key in ("profit_margin_pct", "default_profit_margin_pct"):
        value = user_profile.get(key)
        if isinstance(value, (int, float)):
            margin = float(value)
            if 0 <= margin <= 100:
                return margin
            raise DelegationContextError(f"Invalid {key}: {value!r}. Must be within [0, 100].")
    raise DelegationContextError("User default profit margin is required for delegation.")


def _extract_timezone(user_profile: Mapping[str, Any]) -> str | None:
    for key in ("timezone", "tz"):
        value = user_profile.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None
