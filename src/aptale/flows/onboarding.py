"""First-run WhatsApp onboarding flow for merchant preferences."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from aptale.flows.onboarding_timezone import (
    OnboardingTimezoneError,
    capture_and_persist_onboarding_timezone,
)
from aptale.formatters.whatsapp_markdown import bold, bullets, join_sections, section


_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "onboarding.md"

_REQUIRED_FIELDS = (
    "local_currency",
    "destination_country",
    "common_lanes",
    "profit_margin_pct",
    "timezone",
    "communication_style_preference",
)

_FIELD_LABELS = {
    "local_currency": "Local currency",
    "destination_country": "Destination country",
    "common_lanes": "Common trade lanes",
    "profit_margin_pct": "Default profit margin",
    "timezone": "Local timezone",
    "communication_style_preference": "Reply style",
}

_FIELD_QUESTIONS = {
    "local_currency": "What is your local settlement currency? (ISO code, e.g. `NGN`, `USD`, `EUR`)",
    "destination_country": "What is your default destination country? (ISO-2 or country name, e.g. `NG` or `Nigeria`)",
    "common_lanes": (
        "What are your common trade lanes? Use comma-separated format like `CN->NG, TR->NG`.\n"
        "Reply `none` if you do not want to set lanes now."
    ),
    "profit_margin_pct": "What default profit margin percent should Aptale apply? (0-100)",
    "timezone": "What is your local timezone? (IANA format, e.g. `Africa/Lagos`)",
    "communication_style_preference": "Do you prefer `concise` or `detailed` replies?",
}

_COUNTRY_ALIASES = {
    "cn": "CN",
    "china": "CN",
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
    "jp": "JP",
    "japan": "JP",
    "in": "IN",
    "india": "IN",
}

_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_LANE_RE = re.compile(r"^\s*(?P<origin>[A-Za-z ]+?)\s*(?:->|to)\s*(?P<dest>[A-Za-z ]+?)\s*$", re.I)


class OnboardingError(RuntimeError):
    """Raised when onboarding flow inputs/state are invalid."""


@dataclass(frozen=True)
class OnboardingState:
    """Deterministic onboarding state for WhatsApp-first interactions."""

    status: str
    next_step: str
    channel: str
    pending_field: str | None
    collected_profile: Mapping[str, Any]
    message_markdown: str
    can_proceed: bool


def begin_onboarding(user_profile: Mapping[str, Any] | None = None) -> OnboardingState:
    """Start onboarding or resume from partially provided profile values."""
    if user_profile is not None and not isinstance(user_profile, Mapping):
        raise OnboardingError("user_profile must be a mapping when provided.")

    collected = _seed_collected_profile(dict(user_profile or {}))
    return _build_state(collected)


def process_onboarding_response(
    state: OnboardingState,
    response_text: str,
    *,
    memory_dir: str | Path | None = None,
) -> OnboardingState:
    """Apply one user response to onboarding state and return next state."""
    if not isinstance(state, OnboardingState):
        raise OnboardingError("state must be an OnboardingState instance.")
    if state.status != "awaiting_input" or not state.pending_field:
        raise OnboardingError("Onboarding state is not awaiting input.")
    if not isinstance(response_text, str) or not response_text.strip():
        raise OnboardingError("response_text must not be empty.")

    collected = dict(state.collected_profile)
    field = state.pending_field
    collected[field] = _parse_field_value(field, response_text)

    next_field = _next_missing_field(collected)
    if next_field is not None:
        return _build_state(collected)

    _persist_onboarding_preferences(collected, memory_dir=memory_dir)
    completion_message = _build_completion_message(collected)
    return OnboardingState(
        status="completed",
        next_step="onboarding_complete",
        channel="whatsapp",
        pending_field=None,
        collected_profile=collected,
        message_markdown=completion_message,
        can_proceed=True,
    )


def _build_state(collected: Mapping[str, Any]) -> OnboardingState:
    pending = _next_missing_field(collected)
    if pending is None:
        raise OnboardingError("Onboarding state requires pending field while awaiting input.")

    prompt = _load_onboarding_prompt()
    overview = section("Onboarding Setup", prompt)
    question = section(
        f"Step {_required_index(pending)} of {len(_REQUIRED_FIELDS)}",
        _FIELD_QUESTIONS[pending],
    )

    captured_lines = []
    for key in _REQUIRED_FIELDS:
        if key not in collected:
            continue
        captured_lines.append(f"{bold(_FIELD_LABELS[key])}: {_display_value(key, collected[key])}")

    sections = [overview, question]
    if captured_lines:
        sections.append(section("Captured So Far", bullets(captured_lines)))

    return OnboardingState(
        status="awaiting_input",
        next_step="collect_onboarding_input",
        channel="whatsapp",
        pending_field=pending,
        collected_profile=dict(collected),
        message_markdown=join_sections(sections),
        can_proceed=False,
    )


def _required_index(field: str) -> int:
    return _REQUIRED_FIELDS.index(field) + 1


def _load_onboarding_prompt() -> str:
    if not _PROMPT_PATH.is_file():
        raise OnboardingError(f"Required prompt file missing: {_PROMPT_PATH}")
    text = _PROMPT_PATH.read_text(encoding="utf-8").strip()
    if not text:
        raise OnboardingError(f"Prompt file is empty: {_PROMPT_PATH}")
    return text


def _seed_collected_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    collected: dict[str, Any] = {}
    for field in _REQUIRED_FIELDS:
        if field not in profile:
            continue
        value = profile.get(field)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        collected[field] = _parse_field_value(field, value)
    return collected


def _next_missing_field(collected: Mapping[str, Any]) -> str | None:
    for field in _REQUIRED_FIELDS:
        if field not in collected:
            return field
    return None


def _parse_field_value(field: str, value: Any) -> Any:
    if field == "local_currency":
        return _parse_currency(value)
    if field == "destination_country":
        return _parse_country(value)
    if field == "common_lanes":
        return _parse_common_lanes(value)
    if field == "profit_margin_pct":
        return _parse_margin(value)
    if field == "timezone":
        from aptale.memory.timezone import normalize_timezone
        try:
            return normalize_timezone(value)
        except Exception as exc:
            raise OnboardingError(
                "timezone must be a valid IANA timezone (example: Africa/Lagos)."
            ) from exc
    if field == "communication_style_preference":
        return _parse_style(value)
    raise OnboardingError(f"Unsupported onboarding field: {field!r}")


def _parse_currency(value: Any) -> str:
    code = str(value).strip().upper()
    if not _CURRENCY_RE.fullmatch(code):
        raise OnboardingError("local_currency must be a 3-letter ISO currency code.")
    return code


def _parse_country(value: Any) -> str:
    text = str(value).strip()
    if not text:
        raise OnboardingError("destination_country must not be blank.")
    alias_key = text.casefold()
    if alias_key in _COUNTRY_ALIASES:
        return _COUNTRY_ALIASES[alias_key]
    code = text.upper()
    if len(code) == 2 and code.isalpha():
        return code
    raise OnboardingError("destination_country must be ISO-2 or a supported country name.")


def _parse_common_lanes(value: Any) -> tuple[dict[str, str], ...]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        lanes: list[dict[str, str]] = []
        for idx, item in enumerate(value):
            if not isinstance(item, Mapping):
                raise OnboardingError(
                    f"common_lanes[{idx}] must be an object with origin_country and destination_country."
                )
            origin = _parse_country(item.get("origin_country", ""))
            destination = _parse_country(item.get("destination_country", ""))
            lanes.append(
                {
                    "origin_country": origin,
                    "destination_country": destination,
                }
            )
        return tuple(lanes)

    text = str(value).strip()
    if not text:
        raise OnboardingError("common_lanes must not be blank.")
    if text.casefold() == "none":
        return tuple()

    lanes: list[dict[str, str]] = []
    for token in _split_lane_tokens(text):
        match = _LANE_RE.match(token)
        if not match:
            raise OnboardingError(
                "common_lanes must use 'ORIGIN->DESTINATION' format (example: CN->NG)."
            )
        origin = _parse_country(match.group("origin"))
        destination = _parse_country(match.group("dest"))
        lanes.append(
            {
                "origin_country": origin,
                "destination_country": destination,
            }
        )
    return tuple(lanes)


def _split_lane_tokens(text: str) -> list[str]:
    tokens = [part.strip() for part in re.split(r"[,\n;]+", text) if part.strip()]
    if not tokens:
        raise OnboardingError("common_lanes did not contain any valid lane entries.")
    return tokens


def _parse_margin(value: Any) -> Decimal:
    try:
        margin = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise OnboardingError("profit_margin_pct must be numeric.") from exc
    if margin < 0 or margin > 100:
        raise OnboardingError("profit_margin_pct must be between 0 and 100.")
    return margin.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _parse_style(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"concise", "short", "brief", "quick"}:
        return "concise"
    if text in {"detailed", "long", "in-depth", "thorough"}:
        return "detailed"
    raise OnboardingError("communication_style_preference must be concise or detailed.")


def _persist_onboarding_preferences(
    collected: Mapping[str, Any], *, memory_dir: str | Path | None
) -> None:
    profile_for_persistence = {
        "local_currency": collected["local_currency"],
        "profit_margin_pct": str(collected["profit_margin_pct"]),
        "preferred_routes": list(collected["common_lanes"]),
    }

    try:
        result = capture_and_persist_onboarding_timezone(
            profile_for_persistence,
            timezone_input=str(collected["timezone"]),
            memory_dir=memory_dir,
        )
    except OnboardingTimezoneError as exc:
        raise OnboardingError("Failed to persist onboarding timezone/profile settings.") from exc

    if result.status != "timezone_captured":
        raise OnboardingError("Onboarding could not complete because timezone capture is unresolved.")


def _build_completion_message(collected: Mapping[str, Any]) -> str:
    lines = [
        f"{bold('Local currency')}: {collected['local_currency']}",
        f"{bold('Destination country')}: {collected['destination_country']}",
        f"{bold('Common lanes')}: {_display_value('common_lanes', collected['common_lanes'])}",
        f"{bold('Default profit margin')}: {collected['profit_margin_pct']}%",
        f"{bold('Timezone')}: {collected['timezone']}",
        f"{bold('Reply style')}: {collected['communication_style_preference']}",
    ]
    sections = [
        section("Onboarding Complete", "Your default broker settings are saved."),
        section("Saved Preferences", bullets(lines)),
    ]
    return join_sections(sections)


def _display_value(field: str, value: Any) -> str:
    if field == "common_lanes":
        lanes = value
        if not lanes:
            return "None"
        return ", ".join(f"{lane['origin_country']}->{lane['destination_country']}" for lane in lanes)
    if field == "profit_margin_pct":
        return f"{value}%"
    return str(value)
