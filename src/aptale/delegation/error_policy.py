"""Fail-fast parent-side policy for delegated sourcing failures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .parse_results import (
    SubagentResultParseError,
    SubagentResultValidationError,
    parse_subagent_output,
)
from .result_models import (
    InvalidSubagentPayloadError,
    MissingCitationError,
    ParsedSubagentResult,
    UnsupportedTaskTypeError,
    schema_name_for_task,
)


class SourcingFailureCode(str, Enum):
    """Canonical failure codes for delegated sourcing legs."""

    TIMEOUT = "timeout"
    PORTAL_OUTAGE = "portal_outage"
    CAPTCHA_FAILURE = "captcha_failure"
    SCHEMA_VIOLATION = "schema_violation"
    EMPTY_RESULT = "empty_result"
    UNKNOWN_FAILURE = "unknown_failure"


@dataclass(frozen=True)
class SourcingLegFailure:
    """Structured parent-side failure record for one sourcing leg."""

    task_type: str
    code: SourcingFailureCode
    detail: str
    can_switch_to_open_web_search: bool
    retry_attempt: int = 0
    source_strategy: str = "default"
    switched_to_alternate_sources: bool = False


class SourcingLegFailureError(RuntimeError):
    """Raised when a delegated sourcing leg fails and must be surfaced upstream."""

    def __init__(self, failure: SourcingLegFailure) -> None:
        self.failure = failure
        super().__init__(
            f"{failure.task_type} sourcing failed ({failure.code.value}): {failure.detail}"
        )


def resolve_sourcing_leg(
    *,
    task_type: str,
    raw_output: str | None = None,
    execution_error: Exception | None = None,
    retry_attempt: int = 0,
    source_strategy: str = "default",
) -> ParsedSubagentResult:
    """
    Resolve one sourcing leg output, fail-fast on known failure categories.

    - Detects timeout, outage, CAPTCHA, schema violations, and empty outputs.
    - Raises `SourcingLegFailureError` with structured failure metadata when invalid.
    """
    try:
        schema_name_for_task(task_type)
    except UnsupportedTaskTypeError:
        raise

    if execution_error is not None:
        failure = classify_execution_error(
            task_type=task_type,
            error=execution_error,
            retry_attempt=retry_attempt,
            source_strategy=source_strategy,
        )
        raise SourcingLegFailureError(failure) from execution_error

    if raw_output is None or not raw_output.strip():
        raise SourcingLegFailureError(
            SourcingLegFailure(
                task_type=task_type,
                code=SourcingFailureCode.EMPTY_RESULT,
                detail="Subagent returned an empty result.",
                can_switch_to_open_web_search=_can_switch_to_open_web(
                    task_type=task_type,
                    code=SourcingFailureCode.EMPTY_RESULT,
                ),
                retry_attempt=retry_attempt,
                source_strategy=source_strategy,
                switched_to_alternate_sources=(source_strategy == "open_web_only"),
            )
        )

    try:
        return parse_subagent_output(task_type=task_type, raw_output=raw_output)
    except (
        SubagentResultParseError,
        SubagentResultValidationError,
        InvalidSubagentPayloadError,
        MissingCitationError,
    ) as exc:
        raise SourcingLegFailureError(
            SourcingLegFailure(
                task_type=task_type,
                code=SourcingFailureCode.SCHEMA_VIOLATION,
                detail=str(exc),
                can_switch_to_open_web_search=False,
                retry_attempt=retry_attempt,
                source_strategy=source_strategy,
                switched_to_alternate_sources=(source_strategy == "open_web_only"),
            )
        ) from exc


def classify_execution_error(
    *,
    task_type: str,
    error: Exception,
    retry_attempt: int = 0,
    source_strategy: str = "default",
) -> SourcingLegFailure:
    """Classify delegated subagent execution failures into canonical categories."""
    detail = str(error).strip() or error.__class__.__name__
    lowered = detail.lower()

    if _contains_any(lowered, ("timeout", "timed out", "deadline exceeded")):
        code = SourcingFailureCode.TIMEOUT
    elif _contains_any(lowered, ("captcha", "cf challenge", "cloudflare challenge")):
        code = SourcingFailureCode.CAPTCHA_FAILURE
    elif _contains_any(
        lowered,
        (
            "offline",
            "service unavailable",
            "503",
            "502",
            "500",
            "404",
            "not found",
            "portal unavailable",
            "connection refused",
            "dns",
            "host unreachable",
        ),
    ):
        code = SourcingFailureCode.PORTAL_OUTAGE
    else:
        code = SourcingFailureCode.UNKNOWN_FAILURE

    return SourcingLegFailure(
        task_type=task_type,
        code=code,
        detail=detail,
        can_switch_to_open_web_search=_can_switch_to_open_web(task_type=task_type, code=code),
        retry_attempt=retry_attempt,
        source_strategy=source_strategy,
        switched_to_alternate_sources=(source_strategy == "open_web_only"),
    )


def summarize_failure_for_parent(
    *,
    task_type: str,
    code: SourcingFailureCode,
    detail: str,
    retry_attempt: int = 0,
    source_strategy: str = "default",
    switched_to_alternate_sources: bool = False,
) -> dict[str, Any]:
    """
    Build a compact parent-side summary payload for a sourcing failure.

    This is intended for orchestrator and formatter handoff.
    """
    return {
        "task_type": task_type,
        "failure_code": code.value,
        "detail": detail,
        "can_switch_to_open_web_search": _can_switch_to_open_web(
            task_type=task_type,
            code=code,
        ),
        "retry_attempt": retry_attempt,
        "source_strategy": source_strategy,
        "switched_to_alternate_sources": switched_to_alternate_sources,
    }


def _can_switch_to_open_web(*, task_type: str, code: SourcingFailureCode) -> bool:
    # FX leg already uses open-web sourcing as canonical path in this stage.
    if task_type == "fx":
        return False
    return code in {
        SourcingFailureCode.TIMEOUT,
        SourcingFailureCode.PORTAL_OUTAGE,
        SourcingFailureCode.CAPTCHA_FAILURE,
        SourcingFailureCode.EMPTY_RESULT,
    }


def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token in text for token in tokens)
