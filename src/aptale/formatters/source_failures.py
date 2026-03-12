"""WhatsApp-friendly formatting for delegated sourcing failure messages."""

from __future__ import annotations

from aptale.delegation.error_policy import SourcingFailureCode, SourcingLegFailure

from .whatsapp_markdown import bold, bullets, join_sections, section

_LEG_LABELS = {
    "freight": "Freight sourcing",
    "customs": "Customs sourcing",
    "fx": "FX sourcing",
}

_FAILURE_REASON = {
    SourcingFailureCode.TIMEOUT: "Request timed out while sourcing rates.",
    SourcingFailureCode.PORTAL_OUTAGE: "Required portal appears unavailable/offline.",
    SourcingFailureCode.CAPTCHA_FAILURE: "Sourcing was blocked by a CAPTCHA challenge.",
    SourcingFailureCode.SCHEMA_VIOLATION: "Subagent returned invalid structured output.",
    SourcingFailureCode.EMPTY_RESULT: "Subagent returned no usable result.",
    SourcingFailureCode.UNKNOWN_FAILURE: "Sourcing failed with an unknown execution error.",
}


def render_source_failure(failure: SourcingLegFailure) -> str:
    """Render one sourcing-leg failure in concise WhatsApp markdown."""
    leg = _LEG_LABELS.get(failure.task_type, failure.task_type.upper())
    reason = _FAILURE_REASON[failure.code]
    next_step = (
        "I can switch this leg to open-web search now."
        if failure.can_switch_to_open_web_search
        else "Open-web switch is not available for this failure; rerun this leg after fixing the issue."
    )

    summary = bullets(
        [
            f"{bold('Failed leg')}: {leg}",
            f"{bold('Reason')}: {reason}",
            f"{bold('Detail')}: {_clean_detail(failure.detail)}",
            f"{bold('Retry Attempt')}: {failure.retry_attempt}",
            f"{bold('Source Strategy')}: {failure.source_strategy}",
            (
                f"{bold('Alternate Sources')}: "
                f"{'Switched to alternate sources' if failure.switched_to_alternate_sources else 'Primary source path'}"
            ),
            f"{bold('Open-web search path')}: {'Available' if failure.can_switch_to_open_web_search else 'Not available'}",
        ]
    )
    return join_sections(
        [
            section("Sourcing Leg Failed", summary),
            section("Next Step", next_step),
        ]
    )


def render_source_failures(failures: list[SourcingLegFailure]) -> str:
    """Render a combined message when multiple sourcing legs fail."""
    if not failures:
        raise ValueError("failures must not be empty.")
    if len(failures) == 1:
        return render_source_failure(failures[0])

    items = []
    for failure in failures:
        leg = _LEG_LABELS.get(failure.task_type, failure.task_type.upper())
        availability = "available" if failure.can_switch_to_open_web_search else "not available"
        items.append(
            f"{leg}: {_FAILURE_REASON[failure.code]} "
            f"attempt={failure.retry_attempt}, strategy={failure.source_strategy}. "
            f"Open-web switch {availability}."
        )

    return join_sections(
        [
            section("Sourcing Failures", bullets(items)),
            section(
                "Next Step",
                "Retry only the failed legs. Where available, switch failed freight/customs legs to open-web search.",
            ),
        ]
    )


def _clean_detail(detail: str) -> str:
    compact = " ".join(str(detail).split()).strip()
    if len(compact) <= 240:
        return compact
    return compact[:237] + "..."
