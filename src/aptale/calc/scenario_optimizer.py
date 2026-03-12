"""Deterministic scenario optimizer for fastest/cheapest/balanced plans."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Mapping


@dataclass(frozen=True)
class ScenarioOption:
    """One deterministic scenario option."""

    name: str
    total_landed_cost: float
    delta_vs_balanced: float
    margin_impact_pct: float
    eta_days: int | None
    assumptions: tuple[str, ...]
    source_flags: tuple[str, ...]

    def as_mapping(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "total_landed_cost": self.total_landed_cost,
            "delta_vs_balanced": self.delta_vs_balanced,
            "margin_impact_pct": self.margin_impact_pct,
            "eta_days": self.eta_days,
            "assumptions": list(self.assumptions),
            "source_flags": list(self.source_flags),
        }


def build_scenario_options(
    *,
    landed_cost_input: Mapping[str, Any],
    landed_cost_output: Mapping[str, Any],
    scenario_freight_quotes: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[dict[str, Any], ...]:
    """
    Build deterministic `Fastest`, `Cheapest`, `Balanced` options.

    `scenario_freight_quotes` can include optional `fastest` and `cheapest`
    payloads from extra freight sourcing attempts.
    """
    breakdown = dict(landed_cost_output.get("breakdown") or {})
    margin_pct = Decimal(str(landed_cost_output.get("profit_margin_pct") or 0))

    invoice_local = Decimal(str(breakdown.get("invoice_local") or 0))
    customs_local = Decimal(str(breakdown.get("customs_local") or 0))
    local_charges_local = Decimal(str(breakdown.get("local_charges_local") or 0))
    base_freight_local = Decimal(str(breakdown.get("freight_local") or 0))

    quote_map = dict(scenario_freight_quotes or {})
    cheapest_freight = _resolve_local_freight(
        fallback=base_freight_local * Decimal("0.92"),
        quote=quote_map.get("cheapest"),
        landed_cost_input=landed_cost_input,
    )
    fastest_freight = _resolve_local_freight(
        fallback=base_freight_local * Decimal("1.08"),
        quote=quote_map.get("fastest"),
        landed_cost_input=landed_cost_input,
    )

    balanced_total = _compute_total(
        invoice_local=invoice_local,
        freight_local=base_freight_local,
        customs_local=customs_local,
        local_charges_local=local_charges_local,
        margin_pct=margin_pct,
    )
    cheapest_total = _compute_total(
        invoice_local=invoice_local,
        freight_local=cheapest_freight,
        customs_local=customs_local,
        local_charges_local=local_charges_local,
        margin_pct=margin_pct,
    )
    fastest_total = _compute_total(
        invoice_local=invoice_local,
        freight_local=fastest_freight,
        customs_local=customs_local,
        local_charges_local=local_charges_local,
        margin_pct=margin_pct,
    )

    balanced = ScenarioOption(
        name="Balanced",
        total_landed_cost=float(_money(balanced_total)),
        delta_vs_balanced=0.0,
        margin_impact_pct=0.0,
        eta_days=_resolve_eta_days(quote_map.get("balanced"), default=28),
        assumptions=("Base quote retained as canonical balanced plan.",),
        source_flags=("modeled",),
    )
    cheapest = ScenarioOption(
        name="Cheapest",
        total_landed_cost=float(_money(cheapest_total)),
        delta_vs_balanced=float(_money(cheapest_total - balanced_total)),
        margin_impact_pct=float(_pct_delta(reference=balanced_total, current=cheapest_total)),
        eta_days=_resolve_eta_days(quote_map.get("cheapest"), default=35),
        assumptions=(
            "Freight reduced with economy lane assumptions when explicit quote unavailable.",
        ),
        source_flags=("modeled" if "cheapest" not in quote_map else "sourced",),
    )
    fastest = ScenarioOption(
        name="Fastest",
        total_landed_cost=float(_money(fastest_total)),
        delta_vs_balanced=float(_money(fastest_total - balanced_total)),
        margin_impact_pct=float(_pct_delta(reference=balanced_total, current=fastest_total)),
        eta_days=_resolve_eta_days(quote_map.get("fastest"), default=18),
        assumptions=(
            "Freight increased with express lane assumptions when explicit quote unavailable.",
        ),
        source_flags=("modeled" if "fastest" not in quote_map else "sourced",),
    )

    return (fastest.as_mapping(), cheapest.as_mapping(), balanced.as_mapping())


def scenario_spread_pct(scenarios: tuple[dict[str, Any], ...]) -> float:
    """Return % spread between cheapest and fastest total landed cost."""
    if not scenarios:
        return 0.0
    totals = [Decimal(str(item.get("total_landed_cost") or 0)) for item in scenarios]
    lo = min(totals)
    hi = max(totals)
    if lo <= 0:
        return 0.0
    return float(_pct_delta(reference=lo, current=hi))


def _resolve_local_freight(
    *,
    fallback: Decimal,
    quote: Mapping[str, Any] | None,
    landed_cost_input: Mapping[str, Any],
) -> Decimal:
    if not isinstance(quote, Mapping):
        return _money(fallback)

    amount = Decimal(str(quote.get("quote_amount") or 0))
    if amount <= 0:
        return _money(fallback)

    quote_currency = str(quote.get("currency") or "").upper()
    invoice_currency = str(landed_cost_input.get("invoice_currency") or "").upper()
    local_currency = str(landed_cost_input.get("local_currency") or "").upper()
    fx_rate = Decimal(str(landed_cost_input.get("fx_selected_rate") or 0))

    if quote_currency == local_currency:
        return _money(amount)
    if quote_currency == invoice_currency and fx_rate > 0:
        return _money(amount * fx_rate)
    return _money(fallback)


def _resolve_eta_days(quote: Mapping[str, Any] | None, *, default: int) -> int:
    if not isinstance(quote, Mapping):
        return default
    value = quote.get("transit_time_days")
    if isinstance(value, int) and value > 0:
        return value
    return default


def _compute_total(
    *,
    invoice_local: Decimal,
    freight_local: Decimal,
    customs_local: Decimal,
    local_charges_local: Decimal,
    margin_pct: Decimal,
) -> Decimal:
    subtotal = invoice_local + freight_local + customs_local + local_charges_local
    margin = subtotal * (margin_pct / Decimal("100"))
    return subtotal + margin


def _pct_delta(*, reference: Decimal, current: Decimal) -> Decimal:
    if reference == 0:
        return Decimal("0")
    return _money(((current - reference) / reference) * Decimal("100"))


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
