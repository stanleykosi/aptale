# Russia Freight (Origin: RU)

## Coverage
Use for freight leg when `origin_country=RU`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| FESCO | `https://www.fesco.com` | `browser_navigate` | Ocean/intermodal route references |
| Aeroflot Cargo | `https://cargo.aeroflot.ru` | `browser_navigate` | Air cargo route references |
| Rail/intermodal operators | discover by query | `web_search` + `web_extract` | Supplemental route/rate checks |

## Query Patterns
- `"Russia to {destination_country} freight quote {weight_kg}kg"`
- `"RU sea freight {destination_port}"`
- `"Russia air cargo rate to {destination_country}"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If known portals are blocked or unavailable:
1. Use open-web discovery with carrier/operator domain filters.
2. Cross-check route and amount values before output.
3. Preserve complete citation metadata.
4. Set `source_type=open_web` where schema allows.
5. Fail fast if route-specific values are not verifiable.

## Fail-Fast Rules
- Do not infer prices from non-lane-specific pages.
- If quote currency is unclear, return explicit failure.
- Return strict JSON only.
