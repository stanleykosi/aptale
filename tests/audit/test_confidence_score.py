from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.audit.confidence_score import compute_confidence_report  # noqa: E402
from aptale.delegation.result_models import ParsedSubagentResult  # noqa: E402


def _fixed_now() -> datetime:
    return datetime(2026, 3, 11, 10, 0, 0, tzinfo=timezone.utc)


def _parsed(task_type: str, payload: dict, schema_name: str) -> ParsedSubagentResult:
    return ParsedSubagentResult(task_type=task_type, schema_name=schema_name, payload=payload)


def test_compute_confidence_report_scores_high_for_fresh_official_sources() -> None:
    parsed = {
        "freight": _parsed(
            "freight",
            {
                "source_type": "forwarder_portal",
                "captured_at": "2026-03-11T09:58:00Z",
                "sources": [
                    {
                        "retrieved_at": "2026-03-11T09:57:00Z",
                    }
                ],
            },
            "freight_quote",
        ),
        "customs": _parsed(
            "customs",
            {
                "source_type": "government_portal",
                "captured_at": "2026-03-11T09:56:00Z",
                "sources": [
                    {
                        "retrieved_at": "2026-03-11T09:55:00Z",
                    }
                ],
            },
            "customs_quote",
        ),
    }

    report = compute_confidence_report(parsed, now_fn=_fixed_now)
    assert report.overall_score >= 0.8
    assert report.overall_band == "high"


def test_compute_confidence_report_drops_with_retries_and_advisory_failures() -> None:
    parsed = {
        "freight": _parsed(
            "freight",
            {
                "source_type": "open_web",
                "captured_at": "2026-03-08T09:58:00Z",
                "sources": [
                    {
                        "retrieved_at": "2026-03-08T09:57:00Z",
                    }
                ],
            },
            "freight_quote",
        )
    }

    report = compute_confidence_report(
        parsed,
        retry_count_by_task={"freight": 2},
        advisory_failures=("risk_notes",),
        now_fn=_fixed_now,
    )
    assert report.overall_band in {"low", "medium"}
    assert any("advisory leg unavailable" in reason for reason in report.reasons)
