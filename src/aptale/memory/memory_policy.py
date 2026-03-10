"""Policy helpers for Aptale persistent preference memory updates."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import os
from pathlib import Path
import re
from typing import Any, Mapping, Sequence


_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_COUNTRY_RE = re.compile(r"^[A-Z]{2}$")
_TIMEZONE_RE = re.compile(r"^(UTC|[A-Za-z_]+(?:/[A-Za-z0-9_+\-]+)+)$")

_PII_KEY_PATTERNS = (
    re.compile(r"invoice", re.IGNORECASE),
    re.compile(r"supplier", re.IGNORECASE),
    re.compile(r"price", re.IGNORECASE),
    re.compile(r"subtotal", re.IGNORECASE),
    re.compile(r"total", re.IGNORECASE),
    re.compile(r"line_item", re.IGNORECASE),
    re.compile(r"address", re.IGNORECASE),
    re.compile(r"phone", re.IGNORECASE),
    re.compile(r"email", re.IGNORECASE),
)

_ALLOWED_KEYS = frozenset(
    {"local_currency", "profit_margin_pct", "timezone", "preferred_routes"}
)
_ALLOWED_ROUTE_KEYS = frozenset(
    {"origin_country", "destination_country", "origin_port", "destination_port", "mode"}
)
_ALLOWED_MODES = frozenset({"air", "sea", "road", "rail", "multimodal"})


class MemoryPolicyError(ValueError):
    """Raised when preference persistence policy is violated."""


@dataclass(frozen=True)
class PreferredRoute:
    """A durable route preference safe for persistent memory."""

    origin_country: str
    destination_country: str
    origin_port: str | None = None
    destination_port: str | None = None
    mode: str | None = None

    def as_display_line(self) -> str:
        base = f"{self.origin_country} -> {self.destination_country}"
        ports: list[str] = []
        if self.origin_port:
            ports.append(self.origin_port)
        if self.destination_port:
            ports.append(self.destination_port)
        if ports:
            base += f" ({' -> '.join(ports)})"
        if self.mode:
            base += f" [{self.mode}]"
        return base


@dataclass(frozen=True)
class PreferenceSnapshot:
    """Normalized durable preference data safe to persist."""

    local_currency: str
    profit_margin_pct: Decimal
    timezone: str
    preferred_routes: tuple[PreferredRoute, ...]

    @property
    def profit_margin_display(self) -> str:
        return format(self.profit_margin_pct, ".2f")


def resolve_hermes_memory_dir(
    *, memory_dir: str | Path | None = None, hermes_home: str | Path | None = None
) -> Path:
    """Resolve Hermes memory directory path using canonical runtime rules."""
    if memory_dir is not None:
        path = Path(memory_dir).expanduser()
    else:
        if hermes_home is None:
            hermes_home = os.getenv("HERMES_HOME")
        if hermes_home is None:
            path = Path("~/.hermes/memories").expanduser()
        else:
            path = Path(hermes_home).expanduser() / "memories"

    return path.resolve()


def sanitize_preference_update(payload: Mapping[str, Any]) -> PreferenceSnapshot:
    """Validate and normalize user preference updates before persistence."""
    if not isinstance(payload, Mapping):
        raise MemoryPolicyError("Preference update payload must be a mapping.")

    data = dict(payload)
    assert_no_pii_fields(data)

    keys = set(data.keys())
    missing = sorted(_ALLOWED_KEYS - keys)
    extra = sorted(keys - _ALLOWED_KEYS)
    if missing:
        raise MemoryPolicyError(f"Missing required preference fields: {', '.join(missing)}.")
    if extra:
        raise MemoryPolicyError(f"Unsupported preference fields: {', '.join(extra)}.")

    return PreferenceSnapshot(
        local_currency=_normalize_currency(data["local_currency"]),
        profit_margin_pct=_normalize_margin(data["profit_margin_pct"]),
        timezone=_normalize_timezone(data["timezone"]),
        preferred_routes=_normalize_preferred_routes(data["preferred_routes"]),
    )


def assert_no_pii_fields(value: Any, path: str = "$") -> None:
    """Reject data containing invoice/supplier/raw-pricing style keys."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_str = str(key)
            if _is_pii_key(key_str):
                raise MemoryPolicyError(
                    "PII/raw-pricing field is not allowed in persistent memory: "
                    f"{path}.{key_str}"
                )
            assert_no_pii_fields(child, f"{path}.{key_str}")
        return
    if isinstance(value, list):
        for idx, child in enumerate(value):
            assert_no_pii_fields(child, f"{path}[{idx}]")


def _is_pii_key(key: str) -> bool:
    return any(pattern.search(key) for pattern in _PII_KEY_PATTERNS)


def _normalize_currency(value: Any) -> str:
    code = str(value).strip().upper()
    if not _CURRENCY_RE.fullmatch(code):
        raise MemoryPolicyError(f"Invalid local_currency value: {value!r}")
    return code


def _normalize_margin(value: Any) -> Decimal:
    try:
        margin = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise MemoryPolicyError(f"Invalid profit_margin_pct value: {value!r}") from exc
    if margin < 0 or margin > 100:
        raise MemoryPolicyError("profit_margin_pct must be between 0 and 100.")
    return margin.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _normalize_timezone(value: Any) -> str:
    zone = str(value).strip()
    if not zone:
        raise MemoryPolicyError("timezone must not be blank.")
    if not _TIMEZONE_RE.fullmatch(zone):
        raise MemoryPolicyError(f"Invalid timezone value: {value!r}")
    return zone


def _normalize_preferred_routes(value: Any) -> tuple[PreferredRoute, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise MemoryPolicyError("preferred_routes must be a list of route objects.")

    normalized: list[PreferredRoute] = []
    for idx, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise MemoryPolicyError(
                f"preferred_routes[{idx}] must be an object mapping."
            )
        route = dict(item)
        assert_no_pii_fields(route, path=f"$.preferred_routes[{idx}]")
        missing = sorted({"origin_country", "destination_country"} - set(route.keys()))
        extra = sorted(set(route.keys()) - _ALLOWED_ROUTE_KEYS)
        if missing:
            raise MemoryPolicyError(
                f"preferred_routes[{idx}] missing fields: {', '.join(missing)}."
            )
        if extra:
            raise MemoryPolicyError(
                f"preferred_routes[{idx}] has unsupported fields: {', '.join(extra)}."
            )

        origin_country = str(route["origin_country"]).strip().upper()
        destination_country = str(route["destination_country"]).strip().upper()
        if not _COUNTRY_RE.fullmatch(origin_country):
            raise MemoryPolicyError(
                f"preferred_routes[{idx}].origin_country must be ISO-2 code."
            )
        if not _COUNTRY_RE.fullmatch(destination_country):
            raise MemoryPolicyError(
                f"preferred_routes[{idx}].destination_country must be ISO-2 code."
            )

        origin_port = _normalize_optional_text(route.get("origin_port"))
        destination_port = _normalize_optional_text(route.get("destination_port"))
        mode = _normalize_optional_text(route.get("mode"))
        if mode is not None:
            mode = mode.lower()
            if mode not in _ALLOWED_MODES:
                raise MemoryPolicyError(
                    f"preferred_routes[{idx}].mode must be one of: {', '.join(sorted(_ALLOWED_MODES))}."
                )

        normalized.append(
            PreferredRoute(
                origin_country=origin_country,
                destination_country=destination_country,
                origin_port=origin_port,
                destination_port=destination_port,
                mode=mode,
            )
        )

    return tuple(normalized)


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text
