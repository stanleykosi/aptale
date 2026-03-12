"""Normalization helpers for canonical Aptale payload contracts."""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Mapping

from .errors import NormalizationError

_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_HS_RE = re.compile(r"^[0-9]{4,10}$")
_WEIGHT_RE = re.compile(
    r"^\s*(?P<value>-?[0-9]+(?:\.[0-9]+)?)\s*(?P<unit>[a-zA-Z_]+)?\s*$"
)

_INCOTERMS_2020 = frozenset(
    {"EXW", "FCA", "CPT", "CIP", "DAP", "DPU", "DDP", "FAS", "FOB", "CFR", "CIF"}
)

_WEIGHT_FACTORS = {
    "kg": 1.0,
    "kgs": 1.0,
    "kilogram": 1.0,
    "kilograms": 1.0,
    "g": 0.001,
    "gram": 0.001,
    "grams": 0.001,
    "lb": 0.45359237,
    "lbs": 0.45359237,
    "pound": 0.45359237,
    "pounds": 0.45359237,
    "oz": 0.028349523125,
    "ounce": 0.028349523125,
    "ounces": 0.028349523125,
    "ton": 1000.0,
    "tons": 1000.0,
    "tonne": 1000.0,
    "tonnes": 1000.0,
    "mt": 1000.0,
    "metric_ton": 1000.0,
}


def normalize_currency(value: str) -> str:
    """Normalize currency code to ISO-4217 uppercase 3-letter form."""
    if not isinstance(value, str):
        raise NormalizationError("Currency code must be a string.")

    code = value.strip().upper()
    if not _CURRENCY_RE.fullmatch(code):
        raise NormalizationError(f"Invalid currency code: {value!r}")
    return code


def normalize_incoterm(value: str | None) -> str | None:
    """Normalize Incoterm to canonical uppercase code."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise NormalizationError("Incoterm must be a string or null.")

    term = value.strip().upper()
    if term not in _INCOTERMS_2020:
        raise NormalizationError(f"Unsupported Incoterm: {value!r}")
    return term


def normalize_hs_code(value: str | None) -> str | None:
    """Normalize HS code by removing separators and validating length."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise NormalizationError("HS code must be a string or null.")

    digits = re.sub(r"[^0-9]", "", value)
    if not _HS_RE.fullmatch(digits):
        raise NormalizationError(f"Invalid HS code: {value!r}")
    return digits


def normalize_weight_to_kg(value: Any, unit: str | None = None) -> float:
    """Normalize a weight value into kilograms."""
    if value is None:
        raise NormalizationError("Weight cannot be null when normalization is requested.")

    parsed_value: Any = value
    parsed_unit = unit

    if isinstance(value, str):
        match = _WEIGHT_RE.match(value)
        if not match:
            raise NormalizationError(f"Invalid weight value: {value!r}")
        parsed_value = match.group("value")
        if parsed_unit is None and match.group("unit"):
            parsed_unit = match.group("unit")

    try:
        weight = Decimal(str(parsed_value))
    except (InvalidOperation, ValueError) as exc:
        raise NormalizationError(f"Weight is not numeric: {value!r}") from exc

    if weight < 0:
        raise NormalizationError("Weight cannot be negative.")

    canonical_unit = (parsed_unit or "kg").strip().lower()
    if canonical_unit not in _WEIGHT_FACTORS:
        raise NormalizationError(f"Unsupported weight unit: {parsed_unit!r}")

    return float(weight * Decimal(str(_WEIGHT_FACTORS[canonical_unit])))


def normalize_invoice_extraction_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize invoice extraction payload fields used across later stages."""
    data = deepcopy(dict(payload))

    if "currency" in data and data["currency"] is not None:
        data["currency"] = normalize_currency(data["currency"])
    if "incoterm" in data:
        data["incoterm"] = normalize_incoterm(data["incoterm"])
    if "total_weight_kg" in data and data["total_weight_kg"] is not None:
        data["total_weight_kg"] = normalize_weight_to_kg(data["total_weight_kg"], "kg")

    for country_key in ("origin_country", "destination_country"):
        if country_key in data and isinstance(data[country_key], str):
            data[country_key] = data[country_key].strip().upper()

    items = data.get("items")
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            if "hs_code" in item:
                item["hs_code"] = normalize_hs_code(item["hs_code"])
            if "weight_kg" in item and item["weight_kg"] is not None:
                item["weight_kg"] = normalize_weight_to_kg(item["weight_kg"], "kg")
            if "country_of_origin" in item and isinstance(item["country_of_origin"], str):
                item["country_of_origin"] = item["country_of_origin"].strip().upper()

    return data


def normalize_landed_cost_input_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize landed-cost input payload prior to deterministic calculation."""
    data = deepcopy(dict(payload))

    for key in (
        "invoice_currency",
        "freight_currency",
        "fx_base_currency",
        "fx_quote_currency",
        "local_charges_currency",
        "local_currency",
    ):
        if key in data and data[key] is not None:
            data[key] = normalize_currency(data[key])

    if "invoice_total_weight_kg" in data and data["invoice_total_weight_kg"] is not None:
        data["invoice_total_weight_kg"] = normalize_weight_to_kg(
            data["invoice_total_weight_kg"], "kg"
        )

    customs_lines = data.get("customs_lines")
    if isinstance(customs_lines, list):
        for line in customs_lines:
            if not isinstance(line, dict):
                continue
            if "hs_code" in line:
                line["hs_code"] = normalize_hs_code(line["hs_code"])
            if "fixed_fee_currency" in line and line["fixed_fee_currency"] is not None:
                line["fixed_fee_currency"] = normalize_currency(line["fixed_fee_currency"])

    return data
