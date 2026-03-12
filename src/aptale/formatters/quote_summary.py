"""WhatsApp markdown formatter for landed-cost quote summaries."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Mapping

from aptale.contracts import validate_payload
from aptale.contracts.errors import ContractsError

from .whatsapp_markdown import bold, bullets, join_sections, section


class QuoteSummaryError(ValueError):
    """Raised when landed-cost output cannot be summarized safely."""


def render_quote_summary(
    landed_cost_output: Mapping[str, Any],
    *,
    quote_insights: Mapping[str, Any] | None = None,
) -> str:
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
            f"{bold('Local Charges (Local)')}: {_fmt_amount(breakdown['local_charges_local'], places=2)} {currency}",
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
    ]
    if quote_insights is not None:
        sections.extend(_render_quote_insight_sections(quote_insights))
    sections.append(section("Disclaimer", str(payload["disclaimer"])))
    return join_sections(sections)


def _fmt_amount(value: Any, *, places: int) -> str:
    quant = Decimal("1").scaleb(-places)
    amount = Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP)
    return format(amount, f",.{places}f")


def _fmt_cost_per_unit(value: Any, currency: str) -> str:
    if value is None:
        return "Not available"
    return f"{_fmt_amount(value, places=4)} {currency}"


def _render_quote_insight_sections(quote_insights: Mapping[str, Any]) -> list[str]:
    sections: list[str] = []

    confidence = quote_insights.get("confidence_report")
    if isinstance(confidence, Mapping):
        lines = []
        overall_score = confidence.get("overall_score")
        overall_band = confidence.get("overall_band")
        if isinstance(overall_score, (int, float)):
            lines.append(
                f"{bold('Overall')}: {overall_score:.2f} ({str(overall_band or 'unknown')})"
            )
        leg_scores = confidence.get("leg_scores")
        if isinstance(leg_scores, list):
            for leg in leg_scores:
                if not isinstance(leg, Mapping):
                    continue
                task = str(leg.get("task_type") or "unknown")
                score = leg.get("score")
                band = str(leg.get("band") or "unknown")
                if isinstance(score, (int, float)):
                    lines.append(f"{task}: {score:.2f} ({band})")
        reasons = confidence.get("reasons")
        if isinstance(reasons, list):
            for reason in reasons:
                if isinstance(reason, str) and reason.strip():
                    lines.append(reason.strip())
        if lines:
            sections.append(section("Confidence", bullets(lines)))

    scenarios = quote_insights.get("scenario_options")
    if isinstance(scenarios, list) and scenarios:
        lines = []
        for option in scenarios:
            if not isinstance(option, Mapping):
                continue
            name = str(option.get("name") or "Scenario")
            total = option.get("total_landed_cost")
            delta = option.get("delta_vs_balanced")
            eta = option.get("eta_days")
            if isinstance(total, (int, float)):
                summary = f"{name}: {total:,.2f}"
            else:
                summary = f"{name}: N/A"
            if isinstance(delta, (int, float)):
                summary += f" (delta {delta:+,.2f})"
            if isinstance(eta, int):
                summary += f", ETA {eta}d"
            lines.append(summary)
        if lines:
            sections.append(section("Scenario Optimizer", bullets(lines)))

    advisory = quote_insights.get("advisory_failures")
    if isinstance(advisory, list):
        advisory_lines = [str(item).strip() for item in advisory if str(item).strip()]
        if advisory_lines:
            sections.append(section("Advisory Warnings", bullets(advisory_lines)))

    return sections
