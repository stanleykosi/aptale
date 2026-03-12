"""Audit trail assembly for sourced freight/customs/FX citations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from aptale.delegation.result_models import ParsedSubagentResult

_REQUIRED_TASKS = ("freight", "customs", "fx", "local_charges")
_OPTIONAL_TASKS = ("risk_notes",)
_TASK_ORDER = {name: index for index, name in enumerate(_REQUIRED_TASKS)}
_TASK_ORDER.update({name: len(_TASK_ORDER) + index for index, name in enumerate(_OPTIONAL_TASKS)})
_PORTAL_SOURCE_TYPES = frozenset(
    {
        "official_portal",
        "carrier_portal",
        "forwarder_portal",
        "government_portal",
        "trade_advisory",
    }
)


class SourceTrailError(ValueError):
    """Raised when source audit trail data cannot be assembled safely."""


@dataclass(frozen=True)
class SourceTrailEntry:
    """One citation row in the compact source audit trail."""

    task_type: str
    quote_id: str
    extraction_id: str
    source_url: str
    retrieved_at: str
    captured_at: str
    method: str
    source_type: str
    discovery_channel: str

    def as_mapping(self) -> dict[str, str]:
        """Return a JSON-serializable mapping for exports/logging."""
        return {
            "task_type": self.task_type,
            "quote_id": self.quote_id,
            "extraction_id": self.extraction_id,
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
            "captured_at": self.captured_at,
            "method": self.method,
            "source_type": self.source_type,
            "discovery_channel": self.discovery_channel,
        }


@dataclass(frozen=True)
class SourceTrail:
    """Compact internal audit object for quote/export source traceability."""

    extraction_id: str
    assembled_at: str
    entries: tuple[SourceTrailEntry, ...]

    def as_mapping(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "extraction_id": self.extraction_id,
            "assembled_at": self.assembled_at,
            "entries": [entry.as_mapping() for entry in self.entries],
        }


def assemble_source_trail(
    parsed_results: Mapping[str, ParsedSubagentResult],
    *,
    assembled_at: str | None = None,
) -> SourceTrail:
    """
    Build the canonical source trail from parsed subagent results.

    The incoming mapping is expected to come from Step-18 parsing/validation
    (`parse_subagent_outputs`) and must include freight, customs, and FX.
    """
    payloads = _collect_payloads(parsed_results)
    extraction_id = _resolve_extraction_id(payloads)

    entries: list[SourceTrailEntry] = []
    seen: set[tuple[str, str, str, str, str, str]] = set()

    task_types = list(_REQUIRED_TASKS)
    for optional in _OPTIONAL_TASKS:
        if optional in payloads:
            task_types.append(optional)

    for task_type in task_types:
        payload = payloads[task_type]
        quote_id = _require_non_blank_string(payload, "quote_id", context=task_type)
        captured_at = _require_non_blank_string(payload, "captured_at", context=task_type)
        sources = _require_sources(payload, context=task_type)

        if task_type in {"freight", "customs", "local_charges", "risk_notes"}:
            source_type = _require_non_blank_string(payload, "source_type", context=task_type)
            discovery_channel = _discovery_for_portal_source_type(source_type, context=task_type)
            for source in sources:
                source_url = _require_non_blank_string(source, "source_url", context=task_type)
                retrieved_at = _require_non_blank_string(source, "retrieved_at", context=task_type)
                method = _require_non_blank_string(source, "method", context=task_type)
                dedupe_key = (
                    task_type,
                    quote_id,
                    source_url,
                    retrieved_at,
                    method,
                    source_type,
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                entries.append(
                    SourceTrailEntry(
                        task_type=task_type,
                        quote_id=quote_id,
                        extraction_id=extraction_id,
                        source_url=source_url,
                        retrieved_at=retrieved_at,
                        captured_at=captured_at,
                        method=method,
                        source_type=source_type,
                        discovery_channel=discovery_channel,
                    )
                )
            continue

        for source in sources:
            source_url = _require_non_blank_string(source, "source_url", context=task_type)
            retrieved_at = _require_non_blank_string(source, "retrieved_at", context=task_type)
            method = _require_non_blank_string(source, "method", context=task_type)
            rate_type = _require_non_blank_string(source, "rate_type", context=task_type)
            source_type, discovery_channel = _source_and_discovery_for_fx_rate_type(
                rate_type, context=task_type
            )
            dedupe_key = (
                task_type,
                quote_id,
                source_url,
                retrieved_at,
                method,
                source_type,
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            entries.append(
                SourceTrailEntry(
                    task_type=task_type,
                    quote_id=quote_id,
                    extraction_id=extraction_id,
                    source_url=source_url,
                    retrieved_at=retrieved_at,
                    captured_at=captured_at,
                    method=method,
                    source_type=source_type,
                    discovery_channel=discovery_channel,
                )
            )

    entries.sort(key=lambda entry: (_TASK_ORDER[entry.task_type], entry.retrieved_at, entry.source_url))
    return SourceTrail(
        extraction_id=extraction_id,
        assembled_at=_normalize_assembled_at(assembled_at),
        entries=tuple(entries),
    )


def _collect_payloads(
    parsed_results: Mapping[str, ParsedSubagentResult]
) -> dict[str, Mapping[str, Any]]:
    if not isinstance(parsed_results, Mapping):
        raise SourceTrailError("parsed_results must be a mapping of task_type -> ParsedSubagentResult.")

    missing = [task for task in _REQUIRED_TASKS if task not in parsed_results]
    if missing:
        raise SourceTrailError(
            "Source trail requires all core task results (freight, customs, fx, local_charges). "
            f"Missing: {', '.join(sorted(missing))}."
        )

    payloads: dict[str, Mapping[str, Any]] = {}
    for task in _REQUIRED_TASKS:
        result = parsed_results[task]
        if not isinstance(result, ParsedSubagentResult):
            raise SourceTrailError(
                f"Expected ParsedSubagentResult for task '{task}', got {type(result).__name__}."
            )
        if result.task_type != task:
            raise SourceTrailError(
                f"Task/result mismatch for '{task}': result.task_type={result.task_type!r}."
            )
        if not isinstance(result.payload, Mapping):
            raise SourceTrailError(f"Parsed payload for '{task}' must be a mapping.")
        payloads[task] = result.payload
    for task in _OPTIONAL_TASKS:
        if task not in parsed_results:
            continue
        result = parsed_results[task]
        if not isinstance(result, ParsedSubagentResult):
            raise SourceTrailError(
                f"Expected ParsedSubagentResult for task '{task}', got {type(result).__name__}."
            )
        if result.task_type != task:
            raise SourceTrailError(
                f"Task/result mismatch for '{task}': result.task_type={result.task_type!r}."
            )
        if not isinstance(result.payload, Mapping):
            raise SourceTrailError(f"Parsed payload for '{task}' must be a mapping.")
        payloads[task] = result.payload
    return payloads


def _resolve_extraction_id(payloads: Mapping[str, Mapping[str, Any]]) -> str:
    extraction_ids: dict[str, str] = {}
    for task_type, payload in payloads.items():
        extraction_ids[task_type] = _require_non_blank_string(
            payload, "extraction_id", context=task_type
        )

    unique = set(extraction_ids.values())
    if len(unique) != 1:
        details = ", ".join(f"{task}={value}" for task, value in extraction_ids.items())
        raise SourceTrailError(
            "Source trail cannot be assembled because extraction_id values differ across task outputs: "
            f"{details}."
        )
    return next(iter(unique))


def _require_sources(payload: Mapping[str, Any], *, context: str) -> list[Mapping[str, Any]]:
    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise SourceTrailError(f"{context} payload must include at least one source entry.")

    sources: list[Mapping[str, Any]] = []
    for index, source in enumerate(raw_sources):
        if not isinstance(source, Mapping):
            raise SourceTrailError(f"{context} source at index {index} must be an object.")
        sources.append(source)
    return sources


def _require_non_blank_string(
    payload: Mapping[str, Any],
    key: str,
    *,
    context: str,
) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SourceTrailError(f"{context} payload is missing required field '{key}'.")
    return value.strip()


def _discovery_for_portal_source_type(source_type: str, *, context: str) -> str:
    normalized = source_type.strip().lower()
    if normalized == "open_web":
        return "open_web"
    if normalized in _PORTAL_SOURCE_TYPES:
        return "official_portal"
    raise SourceTrailError(
        f"{context} payload has unsupported source_type {source_type!r}."
    )


def _source_and_discovery_for_fx_rate_type(
    rate_type: str, *, context: str
) -> tuple[str, str]:
    normalized = rate_type.strip().lower()
    if normalized == "official":
        return "official_rate", "official_portal"
    if normalized == "parallel":
        return "parallel_rate", "open_web"
    raise SourceTrailError(
        f"{context} source has unsupported rate_type {rate_type!r}."
    )


def _normalize_assembled_at(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if not isinstance(value, str) or not value.strip():
        raise SourceTrailError("assembled_at must be a non-empty ISO-8601 timestamp string.")
    return value.strip()
