# Netherlands Freight (Origin: NL)

## Coverage
Use for freight leg when `origin_country=NL`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Port of Rotterdam | `https://www.portofrotterdam.com` | `web_search` + `web_extract`; `browser_navigate` as needed | Port/lane context and schedules |
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean lane/rate references |
| MSC | `https://www.msc.com` | `browser_navigate` | Ocean service references |
| KLM Cargo | `https://www.klmcargo.com` | `browser_navigate` | Air cargo route references |

## Query Patterns
- `"Netherlands to {destination_country} freight quote"`
- `"Rotterdam to {destination_port} shipping rate"`
- `"Netherlands air cargo {destination_country} {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If portal workflows fail:
1. Switch to open-web discovery with carrier/port sources.
2. Cross-check lane-specific values.
3. Keep complete citation metadata.
4. Set `source_type=open_web` where allowed.
5. Fail fast on unverifiable route values.

## Fail-Fast Rules
- Do not return non-route-specific benchmark values.
- Return strict JSON only.
