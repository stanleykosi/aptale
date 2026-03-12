"""Deterministic confidence scoring for sourced quote legs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence

from aptale.delegation.result_models import ParsedSubagentResult


@dataclass(frozen=True)
class LegConfidence:
    """Confidence details for one sourcing leg."""

    task_type: str
    score: float
    band: str
    reason: str

    def as_mapping(self) -> dict[str, Any]:
        return {
            "task_type": self.task_type,
            "score": round(self.score, 4),
            "band": self.band,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ConfidenceReport:
    """Aggregate confidence report for quote orchestration."""

    overall_score: float
    overall_band: str
    leg_scores: tuple[LegConfidence, ...]
    reasons: tuple[str, ...]

    def as_mapping(self) -> dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 4),
            "overall_band": self.overall_band,
            "leg_scores": [leg.as_mapping() for leg in self.leg_scores],
            "reasons": list(self.reasons),
        }


def compute_confidence_report(
    parsed_results: Mapping[str, ParsedSubagentResult],
    *,
    retry_count_by_task: Mapping[str, int] | None = None,
    advisory_failures: Sequence[str] = (),
    now_fn: Callable[[], datetime] | None = None,
) -> ConfidenceReport:
    """
    Compute deterministic confidence score from source quality + retries + freshness.

    Score range is [0, 1] and bands are:
    - high >= 0.80
    - medium >= 0.60 and < 0.80
    - low < 0.60
    """
    now = now_fn() if now_fn is not None else datetime.now(timezone.utc)
    retries = dict(retry_count_by_task or {})

    leg_scores: list[LegConfidence] = []
    reasons: list[str] = []

    for task_type, result in parsed_results.items():
        payload = dict(result.payload)
        source_type = str(payload.get("source_type") or "unknown").strip().lower()
        freshness = _freshness_score(payload=payload, now=now)
        reliability = _source_reliability(source_type=source_type, task_type=task_type)
        retry_penalty = min(max(int(retries.get(task_type, 0)), 0), 4) * 0.08

        score = max(0.0, min(1.0, 0.55 * reliability + 0.45 * freshness - retry_penalty))
        band = _band_for_score(score)
        reason = (
            f"reliability={reliability:.2f}, freshness={freshness:.2f}, "
            f"retries={int(retries.get(task_type, 0))}"
        )

        leg_scores.append(
            LegConfidence(
                task_type=task_type,
                score=score,
                band=band,
                reason=reason,
            )
        )

    for task in advisory_failures:
        reasons.append(f"advisory leg unavailable: {task}")

    if leg_scores:
        overall = sum(leg.score for leg in leg_scores) / len(leg_scores)
    else:
        overall = 0.0

    if advisory_failures:
        overall = max(0.0, overall - 0.05 * len(advisory_failures))

    overall_band = _band_for_score(overall)
    reasons.insert(0, f"overall={overall:.2f} ({overall_band})")

    return ConfidenceReport(
        overall_score=overall,
        overall_band=overall_band,
        leg_scores=tuple(sorted(leg_scores, key=lambda item: item.task_type)),
        reasons=tuple(reasons),
    )


def _source_reliability(*, source_type: str, task_type: str) -> float:
    if source_type in {
        "government_portal",
        "official_portal",
        "carrier_portal",
        "forwarder_portal",
        "trade_advisory",
        "official_rate",
    }:
        return 0.95
    if source_type in {"open_web", "parallel_rate"}:
        return 0.72
    # FX payloads may not expose source_type at root; sources remain authoritative.
    if task_type == "fx":
        return 0.82
    return 0.65


def _freshness_score(*, payload: Mapping[str, Any], now: datetime) -> float:
    timestamps: list[datetime] = []

    captured = _parse_iso(payload.get("captured_at"))
    if captured is not None:
        timestamps.append(captured)

    sources = payload.get("sources")
    if isinstance(sources, list):
        for source in sources:
            if not isinstance(source, Mapping):
                continue
            parsed = _parse_iso(source.get("retrieved_at"))
            if parsed is not None:
                timestamps.append(parsed)

    if not timestamps:
        return 0.50

    latest = max(timestamps)
    age_hours = max(0.0, (now.astimezone(timezone.utc) - latest).total_seconds() / 3600.0)
    if age_hours <= 6:
        return 0.98
    if age_hours <= 24:
        return 0.88
    if age_hours <= 72:
        return 0.75
    return 0.60


def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt_value = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=timezone.utc)
    return dt_value.astimezone(timezone.utc)


def _band_for_score(score: float) -> str:
    if score >= 0.80:
        return "high"
    if score >= 0.60:
        return "medium"
    return "low"
