"""Hermes hook to sanitize PII/raw pricing fields before activity logging."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

LOG_FILE = Path.home() / ".hermes" / "hooks" / "pii-redactor" / "activity.log"
SUPPORTED_EVENTS = frozenset({"agent:step", "agent:end"})

REDACTED_SUPPLIER = "[REDACTED_SUPPLIER]"
REDACTED_ADDRESS = "[REDACTED_ADDRESS]"
REDACTED_INVOICE = "[REDACTED_INVOICE]"
REDACTED_PRICE = "[REDACTED_PRICE]"

_SUPPLIER_KEY_RE = re.compile(
    r"(supplier|vendor|consignor|shipper|exporter|seller|manufacturer)",
    re.IGNORECASE,
)
_ADDRESS_KEY_RE = re.compile(
    r"(address|street|building|postal|postcode|zip)",
    re.IGNORECASE,
)
_INVOICE_KEY_RE = re.compile(
    r"(invoice|bill(?:_?number|_?no)?|inv(?:_?number|_?no)?)",
    re.IGNORECASE,
)
_PRICE_KEY_RE = re.compile(
    r"(price|amount|subtotal|total|value|cost|rate|freight|duty|tax|quote)",
    re.IGNORECASE,
)

_SUPPLIER_LINE_RE = re.compile(r"(?im)\b(supplier|vendor)\s*[:\-]\s*([^\n\r;]+)")
_ADDRESS_RE = re.compile(
    r"\b\d{1,6}\s+[A-Za-z0-9][A-Za-z0-9.\- ]{1,60}\s"
    r"(Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Close|Court|Ct)\b"
    r"(?:,?\s*[A-Za-z0-9.\- ]{0,40})?",
    re.IGNORECASE,
)
_INVOICE_LABEL_RE = re.compile(
    r"(?i)\b(invoice(?:\s*(?:number|no\.?|#))?)\s*[:#-]?\s*([A-Z0-9][A-Z0-9\-_/]{2,})"
)
_INVOICE_TOKEN_RE = re.compile(r"(?i)\bINV[-_/ ]?[A-Z0-9]{3,}\b")
_PRICE_LABEL_RE = re.compile(
    r"(?i)\b(price|unit price|amount|subtotal|total|freight|duty|tax)\s*[:=]\s*"
    r"\d+(?:,\d{3})*(?:\.\d+)?"
)
_CURRENCY_AMOUNT_RE = re.compile(
    r"\b(?:USD|EUR|GBP|NGN|JPY|RUB|CNY|CAD|AUD|CHF|INR|KRW)\s*\d+(?:,\d{3})*(?:\.\d+)?\b"
    r"|[$€£¥₦₽]\s*\d+(?:,\d{3})*(?:\.\d+)?"
)


async def handle(event_type: str, context: dict) -> None:
    """Write sanitized activity entries for step/end events."""
    if event_type not in SUPPORTED_EVENTS:
        return

    safe_context = sanitize_for_logging(context)
    _append_log_entry(event_type=event_type, context=safe_context)


def sanitize_for_logging(context: Mapping[str, Any]) -> dict[str, Any]:
    """Return a redacted copy of hook context without mutating caller data."""
    copied = deepcopy(dict(context))
    literals = _collect_pii_literals(copied)
    return _redact_value(copied, literals=literals)


def _append_log_entry(*, event_type: str, context: dict[str, Any]) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "context": context,
    }
    with LOG_FILE.open("a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(entry, ensure_ascii=True, sort_keys=True) + "\n")


def _redact_value(
    value: Any,
    *,
    key_name: str | None = None,
    literals: dict[str, tuple[str, ...]] | None = None,
) -> Any:
    if key_name:
        replacement = _replacement_for_key(key_name)
        if replacement is not None:
            return replacement

    if isinstance(value, Mapping):
        return {
            str(key): _redact_value(child, key_name=str(key), literals=literals)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_redact_value(item, literals=literals) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value(item, literals=literals) for item in value)
    if isinstance(value, str):
        return _redact_text(value, literals=literals)
    return value


def _replacement_for_key(key_name: str) -> str | None:
    if _ADDRESS_KEY_RE.search(key_name):
        return REDACTED_ADDRESS
    if _SUPPLIER_KEY_RE.search(key_name):
        return REDACTED_SUPPLIER
    if _INVOICE_KEY_RE.search(key_name):
        return REDACTED_INVOICE
    if _PRICE_KEY_RE.search(key_name):
        return REDACTED_PRICE
    return None


def _redact_text(value: str, *, literals: dict[str, tuple[str, ...]] | None = None) -> str:
    redacted = value
    if literals:
        redacted = _replace_literals(redacted, literals.get("supplier", ()), REDACTED_SUPPLIER)
        redacted = _replace_literals(redacted, literals.get("address", ()), REDACTED_ADDRESS)
        redacted = _replace_literals(redacted, literals.get("invoice", ()), REDACTED_INVOICE)

    redacted = _SUPPLIER_LINE_RE.sub(lambda m: f"{m.group(1)}: {REDACTED_SUPPLIER}", redacted)
    redacted = _ADDRESS_RE.sub(REDACTED_ADDRESS, redacted)
    redacted = _INVOICE_LABEL_RE.sub(
        lambda m: f"{m.group(1)}: {REDACTED_INVOICE}",
        redacted,
    )
    redacted = _INVOICE_TOKEN_RE.sub(REDACTED_INVOICE, redacted)
    redacted = _PRICE_LABEL_RE.sub(lambda m: f"{m.group(1)}: {REDACTED_PRICE}", redacted)
    redacted = _CURRENCY_AMOUNT_RE.sub(REDACTED_PRICE, redacted)
    return redacted


def _collect_pii_literals(context: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    suppliers = _collect_literals_for_key_pattern(context, _SUPPLIER_KEY_RE)
    addresses = _collect_literals_for_key_pattern(context, _ADDRESS_KEY_RE)
    invoices = _collect_literals_for_key_pattern(context, _INVOICE_KEY_RE)
    return {
        "supplier": tuple(sorted(suppliers, key=len, reverse=True)),
        "address": tuple(sorted(addresses, key=len, reverse=True)),
        "invoice": tuple(sorted(invoices, key=len, reverse=True)),
    }


def _collect_literals_for_key_pattern(
    value: Any,
    key_pattern: re.Pattern[str],
    *,
    current_key: str | None = None,
) -> set[str]:
    literals: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_str = str(key)
            if key_pattern.search(key_str):
                literals.update(_string_values(child))
            literals.update(
                _collect_literals_for_key_pattern(child, key_pattern, current_key=key_str)
            )
        return literals
    if isinstance(value, list):
        for item in value:
            literals.update(
                _collect_literals_for_key_pattern(item, key_pattern, current_key=current_key)
            )
    return literals


def _string_values(value: Any) -> set[str]:
    results: set[str] = set()
    if isinstance(value, str):
        text = value.strip()
        if len(text) >= 3:
            results.add(text)
        return results
    if isinstance(value, Mapping):
        for child in value.values():
            results.update(_string_values(child))
        return results
    if isinstance(value, (list, tuple)):
        for child in value:
            results.update(_string_values(child))
    return results


def _replace_literals(text: str, values: Iterable[str], replacement: str) -> str:
    redacted = text
    for value in values:
        if not value:
            continue
        if value in redacted:
            redacted = redacted.replace(value, replacement)
    return redacted
