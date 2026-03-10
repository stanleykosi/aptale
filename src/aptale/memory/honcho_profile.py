"""Honcho context query wrapper for tone/brevity/business adaptation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import re
from typing import Any, Mapping, Protocol, Sequence


_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "honcho_query.md"
_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


class HonchoProfileError(RuntimeError):
    """Raised when Honcho context querying or normalization fails."""


class HonchoQueryTool(Protocol):
    """Tool-call interface for Hermes `query_user_context`."""

    def __call__(self, *, query: str) -> Any:
        ...


@dataclass(frozen=True)
class OperationalSettings:
    """Canonical operational settings sourced from USER profile memory."""

    local_currency: str
    profit_margin_pct: Decimal
    timezone: str
    preferred_routes: tuple[str, ...]

    @property
    def profit_margin_display(self) -> str:
        return format(self.profit_margin_pct, ".2f")


@dataclass(frozen=True)
class HonchoAdaptiveProfile:
    """Response adaptation profile combining USER and Honcho context."""

    operational_settings: OperationalSettings
    communication_style: str
    brevity_preference: str
    business_context_signals: tuple[str, ...]
    honcho_query: str | None
    honcho_summary: str | None


def build_honcho_query(user_message: str, *, prompt_text: str | None = None) -> str:
    """Build a canonical Honcho query request from prompt conventions."""
    msg = str(user_message).strip()
    if not msg:
        raise HonchoProfileError("user_message must not be blank.")

    guidance = prompt_text if prompt_text is not None else load_honcho_query_prompt()
    guidance = guidance.strip()
    if not guidance:
        raise HonchoProfileError("Honcho query prompt is empty.")

    return (
        f"{guidance}\n\n"
        "Current user request:\n"
        f"{msg}"
    )


def load_honcho_query_prompt() -> str:
    """Load the Honcho query convention prompt text."""
    if not _PROMPT_PATH.is_file():
        raise HonchoProfileError(f"Required prompt file missing: {_PROMPT_PATH}")
    text = _PROMPT_PATH.read_text(encoding="utf-8").strip()
    if not text:
        raise HonchoProfileError(f"Prompt file is empty: {_PROMPT_PATH}")
    return text


def build_adaptive_profile(
    *,
    user_profile: Mapping[str, Any],
    user_message: str,
    query_user_context: HonchoQueryTool | None,
) -> HonchoAdaptiveProfile:
    """
    Build a profile that adapts style/brevity/business context from Honcho.

    Operational settings are always sourced from USER profile data, keeping
    Honcho additive rather than replacing canonical runtime settings.
    """
    settings = extract_operational_settings(user_profile)
    fallback_style = _normalize_style(user_profile.get("communication_style_preference"))
    fallback_brevity = _normalize_brevity(user_profile.get("communication_style_preference"))

    if query_user_context is None:
        return HonchoAdaptiveProfile(
            operational_settings=settings,
            communication_style=fallback_style,
            brevity_preference=fallback_brevity,
            business_context_signals=tuple(),
            honcho_query=None,
            honcho_summary=None,
        )

    query = build_honcho_query(user_message)
    raw = query_user_context(query=query)
    summary = _normalize_honcho_response(raw)

    return HonchoAdaptiveProfile(
        operational_settings=settings,
        communication_style=_derive_style(summary, fallback=fallback_style),
        brevity_preference=_derive_brevity(summary, fallback=fallback_brevity),
        business_context_signals=_derive_business_context(summary),
        honcho_query=query,
        honcho_summary=summary,
    )


def extract_operational_settings(user_profile: Mapping[str, Any]) -> OperationalSettings:
    """Extract canonical operational settings from USER profile data."""
    if not isinstance(user_profile, Mapping):
        raise HonchoProfileError("user_profile must be a mapping.")

    local_currency = _normalize_currency(user_profile.get("local_currency"))
    profit_margin = _normalize_margin(user_profile.get("profit_margin_pct"))
    timezone = _normalize_timezone(user_profile.get("timezone"))
    preferred_routes = _normalize_preferred_routes(user_profile.get("preferred_routes"))

    return OperationalSettings(
        local_currency=local_currency,
        profit_margin_pct=profit_margin,
        timezone=timezone,
        preferred_routes=preferred_routes,
    )


def _normalize_honcho_response(value: Any) -> str:
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise HonchoProfileError("Honcho response text is blank.")
        return text

    if isinstance(value, Mapping):
        for key in ("context", "answer", "result", "content", "text"):
            content = value.get(key)
            if isinstance(content, str) and content.strip():
                return content.strip()
        raise HonchoProfileError(
            "Honcho response mapping must include non-empty text in one of: "
            "context, answer, result, content, text."
        )

    raise HonchoProfileError(
        "Honcho response must be a string or mapping with text content."
    )


def _derive_style(summary: str, *, fallback: str) -> str:
    text = summary.lower()
    if any(token in text for token in ("concise", "brief", "short responses")):
        return "concise"
    if any(token in text for token in ("detailed", "in-depth", "thorough")):
        return "detailed"
    return fallback


def _derive_brevity(summary: str, *, fallback: str) -> str:
    text = summary.lower()
    if any(token in text for token in ("concise", "brief", "short")):
        return "short"
    if any(token in text for token in ("detailed", "in-depth", "long-form")):
        return "long"
    return fallback


def _derive_business_context(summary: str) -> tuple[str, ...]:
    parts = re.split(r"[.\n;]+", summary)
    keywords = (
        "goal",
        "priority",
        "import",
        "trade",
        "freight",
        "customs",
        "margin",
        "lane",
        "business",
    )
    signals: list[str] = []
    for part in parts:
        clean = " ".join(part.split()).strip()
        if not clean:
            continue
        lower = clean.lower()
        if any(token in lower for token in keywords):
            signals.append(clean)
        if len(signals) >= 3:
            break
    return tuple(signals)


def _normalize_currency(value: Any) -> str:
    code = str(value).strip().upper()
    if not _CURRENCY_RE.fullmatch(code):
        raise HonchoProfileError(f"Invalid USER profile local_currency: {value!r}")
    return code


def _normalize_margin(value: Any) -> Decimal:
    try:
        margin = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise HonchoProfileError(
            f"Invalid USER profile profit_margin_pct: {value!r}"
        ) from exc
    if margin < 0 or margin > 100:
        raise HonchoProfileError("USER profile profit_margin_pct must be between 0 and 100.")
    return margin.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _normalize_timezone(value: Any) -> str:
    zone = str(value).strip()
    if not zone:
        raise HonchoProfileError("USER profile timezone must not be blank.")
    return zone


def _normalize_preferred_routes(value: Any) -> tuple[str, ...]:
    if value is None:
        return tuple()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise HonchoProfileError("USER profile preferred_routes must be a sequence.")
    routes: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
            if text:
                routes.append(text)
            continue
        if isinstance(item, Mapping):
            origin = str(item.get("origin_country", "")).strip().upper()
            destination = str(item.get("destination_country", "")).strip().upper()
            if origin and destination:
                routes.append(f"{origin}->{destination}")
                continue
        raise HonchoProfileError("USER profile preferred_routes contains invalid route entry.")
    return tuple(routes)


def _normalize_style(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"concise", "detailed"}:
        return text
    return "balanced"


def _normalize_brevity(value: Any) -> str:
    text = str(value).strip().lower()
    if text == "concise":
        return "short"
    if text == "detailed":
        return "long"
    return "standard"
