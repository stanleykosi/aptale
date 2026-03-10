"""Typed models for deterministic landed-cost calculation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping


@dataclass(frozen=True)
class CustomsLineModel:
    """Normalized customs-line inputs for landed-cost calculation."""

    line_id: str
    hs_code: str
    duty_rate_pct: float
    vat_rate_pct: float | None
    additional_rate_pct: float
    fixed_fee: float | None
    fixed_fee_currency: str | None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> CustomsLineModel:
        return cls(
            line_id=str(data["line_id"]),
            hs_code=str(data["hs_code"]),
            duty_rate_pct=float(data["duty_rate_pct"]),
            vat_rate_pct=(None if data["vat_rate_pct"] is None else float(data["vat_rate_pct"])),
            additional_rate_pct=float(data["additional_rate_pct"]),
            fixed_fee=(None if data["fixed_fee"] is None else float(data["fixed_fee"])),
            fixed_fee_currency=(
                None if data["fixed_fee_currency"] is None else str(data["fixed_fee_currency"])
            ),
        )

    def total_rate_pct_decimal(self) -> Decimal:
        vat = Decimal("0") if self.vat_rate_pct is None else Decimal(str(self.vat_rate_pct))
        return (
            Decimal(str(self.duty_rate_pct))
            + vat
            + Decimal(str(self.additional_rate_pct))
        )


@dataclass(frozen=True)
class QuoteIDsModel:
    """Quote identifiers consumed by the landed-cost calculation."""

    freight_quote_id: str
    customs_quote_id: str
    fx_quote_id: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> QuoteIDsModel:
        return cls(
            freight_quote_id=str(data["freight_quote_id"]),
            customs_quote_id=str(data["customs_quote_id"]),
            fx_quote_id=str(data["fx_quote_id"]),
        )

    def as_list(self) -> list[str]:
        return [self.freight_quote_id, self.customs_quote_id, self.fx_quote_id]


@dataclass(frozen=True)
class LandedCostInputModel:
    """Canonical landed-cost inputs after contract validation."""

    extraction_id: str
    invoice_currency: str
    invoice_total: float
    invoice_total_weight_kg: float | None
    freight_currency: str
    freight_quote_amount: float
    customs_lines: tuple[CustomsLineModel, ...]
    fx_base_currency: str
    fx_quote_currency: str
    fx_selected_rate_type: str
    fx_selected_rate: float
    local_currency: str
    profit_margin_pct: float
    quote_ids: QuoteIDsModel
    requested_at: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> LandedCostInputModel:
        return cls(
            extraction_id=str(data["extraction_id"]),
            invoice_currency=str(data["invoice_currency"]),
            invoice_total=float(data["invoice_total"]),
            invoice_total_weight_kg=(
                None
                if data["invoice_total_weight_kg"] is None
                else float(data["invoice_total_weight_kg"])
            ),
            freight_currency=str(data["freight_currency"]),
            freight_quote_amount=float(data["freight_quote_amount"]),
            customs_lines=tuple(
                CustomsLineModel.from_mapping(line)
                for line in data["customs_lines"]
            ),
            fx_base_currency=str(data["fx_base_currency"]),
            fx_quote_currency=str(data["fx_quote_currency"]),
            fx_selected_rate_type=str(data["fx_selected_rate_type"]),
            fx_selected_rate=float(data["fx_selected_rate"]),
            local_currency=str(data["local_currency"]),
            profit_margin_pct=float(data["profit_margin_pct"]),
            quote_ids=QuoteIDsModel.from_mapping(data["quote_ids"]),
            requested_at=str(data["requested_at"]),
        )


@dataclass(frozen=True)
class LandedCostBreakdownModel:
    """Breakdown fields required by landed_cost_output."""

    invoice_local: float
    freight_local: float
    customs_local: float
    margin_local: float

    def as_mapping(self) -> dict[str, float]:
        return {
            "invoice_local": self.invoice_local,
            "freight_local": self.freight_local,
            "customs_local": self.customs_local,
            "margin_local": self.margin_local,
        }


@dataclass(frozen=True)
class LandedCostOutputModel:
    """Deterministic landed-cost output payload."""

    calculation_id: str
    extraction_id: str
    local_currency: str
    subtotal_before_margin: float
    profit_margin_pct: float
    profit_amount: float
    total_landed_cost: float
    cost_per_unit: float | None
    breakdown: LandedCostBreakdownModel
    source_quote_ids: tuple[str, ...]
    disclaimer: str
    computed_at: str

    def as_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "calculation_id": self.calculation_id,
            "extraction_id": self.extraction_id,
            "local_currency": self.local_currency,
            "subtotal_before_margin": self.subtotal_before_margin,
            "profit_margin_pct": self.profit_margin_pct,
            "profit_amount": self.profit_amount,
            "total_landed_cost": self.total_landed_cost,
            "cost_per_unit": self.cost_per_unit,
            "breakdown": self.breakdown.as_mapping(),
            "source_quote_ids": list(self.source_quote_ids),
            "disclaimer": self.disclaimer,
            "computed_at": self.computed_at,
        }
