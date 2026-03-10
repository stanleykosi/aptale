"""HS code inference layer for canonical invoice extraction payloads."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError
from aptale.contracts.normalize import normalize_hs_code

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


class HSCodeInferenceError(RuntimeError):
    """Raised when HS inference cannot safely produce canonical output."""


@dataclass(frozen=True)
class HSCodeProposal:
    """Normalized HS proposal for a line item."""

    hs_code: str | None
    confidence: float | None
    reason: str | None = None


class HSCodeInferenceEngine(Protocol):
    """Interface for line-item HS inference providers."""

    def __call__(
        self, *, item: Mapping[str, Any], context: Mapping[str, Any], prompt: str
    ) -> Mapping[str, Any]:
        ...


def infer_hs_codes(
    extraction_payload: Mapping[str, Any],
    *,
    inference_engine: HSCodeInferenceEngine | None = None,
    confidence_threshold: float = 0.8,
) -> dict[str, Any]:
    """
    Infer HS code proposals per line item and flag low-confidence cases.

    Output remains in canonical `invoice_extraction` contract format.
    """
    if not isinstance(extraction_payload, Mapping):
        raise HSCodeInferenceError("extraction_payload must be a mapping.")
    if confidence_threshold < 0 or confidence_threshold > 1:
        raise HSCodeInferenceError("confidence_threshold must be in [0, 1].")
    if inference_engine is not None and not callable(inference_engine):
        raise HSCodeInferenceError("inference_engine must be callable when provided.")

    try:
        validated = normalize_and_validate_payload("invoice_extraction", extraction_payload)
    except ContractsError as exc:
        raise HSCodeInferenceError("Input extraction payload is invalid.") from exc

    prompt = _load_prompt("hs_code_inference.md")
    updated = deepcopy(validated)
    uncertainties = list(updated.get("uncertainties") or [])

    for index, item in enumerate(updated["items"], start=1):
        proposal = _propose_hs_code(
            item=item,
            extraction=updated,
            inference_engine=inference_engine,
            prompt=prompt,
        )
        _apply_proposal(item, proposal)
        if _is_low_confidence(item, threshold=confidence_threshold):
            uncertainties.append(_uncertainty_message(index, item))

    updated["uncertainties"] = _dedupe_preserve_order(uncertainties)
    updated["needs_user_confirmation"] = bool(updated["uncertainties"])

    try:
        return normalize_and_validate_payload("invoice_extraction", updated)
    except ContractsError as exc:
        raise HSCodeInferenceError("HS inference output failed invoice schema validation.") from exc


def _propose_hs_code(
    *,
    item: Mapping[str, Any],
    extraction: Mapping[str, Any],
    inference_engine: HSCodeInferenceEngine | None,
    prompt: str,
) -> HSCodeProposal:
    if inference_engine is None:
        return HSCodeProposal(
            hs_code=item.get("hs_code"),
            confidence=item.get("hs_confidence"),
            reason="kept existing value",
        )

    raw = inference_engine(item=item, context=extraction, prompt=prompt)
    if not isinstance(raw, Mapping):
        raise HSCodeInferenceError("HS inference engine must return a mapping.")

    hs_code_raw = raw.get("hs_code")
    confidence_raw = raw.get("confidence")
    reason_raw = raw.get("reason")

    normalized_code = normalize_hs_code(hs_code_raw) if hs_code_raw is not None else None
    if confidence_raw is None:
        confidence = None
    elif isinstance(confidence_raw, (int, float)):
        confidence = float(confidence_raw)
    else:
        raise HSCodeInferenceError("HS inference confidence must be numeric or null.")

    if confidence is not None and not (0.0 <= confidence <= 1.0):
        raise HSCodeInferenceError("HS inference confidence must be within [0, 1].")

    reason = str(reason_raw).strip() if reason_raw is not None else None
    return HSCodeProposal(hs_code=normalized_code, confidence=confidence, reason=reason)


def _apply_proposal(item: dict[str, Any], proposal: HSCodeProposal) -> None:
    current_code = item.get("hs_code")
    current_conf = item.get("hs_confidence")

    if proposal.hs_code is None and current_code is not None:
        return

    if proposal.confidence is not None and isinstance(current_conf, (int, float)):
        if current_code and current_conf >= proposal.confidence:
            return

    item["hs_code"] = proposal.hs_code
    item["hs_confidence"] = proposal.confidence


def _is_low_confidence(item: Mapping[str, Any], *, threshold: float) -> bool:
    hs_code = item.get("hs_code")
    conf = item.get("hs_confidence")
    if hs_code is None:
        return True
    if not isinstance(conf, (int, float)):
        return True
    return conf < threshold


def _uncertainty_message(index: int, item: Mapping[str, Any]) -> str:
    description = str(item.get("description") or f"item {index}")
    confidence = item.get("hs_confidence")
    if isinstance(confidence, (int, float)):
        return (
            f"hs_code_low_confidence: line {index} ({description}) confidence={confidence:.2f}"
        )
    return f"hs_code_missing_or_unknown: line {index} ({description})"


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = value.strip()
        if key and key not in seen:
            seen.add(key)
            out.append(key)
    return out


def _load_prompt(filename: str) -> str:
    path = _PROMPTS_DIR / filename
    if not path.is_file():
        raise HSCodeInferenceError(f"Required prompt file missing: {path}")
    return path.read_text(encoding="utf-8").strip()

