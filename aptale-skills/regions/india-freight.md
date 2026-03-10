# India Freight (Origin: IN)

## Coverage
Use for freight leg when `origin_country=IN`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean lane and quote workflows |
| CMA CGM | `https://www.cma-cgm.com` | `browser_navigate` | Ocean service and schedule references |
| CONCOR references | `https://www.concorindia.com` | `web_search` + `web_extract` | Intermodal/logistics context |
| Air India Cargo | `https://www.airindia.com` | `web_search` + `web_extract` | Air freight references |

## Query Patterns
- `"India to {destination_country} freight quote"`
- `"Nhava Sheva to {destination_port} shipping rate"`
- `"India air cargo {destination_country} {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If portal extraction fails:
1. Switch to open-web discovery with official carrier/forwarder pages.
2. Cross-check lane-specific quotes.
3. Keep complete citations.
4. Use `source_type=open_web` where permitted.
5. Fail fast when data is unverified.

## Fail-Fast Rules
- Do not infer rates from generalized market articles.
- Keep all output schema-bound and JSON-only.
