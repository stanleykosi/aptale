"""Route and local-currency inference for canonical invoice extraction payloads."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError
from aptale.contracts.normalize import normalize_currency

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"

_COUNTRY_ALIASES: dict[str, str] = {
    "cn": "CN",
    "china": "CN",
    "prc": "CN",
    "ng": "NG",
    "nigeria": "NG",
    "tr": "TR",
    "turkey": "TR",
    "turkiye": "TR",
    "us": "US",
    "usa": "US",
    "united states": "US",
    "gb": "GB",
    "uk": "GB",
    "united kingdom": "GB",
    "nl": "NL",
    "netherlands": "NL",
}

_PORT_ALIASES: dict[str, tuple[str, str]] = {
    "guangzhou": ("Guangzhou", "CN"),
    "shenzhen": ("Shenzhen", "CN"),
    "shanghai": ("Shanghai", "CN"),
    "lagos": ("Lagos", "NG"),
    "tin can island": ("Tin Can Island", "NG"),
    "istanbul": ("Istanbul", "TR"),
    "mersin": ("Mersin", "TR"),
    "felixstowe": ("Felixstowe", "GB"),
    "rotterdam": ("Rotterdam", "NL"),
}

_LOCAL_CURRENCY_BY_COUNTRY = {
    "CN": "CNY",
    "NG": "NGN",
    "TR": "TRY",
    "US": "USD",
    "GB": "GBP",
    "NL": "EUR",
}


class RouteInferenceError(RuntimeError):
    """Raised when route inference cannot safely process inputs."""


class RouteInferenceEngine(Protocol):
    """Optional model-assisted route inference provider."""

    def __call__(
        self,
        *,
        extraction: Mapping[str, Any],
        user_profile: Mapping[str, Any],
        recent_chat_context: Sequence[str],
        prompt: str,
    ) -> Mapping[str, Any]:
        ...


@dataclass(frozen=True)
class RouteInferenceResult:
    """Route inference result with explicit unresolved-route behavior."""

    status: str
    next_step: str
    can_source: bool
    invoice_extraction: Mapping[str, Any]
    local_currency: str | None
    route_required_prompt: str | None
    missing_fields: tuple[str, ...]


def infer_route_context(
    extraction_payload: Mapping[str, Any],
    *,
    user_profile: Mapping[str, Any] | None = None,
    recent_chat_context: Sequence[str] | None = None,
    inference_engine: RouteInferenceEngine | None = None,
) -> RouteInferenceResult:
    """
    Infer route and local currency from extraction + profile + chat context.

    Returns explicit `route_required_prompt` when unresolved fields remain.
    """
    if not isinstance(extraction_payload, Mapping):
        raise RouteInferenceError("extraction_payload must be a mapping.")
    if user_profile is not None and not isinstance(user_profile, Mapping):
        raise RouteInferenceError("user_profile must be a mapping when provided.")
    if recent_chat_context is not None and not isinstance(recent_chat_context, Sequence):
        raise RouteInferenceError("recent_chat_context must be a sequence of strings.")
    if inference_engine is not None and not callable(inference_engine):
        raise RouteInferenceError("inference_engine must be callable when provided.")

    profile = dict(user_profile or {})
    recent_context = [str(x) for x in (recent_chat_context or [])]

    try:
        validated = normalize_and_validate_payload("invoice_extraction", extraction_payload)
    except ContractsError as exc:
        raise RouteInferenceError("Input extraction payload is invalid.") from exc

    prompt = _load_prompt("route_inference.md")
    updated = deepcopy(validated)

    explicit_profile = _extract_explicit_profile_route(profile)
    chat_hints = _extract_chat_route_hints(recent_context)
    engine_hints = _extract_engine_hints(
        inference_engine=inference_engine,
        extraction=updated,
        user_profile=profile,
        recent_chat_context=recent_context,
        prompt=prompt,
    )

    _set_if_missing(updated, "origin_country", _pick_country_hint(updated, explicit_profile, chat_hints, engine_hints, "origin_country"))
    _set_if_missing(updated, "destination_country", _pick_country_hint(updated, explicit_profile, chat_hints, engine_hints, "destination_country"))
    _set_if_missing(updated, "origin_port", _pick_port_hint(updated, explicit_profile, chat_hints, engine_hints, "origin_port"))
    _set_if_missing(updated, "destination_port", _pick_port_hint(updated, explicit_profile, chat_hints, engine_hints, "destination_port"))

    # Keep route-country coherence strict where possible.
    _enforce_port_country_consistency(updated)

    missing_fields = _missing_route_fields(updated)
    local_currency = _infer_local_currency(
        payload=updated,
        user_profile=profile,
        chat_hints=chat_hints,
        engine_hints=engine_hints,
    )
    if local_currency is None:
        missing_fields = missing_fields + ("local_currency",)

    try:
        validated_out = normalize_and_validate_payload("invoice_extraction", updated)
    except ContractsError as exc:
        raise RouteInferenceError("Route inference output failed invoice schema validation.") from exc

    if missing_fields:
        return RouteInferenceResult(
            status="route_required",
            next_step="request_route_details",
            can_source=False,
            invoice_extraction=validated_out,
            local_currency=local_currency,
            route_required_prompt=_build_route_required_prompt(missing_fields),
            missing_fields=tuple(missing_fields),
        )

    return RouteInferenceResult(
        status="route_resolved",
        next_step="ready_for_delegation_input",
        can_source=True,
        invoice_extraction=validated_out,
        local_currency=local_currency,
        route_required_prompt=None,
        missing_fields=(),
    )


def _extract_explicit_profile_route(profile: Mapping[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}

    for key in ("origin_country", "destination_country"):
        value = profile.get(key)
        resolved = _resolve_country(value)
        if resolved:
            out[key] = resolved

    for key in ("origin_port", "destination_port"):
        value = profile.get(key)
        resolved = _resolve_port(value)
        if resolved:
            out[key] = resolved[0]

    route = profile.get("default_route")
    if isinstance(route, Mapping):
        for key in ("origin_country", "destination_country"):
            resolved = _resolve_country(route.get(key))
            if resolved:
                out.setdefault(key, resolved)
        for key in ("origin_port", "destination_port"):
            resolved = _resolve_port(route.get(key))
            if resolved:
                out.setdefault(key, resolved[0])
    return out


def _extract_chat_route_hints(context: Sequence[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    blob = "\n".join(context).lower()

    for key, regex in (
        ("origin_country", r"\bfrom\s+([a-z .-]+?)\s+(?:to|->)\s"),
        ("destination_country", r"(?:\bto\b|->)\s*([a-z .-]+?)(?:[\n,.]|$)"),
    ):
        match = re.search(regex, blob)
        if match:
            resolved = _resolve_country(match.group(1))
            if resolved:
                out[key] = resolved

    for key, regex in (
        ("origin_port", r"\bfrom\s+([a-z .-]+?)\s+(?:port|harbor|to|->)\b"),
        ("destination_port", r"(?:\bto\b|->)\s*([a-z .-]+?)\s*(?:port|harbor|$|[,.])"),
    ):
        match = re.search(regex, blob)
        if match:
            resolved = _resolve_port(match.group(1))
            if resolved:
                out[key] = resolved[0]

    for alias, (port_name, country_code) in _PORT_ALIASES.items():
        if alias in blob:
            if "from" in blob and alias in _segment_after(blob, "from"):
                out.setdefault("origin_port", port_name)
                out.setdefault("origin_country", country_code)
            if "to" in blob and alias in _segment_after(blob, "to"):
                out.setdefault("destination_port", port_name)
                out.setdefault("destination_country", country_code)

    currency_match = re.search(r"\b(local currency|settle in|pay in)\s+([A-Z]{3})\b", "\n".join(context))
    if currency_match:
        out["local_currency"] = currency_match.group(2).upper()

    return out


def _extract_engine_hints(
    *,
    inference_engine: RouteInferenceEngine | None,
    extraction: Mapping[str, Any],
    user_profile: Mapping[str, Any],
    recent_chat_context: Sequence[str],
    prompt: str,
) -> dict[str, str]:
    if inference_engine is None:
        return {}

    raw = inference_engine(
        extraction=extraction,
        user_profile=user_profile,
        recent_chat_context=recent_chat_context,
        prompt=prompt,
    )
    if not isinstance(raw, Mapping):
        raise RouteInferenceError("Route inference engine must return a mapping.")

    out: dict[str, str] = {}
    for key in ("origin_country", "destination_country"):
        resolved = _resolve_country(raw.get(key))
        if resolved:
            out[key] = resolved
    for key in ("origin_port", "destination_port"):
        resolved = _resolve_port(raw.get(key))
        if resolved:
            out[key] = resolved[0]

    local = raw.get("local_currency")
    if local is not None:
        out["local_currency"] = normalize_currency(str(local))
    return out


def _pick_country_hint(
    payload: Mapping[str, Any],
    profile_hints: Mapping[str, str],
    chat_hints: Mapping[str, str],
    engine_hints: Mapping[str, str],
    key: str,
) -> str | None:
    existing = payload.get(key)
    if isinstance(existing, str) and existing.strip():
        return existing
    return profile_hints.get(key) or chat_hints.get(key) or engine_hints.get(key)


def _pick_port_hint(
    payload: Mapping[str, Any],
    profile_hints: Mapping[str, str],
    chat_hints: Mapping[str, str],
    engine_hints: Mapping[str, str],
    key: str,
) -> str | None:
    existing = payload.get(key)
    if isinstance(existing, str) and existing.strip():
        return existing
    return profile_hints.get(key) or chat_hints.get(key) or engine_hints.get(key)


def _infer_local_currency(
    *,
    payload: Mapping[str, Any],
    user_profile: Mapping[str, Any],
    chat_hints: Mapping[str, str],
    engine_hints: Mapping[str, str],
) -> str | None:
    for key in ("local_currency", "preferred_currency", "currency"):
        value = user_profile.get(key)
        if isinstance(value, str) and value.strip():
            try:
                return normalize_currency(value)
            except Exception:
                pass

    if "local_currency" in engine_hints:
        return engine_hints["local_currency"]
    if "local_currency" in chat_hints:
        try:
            return normalize_currency(chat_hints["local_currency"])
        except Exception:
            pass

    destination_country = payload.get("destination_country")
    if isinstance(destination_country, str):
        return _LOCAL_CURRENCY_BY_COUNTRY.get(destination_country.strip().upper())
    return None


def _set_if_missing(payload: dict[str, Any], key: str, value: str | None) -> None:
    if value is None:
        return
    current = payload.get(key)
    if current is None or (isinstance(current, str) and current.strip() == ""):
        payload[key] = value


def _enforce_port_country_consistency(payload: dict[str, Any]) -> None:
    origin_port = _resolve_port(payload.get("origin_port"))
    dest_port = _resolve_port(payload.get("destination_port"))
    if origin_port and payload.get("origin_country") is None:
        payload["origin_country"] = origin_port[1]
    if dest_port and payload.get("destination_country") is None:
        payload["destination_country"] = dest_port[1]


def _missing_route_fields(payload: Mapping[str, Any]) -> tuple[str, ...]:
    missing: list[str] = []
    for key in ("origin_country", "destination_country", "origin_port", "destination_port"):
        value = payload.get(key)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(key)
    return tuple(missing)


def _resolve_country(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if re.fullmatch(r"[a-z]{2}", text):
        return text.upper()
    return _COUNTRY_ALIASES.get(text)


def _resolve_port(value: Any) -> tuple[str, str] | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if text in _PORT_ALIASES:
        return _PORT_ALIASES[text]
    return None


def _segment_after(blob: str, marker: str) -> str:
    idx = blob.find(marker)
    if idx == -1:
        return ""
    return blob[idx + len(marker) :]


def _build_route_required_prompt(missing_fields: Sequence[str]) -> str:
    fields = ", ".join(missing_fields)
    return (
        "*Route Required*\n"
        "I still need complete route details before sourcing can run.\n"
        f"Missing fields: {fields}\n\n"
        "Reply with:\n"
        "- Origin country and origin port\n"
        "- Destination country and destination port\n"
        "- Local currency for landed-cost output"
    )


def _load_prompt(filename: str) -> str:
    path = _PROMPTS_DIR / filename
    if not path.is_file():
        raise RouteInferenceError(f"Required prompt file missing: {path}")
    return path.read_text(encoding="utf-8").strip()

