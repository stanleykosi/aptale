# Aptale JSON Contracts (Canonical)

This document defines the only supported wire formats between intake, clarification, delegated sourcing, landed-cost calculation, and alert scheduling.

These contracts are strict by design:

- Every payload must match one of the schemas in `schemas/`.
- Unknown fields are rejected (`additionalProperties: false`).
- Missing required fields are rejected.
- Numeric calculations must not run on partial or prose payloads.

## Schemas

- `schemas/invoice_extraction.schema.json`
- `schemas/invoice_correction.schema.json`
- `schemas/freight_quote.schema.json`
- `schemas/customs_quote.schema.json`
- `schemas/fx_quote.schema.json`
- `schemas/landed_cost_input.schema.json`
- `schemas/landed_cost_output.schema.json`
- `schemas/alert_rule.schema.json`

## Required Field Rules

- `invoice_extraction`: Requires route, currency, totals, confidence flags, and at least one line item.
- `invoice_correction`: Requires explicit confirmation status and correction list (must be empty only when status is `confirmed`).
- `freight_quote`, `customs_quote`, `fx_quote`: Require quote IDs, extraction linkage, normalized currency/rate fields, and source citations.
- `landed_cost_input`: Requires deterministic numeric inputs only (invoice amount, freight amount, customs rates/fees, selected FX rate, margin).
- `landed_cost_output`: Requires deterministic totals and a mandatory disclaimer string.
- `alert_rule`: Requires metric, comparison operator, threshold, cron schedule, and delivery target.

## Nullability Rules

Null is allowed only where uncertainty is expected and explicitly modeled:

- `invoice_extraction`: nullable route elements (`origin_port`, `destination_port`), optional identifiers (`invoice_number`), uncertain HS fields (`hs_code`, `hs_confidence`), and optional weight fields.
- `freight_quote`: nullable transit time, ports, and validity timestamp when source does not publish these.
- `customs_quote`: nullable VAT, fixed fees, fixed-fee currency, and legal reference when not present.
- `fx_quote`: nullable `parallel_rate` and `spread_pct` when a reliable parallel-market quote is unavailable.
- `landed_cost_input`: nullable invoice total weight only.
- `landed_cost_output`: nullable unit cost when a reliable unit divisor is unavailable.
- `alert_rule`: nullable currencies and route for non-FX/non-route-specific rules.

Any field not declared nullable must be populated with a valid non-null value.

## Source Attribution Rules

Source attribution is mandatory for every externally sourced quote payload:

- `freight_quote.sources` must include one or more source entries.
- `customs_quote.sources` must include one or more source entries.
- `fx_quote.sources` must include one or more source entries.

Each source entry must include:

- Source URL (`source_url`)
- Human-readable source label (`source_title`)
- Retrieval timestamp (`retrieved_at`)
- Retrieval method (`method`)

Accepted methods are constrained per schema to align with the sourcing path:

- Freight/customs: `browserbase`, `web_search`, `web_extract`
- FX: `web_search`, `web_extract`

If source attribution is missing or malformed, the payload is invalid and must be rejected.

## Hermes Alignment

These schemas enforce the Hermes subagent isolation and strict-output workflow:

- Parent agent passes complete context to `delegate_task`.
- Subagents return strict JSON payloads only.
- Parent calculation consumes schema-validated JSON only.

This preserves fail-fast behavior and prevents hidden fallbacks or inferred data paths.
