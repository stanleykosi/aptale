# Turkey to Nigeria Freight (TR->NG)

## Coverage
Use for freight leg when `origin_country=TR` and `destination_country=NG`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Turkish Cargo | `https://www.turkishcargo.com` | `browser_navigate` | Air cargo lane and schedule references |
| MSC | `https://www.msc.com` | `browser_navigate` | Ocean freight lane/schedule discovery |
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean freight route and indicative rate sources |
| Regional forwarders | discover by query | `web_search` + `web_extract` | Turkey-origin forwarding options to West Africa |

## Query Patterns
- `"freight quote Istanbul to Lagos {weight_kg}kg"`
- `"Turkey to Nigeria sea freight rate"`
- `"air cargo Turkey Nigeria quote"`
- `"Mersin to Lagos shipping price"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If direct portal extraction fails:
1. Use open-web discovery for Turkey->Nigeria forwarder/carrier references.
2. Prefer sources with explicit lane, mode, and validity context.
3. Provide complete citations and retrieval metadata.
4. Mark `source_type=open_web` where allowed.
5. Fail fast when lane-specific quote evidence is insufficient.

## Fail-Fast Rules
- If extracted value lacks lane context, do not use it.
- If quote currency is unclear, do not infer; return explicit failure.
- Keep final output JSON-only and schema-compliant.
