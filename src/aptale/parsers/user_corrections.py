"""Parsers for user confirmation and correction responses."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import re
from typing import Any, Mapping

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError

CONFIRMATION_PHRASE = "confirmed"

_PATH_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\[\d+\]")
_SET_STATEMENT_RE = re.compile(r"^(?P<path>[A-Za-z_][A-Za-z0-9_.\[\]]*)\s*=\s*(?P<value>.+)$")
_REMOVE_STATEMENT_RE = re.compile(r"^remove\s+(?P<path>[A-Za-z_][A-Za-z0-9_.\[\]]*)$", re.I)


class CorrectionParseError(ValueError):
    """Raised when a user correction response cannot be parsed safely."""


class CorrectionApplyError(ValueError):
    """Raised when parsed corrections cannot be applied to extraction payload."""


def parse_user_corrections(
    response_text: str,
    *,
    extraction_id: str,
    now_fn: callable | None = None,
) -> dict[str, Any]:
    """
    Parse user response into canonical invoice_correction payload.

    Supported forms:
    - "Confirmed"
    - "field.path = value"
    - "remove field.path"
    Multiple statements can be newline- or semicolon-separated.
    """
    if not isinstance(response_text, str) or not response_text.strip():
        raise CorrectionParseError("User clarification response is empty.")
    if not isinstance(extraction_id, str) or not extraction_id.strip():
        raise CorrectionParseError("extraction_id is required for correction payload.")

    now = now_fn or (lambda: datetime.now(timezone.utc))
    cleaned = response_text.strip()

    if _looks_confirmed(cleaned):
        payload = {
            "schema_version": "1.0",
            "extraction_id": extraction_id,
            "confirmation_status": "confirmed",
            "corrected_at": _utc_iso(now()),
            "correction_notes": None,
            "corrections": [],
        }
        return _validate_correction_payload(payload)

    statements = _split_statements(cleaned)
    if not statements:
        raise CorrectionParseError("No correction statements were found.")

    corrections = [_parse_statement(stmt) for stmt in statements]
    payload = {
        "schema_version": "1.0",
        "extraction_id": extraction_id,
        "confirmation_status": "corrected",
        "corrected_at": _utc_iso(now()),
        "correction_notes": None,
        "corrections": corrections,
    }
    return _validate_correction_payload(payload)


def apply_invoice_corrections(
    invoice_extraction: Mapping[str, Any],
    invoice_correction: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply parsed invoice corrections to an extraction payload."""
    if not isinstance(invoice_extraction, Mapping):
        raise CorrectionApplyError("invoice_extraction must be a mapping.")

    payload = deepcopy(dict(invoice_extraction))
    try:
        correction = normalize_and_validate_payload("invoice_correction", invoice_correction)
    except ContractsError as exc:
        raise CorrectionApplyError("invoice_correction payload is invalid.") from exc

    if correction["confirmation_status"] == "confirmed":
        return payload

    for entry in correction["corrections"]:
        op = entry["operation"]
        pointer = entry["path"]
        tokens = _pointer_tokens(pointer)
        if not tokens:
            raise CorrectionApplyError(f"Invalid correction path: {pointer!r}")

        _apply_operation(payload, tokens, op, entry.get("value"))

    return payload


def _validate_correction_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    try:
        return normalize_and_validate_payload("invoice_correction", payload)
    except ContractsError as exc:
        raise CorrectionParseError("Parsed correction payload failed schema validation.") from exc


def _looks_confirmed(text: str) -> bool:
    normalized = text.strip().lower().strip(".!")
    return normalized == CONFIRMATION_PHRASE


def _split_statements(text: str) -> list[str]:
    statements: list[str] = []
    for line in text.replace(";", "\n").splitlines():
        cleaned = line.strip()
        if cleaned:
            statements.append(cleaned)
    return statements


def _parse_statement(statement: str) -> dict[str, Any]:
    remove_match = _REMOVE_STATEMENT_RE.match(statement)
    if remove_match:
        pointer = _to_json_pointer(remove_match.group("path"))
        return {
            "path": pointer,
            "operation": "remove",
            "value": None,
            "reason": None,
        }

    set_match = _SET_STATEMENT_RE.match(statement)
    if set_match:
        pointer = _to_json_pointer(set_match.group("path"))
        value = _parse_value(set_match.group("value"))
        return {
            "path": pointer,
            "operation": "replace",
            "value": value,
            "reason": None,
        }

    raise CorrectionParseError(
        f"Could not parse correction statement: {statement!r}. "
        "Use 'field = value' format."
    )


def _to_json_pointer(path_expr: str) -> str:
    tokens = _path_tokens(path_expr)
    if not tokens:
        raise CorrectionParseError(f"Invalid correction path: {path_expr!r}")
    return "/" + "/".join(str(token) for token in tokens)


def _path_tokens(path_expr: str) -> list[str | int]:
    path_expr = path_expr.strip()
    raw_tokens = _PATH_TOKEN_RE.findall(path_expr)
    if not raw_tokens:
        return []

    joined = "".join(raw_tokens)
    normalized_input = path_expr.replace(".", "")
    if joined != normalized_input:
        return []

    tokens: list[str | int] = []
    for token in raw_tokens:
        if token.startswith("["):
            tokens.append(int(token[1:-1]))
        else:
            tokens.append(token)
    return tokens


def _parse_value(raw: str) -> Any:
    text = raw.strip()
    if not text:
        raise CorrectionParseError("Correction value cannot be blank.")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if (text.startswith('"') and text.endswith('"')) or (
            text.startswith("'") and text.endswith("'")
        ):
            return text[1:-1]
        return text


def _pointer_tokens(pointer: str) -> list[str | int]:
    if not pointer.startswith("/"):
        return []
    out: list[str | int] = []
    for part in pointer.split("/")[1:]:
        unescaped = part.replace("~1", "/").replace("~0", "~")
        if unescaped.isdigit():
            out.append(int(unescaped))
        else:
            out.append(unescaped)
    return out


def _apply_operation(target: dict[str, Any], tokens: list[str | int], op: str, value: Any) -> None:
    parent, final_token = _resolve_parent(target, tokens)
    if isinstance(parent, list):
        _apply_list_operation(parent, final_token, op, value)
    elif isinstance(parent, dict):
        _apply_dict_operation(parent, final_token, op, value)
    else:
        raise CorrectionApplyError("Correction path parent is not addressable.")


def _resolve_parent(
    target: dict[str, Any], tokens: list[str | int]
) -> tuple[dict[str, Any] | list[Any], str | int]:
    current: Any = target
    for token in tokens[:-1]:
        if isinstance(current, list):
            if not isinstance(token, int) or token < 0 or token >= len(current):
                raise CorrectionApplyError("List index out of range in correction path.")
            current = current[token]
        elif isinstance(current, dict):
            if token not in current:
                raise CorrectionApplyError(f"Missing path segment in correction: {token!r}")
            current = current[token]
        else:
            raise CorrectionApplyError("Invalid traversal target in correction path.")
    return current, tokens[-1]


def _apply_dict_operation(
    parent: dict[str, Any], final_token: str | int, op: str, value: Any
) -> None:
    if not isinstance(final_token, str):
        raise CorrectionApplyError("Object field token must be a string.")

    if op == "remove":
        if final_token not in parent:
            raise CorrectionApplyError(f"Cannot remove missing field: {final_token!r}")
        del parent[final_token]
        return

    if op == "replace" and final_token not in parent:
        raise CorrectionApplyError(f"Cannot replace missing field: {final_token!r}")

    if op in {"replace", "set"}:
        parent[final_token] = value
        return

    raise CorrectionApplyError(f"Unsupported correction operation: {op!r}")


def _apply_list_operation(
    parent: list[Any], final_token: str | int, op: str, value: Any
) -> None:
    if not isinstance(final_token, int):
        raise CorrectionApplyError("List index token must be an integer.")
    if final_token < 0 or final_token >= len(parent):
        raise CorrectionApplyError("List index out of range in correction path.")

    if op == "remove":
        parent.pop(final_token)
        return
    if op in {"replace", "set"}:
        parent[final_token] = value
        return
    raise CorrectionApplyError(f"Unsupported correction operation: {op!r}")


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

