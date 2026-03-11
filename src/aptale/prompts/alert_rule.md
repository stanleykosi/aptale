# Alert Rule Parsing Prompt

Convert a user's natural-language alert request into Aptale's canonical alert-rule output.

## Required Extractions

- monitored dimension (`metric`)
- comparison operator (`condition`)
- numeric threshold (`threshold`)
- schedule (`schedule_cron`)
- timezone (IANA)
- delivery target (`deliver`)

## Canonical Constraints

1. Return only deterministic fields required for `alert_rule` schema v1.0.
2. Use strict comparison operators: `lt`, `lte`, `gt`, `gte`, `eq`.
3. `schedule_cron` must be a 5-field cron expression.
4. `deliver` must be one of: `origin`, `whatsapp`, `telegram`, `discord`, `slack`, `local`.
5. For FX metrics, include both `base_currency` and `quote_currency`.
6. Fail fast when threshold, timezone, operator, or required FX currencies are missing.

## Metric Mapping Guidance

- Parallel / black-market FX language -> `fx_parallel_rate`
- Official bank FX language -> `fx_official_rate`
- Freight / shipping quote language -> `freight_quote_amount`
- Landed cost language -> `landed_cost_total`

## Output Shape

Produce a structured object equivalent to:

```json
{
  "timezone": "Africa/Lagos",
  "alert_rule": {
    "schema_version": "1.0",
    "alert_id": "...",
    "user_id": "...",
    "active": true,
    "metric": "fx_parallel_rate",
    "condition": "lt",
    "threshold": 1400,
    "base_currency": "USD",
    "quote_currency": "NGN",
    "route": null,
    "schedule_cron": "0 8 * * *",
    "deliver": "origin",
    "message_template": "...",
    "created_at": "2026-03-11T00:00:00Z"
  }
}
```
