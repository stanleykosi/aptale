# Brazil Freight (Origin: BR)

## Coverage
Use for freight leg when `origin_country=BR`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| MSC | `https://www.msc.com` | `browser_navigate` | Ocean lane schedules/rates |
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean lane/rate references |
| LATAM Cargo | `https://www.latamcargo.com` | `browser_navigate` | Air cargo route references |
| Port/logistics references | discover via query | `web_search` + `web_extract` | Supplemental lane verification |

## Query Patterns
- `"Brazil to {destination_country} freight quote"`
- `"Santos to {destination_port} shipping rate"`
- `"Brazil air cargo {destination_country} {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If quote portals fail:
1. Use open-web discovery for lane-specific carrier/forwarder sources.
2. Cross-check route and price values.
3. Keep complete source citations.
4. Set `source_type=open_web` where allowed.
5. Fail fast on weak evidence.

## Fail-Fast Rules
- Do not return non-route-specific averages as final quote.
- Return strict JSON only.
