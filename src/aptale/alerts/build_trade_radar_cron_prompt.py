"""Build Hermes cron prompt for HS-lane trade radar with daily delta reporting."""

from __future__ import annotations

import json
from typing import Any, Mapping

from aptale.contracts import normalize_and_validate_payload
from aptale.contracts.errors import ContractsError
from aptale.memory.timezone import normalize_timezone


class TradeRadarCronPromptError(ValueError):
    """Raised when trade radar cron prompt inputs are invalid."""


def build_trade_radar_cron_prompt(
    trade_radar_rule: Mapping[str, Any],
    *,
    sourcing_context: Mapping[str, Any],
) -> str:
    if not isinstance(sourcing_context, Mapping) or not dict(sourcing_context):
        raise TradeRadarCronPromptError("sourcing_context must be a non-empty mapping.")

    try:
        rule = normalize_and_validate_payload("trade_radar_rule", trade_radar_rule)
    except ContractsError as exc:
        raise TradeRadarCronPromptError("trade_radar_rule payload failed schema validation.") from exc

    timezone = normalize_timezone(rule["timezone"])
    context_json = json.dumps(dict(sourcing_context), indent=2, sort_keys=True, ensure_ascii=True)

    return (
        "You are running a Hermes cron job for Aptale Trade Radar.\n\n"
        "*Fresh Session Constraint*\n"
        "- This cron run starts with zero memory of prior chat.\n"
        "- Use only this prompt context.\n"
        "- Do not ask follow-up questions.\n\n"
        "*Trade Radar Rule*\n"
        f"- Alert ID: {rule['alert_id']}\n"
        f"- HS code: {rule['hs_code']}\n"
        f"- Route: {rule['origin_country']} -> {rule['destination_country']}\n"
        f"- Schedule: {rule['schedule_cron']}\n"
        f"- Timezone: {timezone}\n"
        "- Deliver: origin (same WhatsApp chat)\n\n"
        "*Execution Steps*\n"
        "1. Run sourcing for freight/customs/fx/local charges and lane risk notes.\n"
        "2. Compare current snapshot against most recent prior snapshot in available context.\n"
        "3. Produce a daily delta update that always sends, including no-change summary when unchanged.\n"
        "4. Include: what changed, confidence shift, and source URLs.\n\n"
        "*Sourcing Context (Authoritative JSON)*\n"
        "```json\n"
        f"{context_json}\n"
        "```\n\n"
        "*Output Contract*\n"
        "Return concise WhatsApp markdown with sections:\n"
        "- Radar Update\n"
        "- What Changed Today\n"
        "- Confidence Shift\n"
        "- Sources\n"
        "Always include a line even when unchanged: 'No material changes since last run.'"
    )
