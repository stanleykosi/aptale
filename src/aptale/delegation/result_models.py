"""Models and normalization helpers for delegated subagent outputs."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from aptale.contracts.errors import NormalizationError
from aptale.contracts.normalize import normalize_currency, normalize_hs_code

TASK_TO_SCHEMA = {
    "freight": "freight_quote",
    "customs": "customs_quote",
    "fx": "fx_quote",
    "local_charges": "local_charge_quote",
    "risk_notes": "risk_note_quote",
}


class SubagentResultError(RuntimeError):
    """Base error for delegated subagent output handling."""


class UnsupportedTaskTypeError(SubagentResultError):
    """Raised when a subagent task type is unknown."""


class InvalidSubagentPayloadError(SubagentResultError):
    """Raised when a subagent payload cannot be normalized safely."""


class MissingCitationError(SubagentResultError):
    """Raised when required source citation fields are absent."""


@dataclass(frozen=True)
class ParsedSubagentResult:
    """Validated and normalized output returned by a delegated subagent."""

    task_type: str
    schema_name: str
    payload: Mapping[str, Any]


def schema_name_for_task(task_type: str) -> str:
    """Resolve the canonical schema name for a delegation task type."""
    schema_name = TASK_TO_SCHEMA.get(task_type)
    if schema_name is None:
        allowed = ", ".join(sorted(TASK_TO_SCHEMA.keys()))
        raise UnsupportedTaskTypeError(
            f"Unsupported task_type {task_type!r}. Expected one of: {allowed}."
        )
    return schema_name


def normalize_subagent_payload(task_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize subagent output fields prior to schema validation."""
    schema_name_for_task(task_type)
    if not isinstance(payload, Mapping):
        raise InvalidSubagentPayloadError("Subagent JSON output must be an object.")

    data = deepcopy(dict(payload))
    try:
        _normalize_common_root_fields(data)
        if task_type == "freight":
            _normalize_freight_payload(data)
        elif task_type == "customs":
            _normalize_customs_payload(data)
        elif task_type == "fx":
            _normalize_fx_payload(data)
        elif task_type == "local_charges":
            _normalize_local_charges_payload(data)
        elif task_type == "risk_notes":
            _normalize_risk_notes_payload(data)
    except (NormalizationError, TypeError, ValueError) as exc:
        raise InvalidSubagentPayloadError(
            f"Failed to normalize {task_type} payload: {exc}"
        ) from exc
    return data


def _normalize_common_root_fields(data: dict[str, Any]) -> None:
    _strip_field(data, "schema_version")
    _strip_field(data, "quote_id")
    _strip_field(data, "extraction_id")
    _strip_field(data, "captured_at")


def _normalize_freight_payload(data: dict[str, Any]) -> None:
    _normalize_country_field(data, "origin_country")
    _normalize_country_field(data, "destination_country")
    _normalize_currency_field(data, "currency")
    _strip_field(data, "provider_name")
    _strip_nullable_string_field(data, "origin_port")
    _strip_nullable_string_field(data, "destination_port")
    _strip_nullable_string_field(data, "valid_until")
    _lower_field(data, "mode")
    _lower_field(data, "service_level")
    _lower_field(data, "source_type")
    _normalize_sources(data, include_rate_type=False)

    charge_breakdown = data.get("charge_breakdown")
    if isinstance(charge_breakdown, list):
        for entry in charge_breakdown:
            if not isinstance(entry, dict):
                continue
            _strip_field(entry, "name")
            _normalize_currency_field(entry, "currency")


def _normalize_customs_payload(data: dict[str, Any]) -> None:
    _normalize_country_field(data, "destination_country")
    _lower_field(data, "assessment_basis")
    _lower_field(data, "source_type")
    _normalize_sources(data, include_rate_type=False)

    lines = data.get("lines")
    if isinstance(lines, list):
        for line in lines:
            if not isinstance(line, dict):
                continue
            _strip_field(line, "line_id")
            if "hs_code" in line and line["hs_code"] is not None:
                line["hs_code"] = normalize_hs_code(str(line["hs_code"]))
            _strip_nullable_string_field(line, "legal_reference")
            _normalize_nullable_currency_field(line, "fixed_fee_currency")


def _normalize_fx_payload(data: dict[str, Any]) -> None:
    _normalize_currency_field(data, "base_currency")
    _normalize_currency_field(data, "quote_currency")
    _lower_field(data, "selected_rate_type")
    _normalize_sources(data, include_rate_type=True)

    official_rate = data.get("official_rate")
    if isinstance(official_rate, dict):
        _strip_field(official_rate, "provider_name")
        _strip_field(official_rate, "as_of")
        _strip_field(official_rate, "source_url")

    parallel_rate = data.get("parallel_rate")
    if isinstance(parallel_rate, dict):
        _strip_field(parallel_rate, "provider_name")
        _strip_field(parallel_rate, "as_of")
        _strip_field(parallel_rate, "source_url")


def _normalize_local_charges_payload(data: dict[str, Any]) -> None:
    _normalize_country_field(data, "destination_country")
    _normalize_currency_field(data, "currency")
    _lower_field(data, "source_type")
    _normalize_sources(data, include_rate_type=False)

    lines = data.get("lines")
    if isinstance(lines, list):
        for line in lines:
            if not isinstance(line, dict):
                continue
            _strip_field(line, "name")
            _normalize_currency_field(line, "currency")
            _strip_nullable_string_field(line, "notes")


def _normalize_risk_notes_payload(data: dict[str, Any]) -> None:
    _normalize_country_field(data, "destination_country")
    _lower_field(data, "risk_level")
    _lower_field(data, "source_type")
    _normalize_sources(data, include_rate_type=False)

    notes = data.get("notes")
    if isinstance(notes, list):
        for note in notes:
            if not isinstance(note, dict):
                continue
            _strip_field(note, "code")
            _strip_field(note, "title")
            _strip_field(note, "description")
            _lower_field(note, "impact_level")
            _strip_field(note, "recommendation")


def _normalize_sources(data: dict[str, Any], *, include_rate_type: bool) -> None:
    sources = data.get("sources")
    if not isinstance(sources, list):
        return
    for source in sources:
        if not isinstance(source, dict):
            continue
        _strip_field(source, "source_url")
        _strip_field(source, "source_title")
        _strip_field(source, "retrieved_at")
        _lower_field(source, "method")
        if include_rate_type:
            _lower_field(source, "rate_type")


def _normalize_country_field(data: dict[str, Any], key: str) -> None:
    value = data.get(key)
    if isinstance(value, str):
        data[key] = value.strip().upper()


def _normalize_currency_field(data: dict[str, Any], key: str) -> None:
    value = data.get(key)
    if value is None:
        return
    data[key] = normalize_currency(str(value))


def _normalize_nullable_currency_field(data: dict[str, Any], key: str) -> None:
    value = data.get(key)
    if value is None:
        return
    data[key] = normalize_currency(str(value))


def _strip_field(data: dict[str, Any], key: str) -> None:
    value = data.get(key)
    if isinstance(value, str):
        data[key] = value.strip()


def _strip_nullable_string_field(data: dict[str, Any], key: str) -> None:
    value = data.get(key)
    if value is None:
        return
    if isinstance(value, str):
        data[key] = value.strip()


def _lower_field(data: dict[str, Any], key: str) -> None:
    value = data.get(key)
    if isinstance(value, str):
        data[key] = value.strip().lower()
