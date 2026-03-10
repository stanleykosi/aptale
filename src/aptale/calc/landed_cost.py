"""Deterministic landed-cost calculator for canonical Aptale contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import re
from typing import Any, Callable, Mapping

from aptale.contracts import validate_landed_cost_input, validate_payload
from aptale.contracts.errors import ContractsError

from .models import (
    LandedCostBreakdownModel,
    LandedCostInputModel,
    LandedCostOutputModel,
)

DISCLAIMER_TEXT = (
    "Estimates only, subject to final customs assessment and market fluctuations."
)


class LandedCostComputationError(RuntimeError):
    """Raised when deterministic landed-cost computation cannot proceed safely."""


def calculate_landed_cost(
    payload: Mapping[str, Any],
    *,
    now_fn: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    """
    Compute landed-cost output contract from validated landed-cost input payload.

    This path is deterministic and fail-fast: malformed inputs and unsupported
    currency combinations raise explicit errors.
    """
    if not isinstance(payload, Mapping):
        raise LandedCostComputationError("payload must be a mapping.")

    try:
        validated_input = validate_landed_cost_input(payload)
    except ContractsError as exc:
        raise LandedCostComputationError("Invalid landed_cost_input payload.") from exc

    request = LandedCostInputModel.from_mapping(validated_input)
    now = now_fn or (lambda: datetime.now(timezone.utc))
    output = _compute_landed_cost(request, computed_at=now())
    output_payload = output.as_mapping()

    try:
        return validate_payload("landed_cost_output", output_payload)
    except ContractsError as exc:
        raise LandedCostComputationError(
            "Computed landed-cost output failed schema validation."
        ) from exc


def _compute_landed_cost(
    request: LandedCostInputModel,
    *,
    computed_at: datetime,
) -> LandedCostOutputModel:
    fx_rate = Decimal(str(request.fx_selected_rate))
    invoice_total = Decimal(str(request.invoice_total))
    freight_quote_amount = Decimal(str(request.freight_quote_amount))
    margin_pct = Decimal(str(request.profit_margin_pct))

    invoice_local = _money(invoice_total * fx_rate)
    freight_local = _money(freight_quote_amount * fx_rate)
    customs_local = _compute_customs_local(request=request, invoice_total=invoice_total, fx_rate=fx_rate)

    subtotal = _money(invoice_local + freight_local + customs_local)
    profit_amount = _money(subtotal * (margin_pct / Decimal("100")))
    total_landed_cost = _money(subtotal + profit_amount)
    cost_per_unit = _cost_per_unit(
        total=total_landed_cost,
        weight_kg=request.invoice_total_weight_kg,
    )

    output = LandedCostOutputModel(
        calculation_id=_build_calculation_id(request.extraction_id, computed_at),
        extraction_id=request.extraction_id,
        local_currency=request.local_currency,
        subtotal_before_margin=float(subtotal),
        profit_margin_pct=float(margin_pct),
        profit_amount=float(profit_amount),
        total_landed_cost=float(total_landed_cost),
        cost_per_unit=(None if cost_per_unit is None else float(cost_per_unit)),
        breakdown=LandedCostBreakdownModel(
            invoice_local=float(invoice_local),
            freight_local=float(freight_local),
            customs_local=float(customs_local),
            margin_local=float(profit_amount),
        ),
        source_quote_ids=tuple(request.quote_ids.as_list()),
        disclaimer=DISCLAIMER_TEXT,
        computed_at=_utc_iso(computed_at),
    )
    return output


def _compute_customs_local(
    *,
    request: LandedCostInputModel,
    invoice_total: Decimal,
    fx_rate: Decimal,
) -> Decimal:
    line_count = Decimal(str(len(request.customs_lines)))
    total_rate_pct = sum((line.total_rate_pct_decimal() for line in request.customs_lines), Decimal("0"))
    avg_rate_pct = total_rate_pct / line_count

    customs_from_rates_local = invoice_total * (avg_rate_pct / Decimal("100")) * fx_rate
    fixed_fees_local = Decimal("0")

    for line in request.customs_lines:
        if line.fixed_fee is None:
            continue

        fixed_fee = Decimal(str(line.fixed_fee))
        fixed_fee_currency = line.fixed_fee_currency
        if fixed_fee_currency == request.invoice_currency:
            fixed_fees_local += fixed_fee * fx_rate
        elif fixed_fee_currency == request.local_currency:
            fixed_fees_local += fixed_fee
        else:
            raise LandedCostComputationError(
                "Unsupported fixed_fee_currency in customs_lines: "
                f"{fixed_fee_currency!r}. Expected {request.invoice_currency!r} "
                f"or {request.local_currency!r}."
            )

    return _money(customs_from_rates_local + fixed_fees_local)


def _cost_per_unit(*, total: Decimal, weight_kg: float | None) -> Decimal | None:
    if weight_kg is None or weight_kg <= 0:
        return None
    weight = Decimal(str(weight_kg))
    return _quantize(total / weight, places=4)


def _money(value: Decimal) -> Decimal:
    return _quantize(value, places=2)


def _quantize(value: Decimal, *, places: int) -> Decimal:
    return value.quantize(Decimal("1").scaleb(-places), rounding=ROUND_HALF_UP)


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def _build_calculation_id(extraction_id: str, computed_at: datetime) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", extraction_id).strip("_")
    timestamp = computed_at.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
    if not slug:
        slug = "unknown"
    return f"lc_{slug}_{timestamp}"
