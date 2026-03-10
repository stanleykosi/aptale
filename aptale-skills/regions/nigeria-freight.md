# Nigeria Freight (Origin: NG)

## Coverage
Use for freight leg when `origin_country=NG`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean lane/rate references |
| CMA CGM | `https://www.cma-cgm.com` | `browser_navigate` | Ocean route/schedule references |
| Freight forwarding listings | discover via query | `web_search` + `web_extract` | Forwarder lane quote checks |
| Airline cargo portals | discover by route | `web_search` + `web_extract`; `browser_navigate` as needed | Air cargo references |

## Query Patterns
- `"Nigeria to {destination_country} freight quote"`
- `"Lagos to {destination_port} shipping rate"`
- `"Nigeria air cargo {destination_country} {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If known portals fail:
1. Switch to open-web discovery for route-specific carriers/forwarders.
2. Cross-check quote values across independent sources.
3. Include complete source citations.
4. Set `source_type=open_web` where allowed.
5. Fail fast if no verifiable lane quote is available.

## Fail-Fast Rules
- Do not output rates without clear origin/destination match.
- Do not return prose wrappers.
- Return one schema-compliant JSON object only.
