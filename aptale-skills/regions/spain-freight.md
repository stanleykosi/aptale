# Spain Freight (Origin: ES)

## Coverage
Use for freight leg when `origin_country=ES`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean lane/rate references |
| CMA CGM | `https://www.cma-cgm.com` | `browser_navigate` | Ocean route/schedule references |
| IAG Cargo | `https://www.iagcargo.com` | `browser_navigate` | Air cargo route references |
| Forwarder listings | discover via query | `web_search` + `web_extract` | Supplemental route quote checks |

## Query Patterns
- `"Spain to {destination_country} freight quote"`
- `"Valencia to {destination_port} shipping rate"`
- `"Spain air cargo {destination_country} {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If direct portals fail:
1. Use open-web discovery with route-scoped queries.
2. Cross-check values from independent sources.
3. Preserve complete citations.
4. Set `source_type=open_web` where schema allows.
5. Fail fast when evidence is weak.

## Fail-Fast Rules
- Do not return quote values without destination lane match.
- Return strict JSON only.
