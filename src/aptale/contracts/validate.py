"""Schema validation helpers for Aptale JSON contracts."""

from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from .errors import (
    MalformedPayloadError,
    PartialPayloadError,
    SchemaNotFoundError,
    SchemaValidationError,
)
from .normalize import (
    normalize_invoice_extraction_payload,
    normalize_landed_cost_input_payload,
)

_SCHEMA_FILES = {
    "invoice_extraction": "invoice_extraction.schema.json",
    "invoice_correction": "invoice_correction.schema.json",
    "freight_quote": "freight_quote.schema.json",
    "customs_quote": "customs_quote.schema.json",
    "fx_quote": "fx_quote.schema.json",
    "landed_cost_input": "landed_cost_input.schema.json",
    "landed_cost_output": "landed_cost_output.schema.json",
    "alert_rule": "alert_rule.schema.json",
}

_SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "schemas"


def available_schemas() -> tuple[str, ...]:
    """Return the supported canonical schema names."""
    return tuple(sorted(_SCHEMA_FILES.keys()))


@lru_cache(maxsize=None)
def load_schema(schema_name: str) -> dict[str, Any]:
    """Load and verify a JSON schema by canonical name."""
    schema_filename = _SCHEMA_FILES.get(schema_name)
    if schema_filename is None:
        raise SchemaNotFoundError(
            f"Unknown schema '{schema_name}'. Available: {', '.join(available_schemas())}"
        )

    schema_path = _SCHEMA_ROOT / schema_filename
    if not schema_path.is_file():
        raise SchemaNotFoundError(
            f"Schema file for '{schema_name}' not found at {schema_path}"
        )

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


@lru_cache(maxsize=None)
def _get_validator(schema_name: str) -> Draft202012Validator:
    return Draft202012Validator(load_schema(schema_name), format_checker=FormatChecker())


def validate_payload(schema_name: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    """
    Validate a payload against one of Aptale's canonical schemas.

    Raises:
      - MalformedPayloadError on malformed input shape/content.
      - SchemaValidationError on schema violations.
    """
    if not isinstance(payload, Mapping):
        raise MalformedPayloadError("Payload must be a mapping (JSON object).")

    data = dict(payload)
    _assert_no_non_finite_numbers(data)
    _assert_no_blank_strings(data)

    validator = _get_validator(schema_name)
    errors = sorted(validator.iter_errors(data), key=lambda err: list(err.path))
    if errors:
        formatted = [_format_schema_error(err) for err in errors]
        raise SchemaValidationError(schema_name=schema_name, errors=formatted)

    return data


def normalize_payload_for_schema(
    schema_name: str, payload: Mapping[str, Any]
) -> dict[str, Any]:
    """Normalize schema-relevant fields before validation."""
    if schema_name == "invoice_extraction":
        return normalize_invoice_extraction_payload(payload)
    if schema_name == "landed_cost_input":
        return normalize_landed_cost_input_payload(payload)
    return dict(payload)


def normalize_and_validate_payload(
    schema_name: str, payload: Mapping[str, Any]
) -> dict[str, Any]:
    """Normalize then validate a canonical payload."""
    normalized = normalize_payload_for_schema(schema_name, payload)
    return validate_payload(schema_name, normalized)


def validate_landed_cost_input(payload: Mapping[str, Any]) -> dict[str, Any]:
    """
    Normalize and validate landed-cost inputs with extra fail-fast checks.

    This rejects structurally valid but partial/mismatched payloads before
    deterministic cost computation.
    """
    data = normalize_and_validate_payload("landed_cost_input", payload)

    required_paths = (
        "invoice_total",
        "freight_quote_amount",
        "fx_selected_rate",
        "profit_margin_pct",
        "customs_lines",
        "quote_ids.freight_quote_id",
        "quote_ids.customs_quote_id",
        "quote_ids.fx_quote_id",
    )
    for path in required_paths:
        value = _value_at_path(data, path)
        if _is_empty(value):
            raise PartialPayloadError(
                f"Required calculation input '{path}' is missing or empty."
            )

    invoice_currency = data["invoice_currency"]
    freight_currency = data["freight_currency"]
    fx_base_currency = data["fx_base_currency"]
    local_currency = data["local_currency"]
    fx_quote_currency = data["fx_quote_currency"]

    # The Step 10 calculator path is single-base-currency only.
    if not (
        invoice_currency == freight_currency and invoice_currency == fx_base_currency
    ):
        raise PartialPayloadError(
            "invoice_currency, freight_currency, and fx_base_currency must match."
        )
    if local_currency != fx_quote_currency:
        raise PartialPayloadError(
            "local_currency must match fx_quote_currency for landed-cost calculation."
        )

    for idx, line in enumerate(data["customs_lines"]):
        fixed_fee = line.get("fixed_fee")
        fixed_fee_currency = line.get("fixed_fee_currency")
        if (fixed_fee is None) != (fixed_fee_currency is None):
            raise PartialPayloadError(
                "customs_lines[%d] fixed_fee and fixed_fee_currency must both be "
                "provided or both be null." % idx
            )

    return data


def _format_schema_error(error: Any) -> str:
    path = _json_path(error.path)
    return f"{path}: {error.message}"


def _json_path(path_parts: Iterable[Any]) -> str:
    path = "$"
    for part in path_parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _assert_no_non_finite_numbers(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise MalformedPayloadError(f"Non-finite number found at {path}.")
        return

    if isinstance(value, Mapping):
        for key, child in value.items():
            _assert_no_non_finite_numbers(child, f"{path}.{key}")
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_non_finite_numbers(child, f"{path}[{index}]")


def _assert_no_blank_strings(value: Any, path: str = "$") -> None:
    if isinstance(value, str):
        if value.strip() == "":
            raise MalformedPayloadError(f"Blank string found at {path}.")
        return

    if isinstance(value, Mapping):
        for key, child in value.items():
            _assert_no_blank_strings(child, f"{path}.{key}")
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_blank_strings(child, f"{path}[{index}]")


def _value_at_path(payload: Mapping[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, (list, tuple, set, dict)) and len(value) == 0:
        return True
    return False

