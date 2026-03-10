"""Fail-fast intake error models for poor image quality and missing fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class IntakeFailure(Exception):
    """Base deterministic intake failure used to halt sourcing."""

    code: str
    user_message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.user_message}"


@dataclass(frozen=True)
class BlurryImageFailure(IntakeFailure):
    """Image quality is too poor for reliable extraction."""

    code: str = "blurry_image"
    user_message: str = (
        "The invoice image is blurry or unreadable, so extraction is not reliable."
    )


@dataclass(frozen=True)
class MissingRouteFailure(IntakeFailure):
    """Required origin/destination route fields are missing."""

    code: str = "missing_route"
    user_message: str = (
        "Origin and destination details are incomplete in the extracted invoice."
    )


@dataclass(frozen=True)
class UnreadableTotalsFailure(IntakeFailure):
    """Invoice totals are missing or not parseable."""

    code: str = "unreadable_totals"
    user_message: str = "Invoice subtotal/total values are missing or unreadable."


@dataclass(frozen=True)
class UncertainHSCodeFailure(IntakeFailure):
    """HS code inference is missing or low-confidence."""

    code: str = "uncertain_hs_code"
    user_message: str = "HS code inference is uncertain and needs user confirmation."


def detect_intake_failures(
    extraction_payload: Mapping[str, Any],
    *,
    image_quality_score: float | None = None,
    hs_confidence_threshold: float = 0.8,
) -> list[IntakeFailure]:
    """
    Return deterministic intake failures found in the extraction payload.

    Ordering is significant for fail-fast handling:
    1) blurry image
    2) missing route
    3) unreadable totals
    4) uncertain HS code
    """
    if not isinstance(extraction_payload, Mapping):
        raise TypeError("extraction_payload must be a mapping.")

    failures: list[IntakeFailure] = []
    uncertainties = _to_string_list(extraction_payload.get("uncertainties"))
    uncertainty_blob = " ".join(uncertainties).lower()

    if _is_blurry(image_quality_score, uncertainty_blob):
        failures.append(BlurryImageFailure())

    if _is_missing_route(extraction_payload):
        failures.append(MissingRouteFailure())

    if _is_unreadable_totals(extraction_payload):
        failures.append(UnreadableTotalsFailure())

    if _has_uncertain_hs(extraction_payload, hs_confidence_threshold, uncertainty_blob):
        failures.append(UncertainHSCodeFailure())

    return failures


def ensure_intake_ready_for_clarification(
    extraction_payload: Mapping[str, Any],
    *,
    image_quality_score: float | None = None,
    hs_confidence_threshold: float = 0.8,
) -> None:
    """Raise first failure if intake extraction cannot proceed safely."""
    failures = detect_intake_failures(
        extraction_payload,
        image_quality_score=image_quality_score,
        hs_confidence_threshold=hs_confidence_threshold,
    )
    if failures:
        raise failures[0]


def _is_blurry(image_quality_score: float | None, uncertainty_blob: str) -> bool:
    if image_quality_score is not None and image_quality_score < 0.45:
        return True
    return any(
        marker in uncertainty_blob
        for marker in ("blurry", "illegible", "unreadable image", "low image quality")
    )


def _is_missing_route(payload: Mapping[str, Any]) -> bool:
    required = (
        payload.get("origin_country"),
        payload.get("destination_country"),
        payload.get("origin_port"),
        payload.get("destination_port"),
    )
    return any(_is_blank(value) for value in required)


def _is_unreadable_totals(payload: Mapping[str, Any]) -> bool:
    subtotal = payload.get("subtotal")
    total = payload.get("total")
    if not _is_positive_number(subtotal):
        return True
    if not _is_positive_number(total):
        return True
    return False


def _has_uncertain_hs(
    payload: Mapping[str, Any], threshold: float, uncertainty_blob: str
) -> bool:
    if any(marker in uncertainty_blob for marker in ("hs", "harmonized", "tariff")):
        return True

    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return True

    for item in items:
        if not isinstance(item, Mapping):
            return True
        hs_code = item.get("hs_code")
        hs_conf = item.get("hs_confidence")
        if _is_blank(hs_code):
            return True
        if not isinstance(hs_conf, (int, float)):
            return True
        if hs_conf < threshold:
            return True
    return False


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and value > 0


def _to_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return [str(value)]
    return [str(v) for v in value]

