# France Freight (Origin: FR)

## Coverage
Use for freight leg when `origin_country=FR`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| CMA CGM | `https://www.cma-cgm.com` | `browser_navigate` | Ocean lane/schedule/rate workflows |
| GEODIS | `https://www.geodis.com` | `web_search` + `web_extract` | Forwarding and logistics references |
| Air France KLM Martinair Cargo | `https://www.afklcargo.com` | `browser_navigate` | Air cargo route references |
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean lane verification |

## Query Patterns
- `"France to {destination_country} freight quote"`
- `"Le Havre to {destination_port} shipping rate"`
- `"France air cargo {destination_country} {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If carrier/forwarder portals fail:
1. Use open-web discovery with official carrier pages first.
2. Cross-check rates across independent sources.
3. Keep complete citations.
4. Set `source_type=open_web` where allowed.
5. Fail fast on insufficient lane evidence.

## Fail-Fast Rules
- Do not use non-route-specific benchmark rates as final quote.
- Return strict JSON only.
