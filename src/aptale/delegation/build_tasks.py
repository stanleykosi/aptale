"""Parent-side task planner for three-leg delegated sourcing."""

from __future__ import annotations

from typing import Any, Mapping

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError
from aptale.contracts.normalize import normalize_currency

from .context_builder import DelegationContextError, build_subagent_context


class DelegationBuildError(RuntimeError):
    """Raised when sourcing delegation tasks cannot be built safely."""


def build_sourcing_tasks(
    *,
    invoice_extraction: Mapping[str, Any],
    local_currency: str,
    user_profile: Mapping[str, Any],
    extraction_status: str,
    route_status: str,
    subagent_model: str | None = None,
    source_strategy_by_task: Mapping[str, str] | None = None,
) -> list[dict[str, Any]]:
    """
    Build canonical sourcing tasks: freight, customs, fx, local charges, risk notes.

    This function is fail-fast by design: it only runs after extraction is
    validated and route inference is resolved.
    """
    if extraction_status != "validated":
        raise DelegationBuildError(
            "Extraction must be validated before delegation tasks can be built."
        )
    if route_status != "route_resolved":
        raise DelegationBuildError("Route must be resolved before delegation.")

    try:
        extraction = normalize_and_validate_payload("invoice_extraction", invoice_extraction)
    except ContractsError as exc:
        raise DelegationBuildError("invoice_extraction payload is invalid.") from exc

    try:
        local = normalize_currency(local_currency)
    except Exception as exc:
        raise DelegationBuildError("local_currency is invalid.") from exc

    route = _route_summary(extraction)
    total_weight = extraction.get("total_weight_kg")
    weight_label = "unknown weight" if total_weight is None else f"{total_weight:.2f} kg"

    tasks: list[dict[str, Any]] = []
    strategy_map = _normalize_source_strategy_map(source_strategy_by_task)

    task_specs = (
        (
            "freight",
            "Find current freight rates for this route and shipment profile.",
            ["browser", "web"],
            (
                f"Find freight rates from {route} for {weight_label}. "
                "Return strict JSON only matching freight_quote schema."
            ),
        ),
        (
            "customs",
            "Find current import duty/tax rates by HS code for destination.",
            ["browser", "web"],
            (
                f"Find customs duty rates for destination {extraction['destination_country']} "
                "using provided HS codes. Return strict JSON only matching customs_quote schema."
            ),
        ),
        (
            "fx",
            "Find official and parallel FX rates for landed-cost conversion.",
            ["web"],
            (
                f"Find FX rates to convert {extraction['currency']} into {local}. "
                "Include official and parallel rates when available. Return strict JSON only "
                "matching fx_quote schema."
            ),
        ),
        (
            "local_charges",
            "Find destination local charges for handling/clearance/terminal operations.",
            ["browser", "web"],
            (
                f"Find local charges for destination {extraction['destination_country']} on route {route}. "
                f"Return strict JSON only matching local_charge_quote schema in {local}."
            ),
        ),
        (
            "risk_notes",
            "Find current disruption and compliance risks for this lane.",
            ["web"],
            (
                f"Find lane risk notes for {route}. Include operational/compliance disruptions. "
                "Return strict JSON only matching risk_note_quote schema."
            ),
        ),
    )

    for task_type, title, toolsets, goal in task_specs:
        try:
            context = build_subagent_context(
                task_type=task_type,
                invoice_extraction=extraction,
                local_currency=local,
                user_profile=user_profile,
                route_status=route_status,
            )
        except DelegationContextError as exc:
            raise DelegationBuildError(
                f"Failed to build context for {task_type} task."
            ) from exc

        task: dict[str, Any] = {
            "task_type": task_type,
            "title": title,
            "goal": goal,
            "context": context,
            "toolsets": toolsets,
        }
        strategy = strategy_map.get(task_type)
        if strategy is not None:
            task["source_strategy"] = strategy
        if subagent_model:
            task["model"] = subagent_model
        tasks.append(task)

    if len(tasks) != 5:
        raise DelegationBuildError("Delegation planner must produce exactly five tasks.")
    return tasks


def _route_summary(extraction: Mapping[str, Any]) -> str:
    origin_country = extraction.get("origin_country") or "??"
    destination_country = extraction.get("destination_country") or "??"
    origin_port = extraction.get("origin_port") or "unknown port"
    destination_port = extraction.get("destination_port") or "unknown port"
    return f"{origin_country} ({origin_port}) to {destination_country} ({destination_port})"


def _normalize_source_strategy_map(
    source_strategy_by_task: Mapping[str, str] | None,
) -> dict[str, str]:
    if source_strategy_by_task is None:
        return {}
    if not isinstance(source_strategy_by_task, Mapping):
        raise DelegationBuildError("source_strategy_by_task must be a mapping when provided.")

    allowed_tasks = {"freight", "customs", "fx", "local_charges", "risk_notes"}
    normalized: dict[str, str] = {}
    for task_type, strategy in source_strategy_by_task.items():
        task = str(task_type).strip()
        if task not in allowed_tasks:
            raise DelegationBuildError(f"Unsupported source strategy task_type: {task_type!r}.")
        value = str(strategy).strip().lower()
        if value not in {"default", "open_web_only"}:
            raise DelegationBuildError(
                f"Unsupported source strategy {strategy!r} for task {task!r}. "
                "Expected 'default' or 'open_web_only'."
            )
        normalized[task] = value
    return normalized
