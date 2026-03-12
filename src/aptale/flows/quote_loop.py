"""Canonical invoice->clarify->delegate->calculate->export orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from aptale.audit.source_trail import assemble_source_trail
from aptale.calc.landed_cost import calculate_landed_cost
from aptale.delegation.build_tasks import build_sourcing_tasks
from aptale.delegation.error_policy import (
    SourcingFailureCode,
    SourcingLegFailure,
    SourcingLegFailureError,
    resolve_sourcing_leg,
    summarize_failure_for_parent,
)
from aptale.delegation.result_models import ParsedSubagentResult
from aptale.flows.clarify_extraction import (
    assert_sourcing_allowed,
    begin_clarification,
    process_clarification_response,
)
from aptale.flows.intake_failure_responses import build_intake_failure_response
from aptale.flows.invoice_intake import MultimodalExtractor, orchestrate_invoice_intake
from aptale.flows.route_inference import RouteInferenceEngine, infer_route_context
from aptale.flows.send_export import assemble_whatsapp_export_response
from aptale.formatters.source_failures import render_source_failure, render_source_failures


class QuoteLoopError(RuntimeError):
    """Raised when quote-loop orchestration cannot proceed safely."""


class DelegateTaskOutputError(QuoteLoopError):
    """Raised when delegate task output shape is unsupported."""


class MissingUserProfileFieldError(QuoteLoopError):
    """Raised when required user profile values are missing for calculation."""


class DelegateTaskRunner(Protocol):
    """Callable wrapper around Hermes `delegate_task` execution."""

    def __call__(self, *, tasks: Sequence[Mapping[str, Any]]) -> Any:
        ...


@dataclass(frozen=True)
class QuoteLoopResult:
    """Unified result payload for the Aptale quote loop."""

    status: str
    next_step: str
    user_message: str
    invoice_extraction: Mapping[str, Any] | None = None
    route_status: str | None = None
    local_currency: str | None = None
    landed_cost_output: Mapping[str, Any] | None = None
    export_response: Mapping[str, Any] | None = None
    source_trail: Mapping[str, Any] | None = None
    sourcing_failures: tuple[Mapping[str, Any], ...] = ()

    def as_mapping(self) -> dict[str, Any]:
        """Return a JSON-serializable mapping."""
        return {
            "status": self.status,
            "next_step": self.next_step,
            "user_message": self.user_message,
            "invoice_extraction": self.invoice_extraction,
            "route_status": self.route_status,
            "local_currency": self.local_currency,
            "landed_cost_output": self.landed_cost_output,
            "export_response": self.export_response,
            "source_trail": self.source_trail,
            "sourcing_failures": [dict(item) for item in self.sourcing_failures],
        }


def begin_invoice_quote_loop(
    whatsapp_event: Mapping[str, Any],
    *,
    multimodal_extractor: MultimodalExtractor,
    user_profile: Mapping[str, Any] | None = None,
    image_quality_score: float | None = None,
    hs_confidence_threshold: float = 0.8,
    now_fn: Callable[[], datetime] | None = None,
) -> QuoteLoopResult:
    """
    Run intake and return clarification prompt (or fail-fast intake block).

    This is the first runtime phase for WhatsApp image intake.
    """
    intake_result = orchestrate_invoice_intake(
        whatsapp_event,
        multimodal_extractor=multimodal_extractor,
        user_profile=user_profile,
        now_fn=now_fn,
    )
    intake_failure = build_intake_failure_response(
        intake_result.invoice_extraction,
        image_quality_score=image_quality_score,
        hs_confidence_threshold=hs_confidence_threshold,
    )
    if intake_failure is not None:
        return QuoteLoopResult(
            status="intake_blocked",
            next_step="await_invoice_retry",
            user_message=intake_failure,
        )

    clarification = begin_clarification(intake_result.invoice_extraction)
    return QuoteLoopResult(
        status=clarification.status,
        next_step=clarification.next_step,
        user_message=clarification.clarify_message,
        invoice_extraction=clarification.invoice_extraction,
    )


def complete_invoice_quote_loop(
    *,
    invoice_extraction: Mapping[str, Any],
    clarification_response: str,
    delegate_task_runner: DelegateTaskRunner,
    user_profile: Mapping[str, Any],
    recent_chat_context: Sequence[str] | None = None,
    inference_engine: RouteInferenceEngine | None = None,
    subagent_model: str | None = None,
    export_format: str = "pdf",
    output_dir: str | Path = "/workspace",
    filename_stem: str | None = None,
    now_fn: Callable[[], datetime] | None = None,
) -> QuoteLoopResult:
    """
    Complete the loop from clarification to WhatsApp export delivery payload.

    This phase requires a stored invoice extraction payload plus user
    clarification response.
    """
    if not isinstance(user_profile, Mapping):
        raise QuoteLoopError("user_profile must be a mapping.")
    if not callable(delegate_task_runner):
        raise QuoteLoopError("delegate_task_runner must be callable.")
    if not isinstance(clarification_response, str) or not clarification_response.strip():
        raise QuoteLoopError("clarification_response must be a non-empty string.")

    now = now_fn or (lambda: datetime.now(timezone.utc))
    clarified = process_clarification_response(
        invoice_extraction,
        clarification_response,
        now_fn=now,
    )
    assert_sourcing_allowed(clarified)

    route_result = infer_route_context(
        clarified.invoice_extraction,
        user_profile=user_profile,
        recent_chat_context=recent_chat_context or (),
        inference_engine=inference_engine,
    )
    if not route_result.can_source or route_result.local_currency is None:
        return QuoteLoopResult(
            status=route_result.status,
            next_step=route_result.next_step,
            user_message=route_result.route_required_prompt
            or "Route details are required before sourcing can run.",
            invoice_extraction=route_result.invoice_extraction,
            route_status=route_result.status,
            local_currency=route_result.local_currency,
        )

    tasks = build_sourcing_tasks(
        invoice_extraction=route_result.invoice_extraction,
        local_currency=route_result.local_currency,
        user_profile=user_profile,
        extraction_status=clarified.status,
        route_status=route_result.status,
        subagent_model=subagent_model,
    )

    delegate_outputs = delegate_task_runner(tasks=tasks)
    raw_outputs = _coerce_delegate_outputs(tasks=tasks, delegate_outputs=delegate_outputs)
    parsed_results, failures = _resolve_sourcing_results(
        tasks=tasks,
        raw_outputs=raw_outputs,
    )
    if failures:
        return QuoteLoopResult(
            status="sourcing_failed",
            next_step="retry_failed_sourcing_legs",
            user_message=_render_sourcing_failure_message(failures),
            invoice_extraction=route_result.invoice_extraction,
            route_status=route_result.status,
            local_currency=route_result.local_currency,
            sourcing_failures=tuple(
                summarize_failure_for_parent(
                    task_type=failure.task_type,
                    code=failure.code,
                    detail=failure.detail,
                )
                for failure in failures
            ),
        )

    requested_at = _utc_iso(now())
    landed_cost_input = _build_landed_cost_input(
        invoice_extraction=route_result.invoice_extraction,
        parsed_results=parsed_results,
        local_currency=route_result.local_currency,
        user_profile=user_profile,
        requested_at=requested_at,
    )
    landed_cost_output = calculate_landed_cost(landed_cost_input, now_fn=now)
    export_result = assemble_whatsapp_export_response(
        landed_cost_output,
        export_format=export_format,
        output_dir=output_dir,
        filename_stem=filename_stem,
    )
    source_trail = assemble_source_trail(parsed_results, assembled_at=requested_at)
    return QuoteLoopResult(
        status="completed",
        next_step="send_whatsapp_export",
        user_message=export_result.message_markdown,
        invoice_extraction=route_result.invoice_extraction,
        route_status=route_result.status,
        local_currency=route_result.local_currency,
        landed_cost_output=landed_cost_output,
        export_response=export_result.as_mapping(),
        source_trail=source_trail.as_mapping(),
    )


def run_invoice_quote_loop(
    whatsapp_event: Mapping[str, Any],
    *,
    multimodal_extractor: MultimodalExtractor,
    delegate_task_runner: DelegateTaskRunner | None = None,
    user_profile: Mapping[str, Any] | None = None,
    clarification_response: str | None = None,
    recent_chat_context: Sequence[str] | None = None,
    inference_engine: RouteInferenceEngine | None = None,
    subagent_model: str | None = None,
    export_format: str = "pdf",
    output_dir: str | Path = "/workspace",
    filename_stem: str | None = None,
    image_quality_score: float | None = None,
    hs_confidence_threshold: float = 0.8,
    now_fn: Callable[[], datetime] | None = None,
) -> QuoteLoopResult:
    """
    Convenience wrapper for running both phases in one call.

    If `clarification_response` is omitted, this returns the clarification-stage
    prompt and extraction payload for storage between WhatsApp turns.
    """
    profile = dict(user_profile or {})
    begin_result = begin_invoice_quote_loop(
        whatsapp_event,
        multimodal_extractor=multimodal_extractor,
        user_profile=profile,
        image_quality_score=image_quality_score,
        hs_confidence_threshold=hs_confidence_threshold,
        now_fn=now_fn,
    )
    if begin_result.status != "awaiting_clarification":
        return begin_result
    if clarification_response is None or not clarification_response.strip():
        return begin_result
    if delegate_task_runner is None:
        raise QuoteLoopError(
            "delegate_task_runner is required when clarification_response is provided."
        )
    if begin_result.invoice_extraction is None:
        raise QuoteLoopError("begin phase did not provide invoice_extraction state.")

    return complete_invoice_quote_loop(
        invoice_extraction=begin_result.invoice_extraction,
        clarification_response=clarification_response,
        delegate_task_runner=delegate_task_runner,
        user_profile=profile,
        recent_chat_context=recent_chat_context,
        inference_engine=inference_engine,
        subagent_model=subagent_model,
        export_format=export_format,
        output_dir=output_dir,
        filename_stem=filename_stem,
        now_fn=now_fn,
    )


def _coerce_delegate_outputs(
    *,
    tasks: Sequence[Mapping[str, Any]],
    delegate_outputs: Any,
) -> dict[str, str]:
    task_types = _task_types_from_tasks(tasks)

    if isinstance(delegate_outputs, Mapping):
        raw_outputs: dict[str, str] = {}
        for task_type in task_types:
            raw = delegate_outputs.get(task_type)
            if not isinstance(raw, str):
                raise DelegateTaskOutputError(
                    f"delegate output for task '{task_type}' must be a string."
                )
            raw_outputs[task_type] = raw
        return raw_outputs

    if isinstance(delegate_outputs, Sequence) and not isinstance(
        delegate_outputs, (str, bytes, bytearray)
    ):
        if len(delegate_outputs) != len(task_types):
            raise DelegateTaskOutputError(
                f"delegate output list length {len(delegate_outputs)} does not match "
                f"task count {len(task_types)}."
            )
        raw_outputs = {}
        for index, item in enumerate(delegate_outputs):
            task_type = task_types[index]
            if isinstance(item, str):
                raw_outputs[task_type] = item
                continue
            if isinstance(item, Mapping):
                raw = item.get("output")
                if raw is None:
                    raw = item.get("result")
                if raw is None:
                    raw = item.get("summary")
                if isinstance(raw, str):
                    raw_outputs[task_type] = raw
                    continue
            raise DelegateTaskOutputError(
                f"delegate output item at index {index} for task '{task_type}' "
                "must be a string or a mapping with string output/result/summary."
            )
        return raw_outputs

    raise DelegateTaskOutputError(
        "delegate_task_runner must return either a mapping of task_type->string "
        "or an ordered sequence of strings."
    )


def _task_types_from_tasks(tasks: Sequence[Mapping[str, Any]]) -> list[str]:
    if not isinstance(tasks, Sequence):
        raise DelegateTaskOutputError("tasks must be a sequence.")
    task_types: list[str] = []
    for index, task in enumerate(tasks):
        if not isinstance(task, Mapping):
            raise DelegateTaskOutputError(f"Task at index {index} must be a mapping.")
        task_type = task.get("task_type")
        if not isinstance(task_type, str) or not task_type.strip():
            raise DelegateTaskOutputError(
                f"Task at index {index} missing non-empty task_type."
            )
        task_types.append(task_type.strip())
    return task_types


def _resolve_sourcing_results(
    *,
    tasks: Sequence[Mapping[str, Any]],
    raw_outputs: Mapping[str, str],
) -> tuple[dict[str, ParsedSubagentResult], list[SourcingLegFailure]]:
    parsed_results: dict[str, ParsedSubagentResult] = {}
    failures: list[SourcingLegFailure] = []
    task_types = _task_types_from_tasks(tasks)

    for task_type in task_types:
        raw_output = raw_outputs.get(task_type)
        if raw_output is None:
            failures.append(
                SourcingLegFailure(
                    task_type=task_type,
                    code=SourcingFailureCode.EMPTY_RESULT,
                    detail="Subagent output missing for this task.",
                    can_switch_to_open_web_search=(task_type != "fx"),
                )
            )
            continue
        try:
            parsed_results[task_type] = resolve_sourcing_leg(
                task_type=task_type,
                raw_output=raw_output,
            )
        except SourcingLegFailureError as exc:
            failures.append(exc.failure)

    return parsed_results, failures


def _build_landed_cost_input(
    *,
    invoice_extraction: Mapping[str, Any],
    parsed_results: Mapping[str, ParsedSubagentResult],
    local_currency: str,
    user_profile: Mapping[str, Any],
    requested_at: str,
) -> dict[str, Any]:
    freight = parsed_results["freight"].payload
    customs = parsed_results["customs"].payload
    fx = parsed_results["fx"].payload

    profit_margin_pct = _extract_profit_margin_pct(user_profile)
    return {
        "schema_version": "1.0",
        "extraction_id": invoice_extraction["extraction_id"],
        "invoice_currency": invoice_extraction["currency"],
        "invoice_total": invoice_extraction["total"],
        "invoice_total_weight_kg": invoice_extraction["total_weight_kg"],
        "freight_currency": freight["currency"],
        "freight_quote_amount": freight["quote_amount"],
        "customs_lines": _normalize_customs_lines_for_landed_cost(customs["lines"]),
        "fx_base_currency": fx["base_currency"],
        "fx_quote_currency": fx["quote_currency"],
        "fx_selected_rate_type": fx["selected_rate_type"],
        "fx_selected_rate": fx["selected_rate"],
        "local_currency": local_currency,
        "profit_margin_pct": profit_margin_pct,
        "quote_ids": {
            "freight_quote_id": freight["quote_id"],
            "customs_quote_id": customs["quote_id"],
            "fx_quote_id": fx["quote_id"],
        },
        "requested_at": requested_at,
    }


def _normalize_customs_lines_for_landed_cost(lines: Any) -> list[dict[str, Any]]:
    if not isinstance(lines, list) or not lines:
        raise QuoteLoopError("customs lines must be a non-empty list.")
    normalized: list[dict[str, Any]] = []
    required = (
        "line_id",
        "hs_code",
        "duty_rate_pct",
        "vat_rate_pct",
        "additional_rate_pct",
        "fixed_fee",
        "fixed_fee_currency",
    )
    for index, line in enumerate(lines):
        if not isinstance(line, Mapping):
            raise QuoteLoopError(f"customs line at index {index} must be a mapping.")
        normalized.append({field: line.get(field) for field in required})
    return normalized


def _extract_profit_margin_pct(user_profile: Mapping[str, Any]) -> float:
    for key in ("profit_margin_pct", "default_profit_margin_pct"):
        value = user_profile.get(key)
        if isinstance(value, (int, float)):
            margin = float(value)
            if 0 <= margin <= 100:
                return margin
            raise MissingUserProfileFieldError(
                f"{key} must be within [0, 100]. Got: {value!r}."
            )
    raise MissingUserProfileFieldError(
        "user_profile must include profit_margin_pct or default_profit_margin_pct."
    )


def _render_sourcing_failure_message(failures: Sequence[SourcingLegFailure]) -> str:
    if len(failures) == 1:
        return render_source_failure(failures[0])
    return render_source_failures(list(failures))


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")
