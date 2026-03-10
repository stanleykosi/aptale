"""Strict parser/validator for delegated subagent JSON outputs."""

from __future__ import annotations

import json
from typing import Any, Mapping

from aptale.contracts import validate_payload
from aptale.contracts.errors import ContractsError

from .result_models import (
    MissingCitationError,
    ParsedSubagentResult,
    SubagentResultError,
    normalize_subagent_payload,
    schema_name_for_task,
)


class SubagentResultParseError(SubagentResultError):
    """Raised when a subagent output cannot be parsed as strict JSON."""


class ProseSubagentOutputError(SubagentResultParseError):
    """Raised when subagent output includes prose or wrappers around JSON."""


class PartialJSONOutputError(SubagentResultParseError):
    """Raised when subagent output appears truncated/partial JSON."""


class SubagentResultValidationError(SubagentResultError):
    """Raised when normalized subagent JSON fails contract validation."""


def parse_subagent_output(*, task_type: str, raw_output: str) -> ParsedSubagentResult:
    """
    Parse one subagent output, enforcing strict JSON-only contract.

    Rejects prose wrappers, partial/truncated JSON, malformed payloads, missing
    citations, and schema-invalid output.
    """
    schema_name = schema_name_for_task(task_type)
    payload = _decode_json_object(raw_output, task_type=task_type)
    normalized = normalize_subagent_payload(task_type, payload)
    _assert_citations(task_type=task_type, payload=normalized)

    try:
        validated = validate_payload(schema_name, normalized)
    except ContractsError as exc:
        raise SubagentResultValidationError(
            f"{task_type} subagent output failed {schema_name} validation."
        ) from exc

    return ParsedSubagentResult(
        task_type=task_type,
        schema_name=schema_name,
        payload=validated,
    )


def parse_subagent_outputs(raw_outputs: Mapping[str, str]) -> dict[str, ParsedSubagentResult]:
    """Parse and validate a mapping of task_type -> raw subagent output."""
    if not isinstance(raw_outputs, Mapping):
        raise SubagentResultParseError("raw_outputs must be a mapping of task_type -> output.")

    parsed: dict[str, ParsedSubagentResult] = {}
    for task_type, raw_output in raw_outputs.items():
        parsed[task_type] = parse_subagent_output(task_type=task_type, raw_output=raw_output)
    return parsed


def _decode_json_object(raw_output: str, *, task_type: str) -> dict[str, Any]:
    if not isinstance(raw_output, str) or not raw_output.strip():
        raise SubagentResultParseError(
            f"{task_type} subagent output is empty. Expected strict JSON object."
        )

    text = raw_output.strip()
    if not text.startswith("{"):
        raise ProseSubagentOutputError(
            f"{task_type} subagent output must be JSON-only with no prose prefix."
        )

    decoder = json.JSONDecoder()
    try:
        parsed, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        if _looks_partial_json(exc, text):
            raise PartialJSONOutputError(
                f"{task_type} subagent output appears partial/truncated JSON."
            ) from exc
        raise SubagentResultParseError(
            f"{task_type} subagent output is not valid JSON: {exc.msg}."
        ) from exc

    if not isinstance(parsed, dict):
        raise ProseSubagentOutputError(
            f"{task_type} subagent output must be a JSON object."
        )
    if text[end:].strip():
        raise ProseSubagentOutputError(
            f"{task_type} subagent output must contain only JSON with no trailing prose."
        )
    return parsed


def _looks_partial_json(error: json.JSONDecodeError, text: str) -> bool:
    if error.pos >= len(text) - 1:
        return True
    msg = error.msg.lower()
    if "unterminated" in msg:
        return True
    if "expecting value" in msg and error.pos >= len(text) - 8:
        return True
    return False


def _assert_citations(*, task_type: str, payload: Mapping[str, Any]) -> None:
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise MissingCitationError(
            f"{task_type} output is missing required source citations."
        )

    required_fields = ["source_url", "source_title", "retrieved_at", "method"]
    if task_type == "fx":
        required_fields.append("rate_type")

    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            raise MissingCitationError(
                f"{task_type} citation at index {index} must be an object."
            )
        for field in required_fields:
            value = source.get(field)
            if not isinstance(value, str) or not value.strip():
                raise MissingCitationError(
                    f"{task_type} citation at index {index} is missing {field}."
                )

    if task_type == "fx":
        official = payload.get("official_rate")
        if not isinstance(official, Mapping):
            raise MissingCitationError("fx output is missing official_rate citation details.")
        source_url = official.get("source_url")
        if not isinstance(source_url, str) or not source_url.strip():
            raise MissingCitationError(
                "fx output official_rate is missing required source_url citation."
            )
