"""WhatsApp markdown formatter for landed-cost quote summaries."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Mapping

from aptale.contracts import validate_payload
from aptale.contracts.errors import ContractsError

from .whatsapp_markdown import bold, bullets, join_sections, section


class QuoteSummaryError(ValueError):
    """Raised when landed-cost output cannot be summarized safely."""


def render_quote_summary(landed_cost_output: Mapping[str, Any]) -> str:
    """Render a concise WhatsApp markdown quote summary with disclaimer."""
    if not isinstance(landed_cost_output, Mapping):
        raise QuoteSummaryError("landed_cost_output must be a mapping.")

    try:
        payload = validate_payload("landed_cost_output", landed_cost_output)
    except ContractsError as exc:
        raise QuoteSummaryError("Invalid landed_cost_output payload.") from exc

    currency = str(payload["local_currency"])
    breakdown = payload["breakdown"]
    cost_per_unit = payload["cost_per_unit"]
    source_ids = ", ".join(str(x) for x in payload["source_quote_ids"])

    headline = bullets(
        [
            f"{bold('Calculation ID')}: {payload['calculation_id']}",
            f"{bold('Extraction ID')}: {payload['extraction_id']}",
            f"{bold('Computed At (UTC)')}: {payload['computed_at']}",
            f"{bold('Local Currency')}: {currency}",
            f"{bold('Total Landed Cost')}: {_fmt_amount(payload['total_landed_cost'], places=2)} {currency}",
            f"{bold('Cost Per Unit')}: {_fmt_cost_per_unit(cost_per_unit, currency)}",
        ]
    )

    totals = bullets(
        [
            f"{bold('Invoice (Local)')}: {_fmt_amount(breakdown['invoice_local'], places=2)} {currency}",
            f"{bold('Freight (Local)')}: {_fmt_amount(breakdown['freight_local'], places=2)} {currency}",
            f"{bold('Customs (Local)')}: {_fmt_amount(breakdown['customs_local'], places=2)} {currency}",
            f"{bold('Margin (Local)')}: {_fmt_amount(breakdown['margin_local'], places=2)} {currency}",
            f"{bold('Subtotal Before Margin')}: {_fmt_amount(payload['subtotal_before_margin'], places=2)} {currency}",
            f"{bold('Profit Margin')}: {_fmt_amount(payload['profit_margin_pct'], places=2)}%",
            f"{bold('Profit Amount')}: {_fmt_amount(payload['profit_amount'], places=2)} {currency}",
            f"{bold('Source Quote IDs')}: {source_ids}",
        ]
    )

    sections = [
        section("Quote Summary", headline),
        section("Cost Breakdown", totals),
        section("Disclaimer", str(payload["disclaimer"])),
    ]
    return join_sections(sections)


def _fmt_amount(value: Any, *, places: int) -> str:
    quant = Decimal("1").scaleb(-places)
    amount = Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP)
    return format(amount, f",.{places}f")


def _fmt_cost_per_unit(value: Any, currency: str) -> str:
    if value is None:
        return "Not available"
    return f"{_fmt_amount(value, places=4)} {currency}"
