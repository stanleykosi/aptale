# Route Inference Prompt

Infer trade route fields from invoice data and conversational context.

## Goal

Determine:

- `origin_country` (ISO alpha-2)
- `destination_country` (ISO alpha-2)
- `origin_port`
- `destination_port`
- `local_currency` (ISO-4217)

## Data Sources

- Current invoice extraction payload
- Saved user profile (default lanes/currency)
- Recent chat context

## Rules

- Prefer explicit evidence from invoice content first.
- Use profile/chat only to fill missing route fields.
- Never fabricate route details.
- If uncertain, leave fields unresolved for an explicit route-required prompt.

## Output

Return strict JSON only:

```json
{
  "origin_country": "CN",
  "destination_country": "NG",
  "origin_port": "Guangzhou",
  "destination_port": "Lagos",
  "local_currency": "NGN"
}
```

No markdown or prose outside JSON.
