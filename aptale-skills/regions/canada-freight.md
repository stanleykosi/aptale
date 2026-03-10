# Canada Freight (Origin: CA)

## Coverage
Use for freight leg when `origin_country=CA`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean route and quote workflows |
| MSC | `https://www.msc.com` | `browser_navigate` | Ocean lane/service references |
| Air Canada Cargo | `https://www.aircanada.com/cargo` | `browser_navigate` | Air cargo lane references |
| CN Logistics references | discover by query | `web_search` + `web_extract` | Intermodal/freight support checks |

## Query Patterns
- `"Canada to {destination_country} freight quote"`
- `"Toronto to {destination_port} shipping rate"`
- `"Canada air cargo quote {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If portals fail:
1. Use open-web discovery for lane-specific carrier/forwarder sources.
2. Cross-check at least two authoritative references.
3. Include full citation metadata.
4. Set `source_type=open_web` where allowed.
5. Fail fast if quote evidence is insufficient.

## Fail-Fast Rules
- Do not return mixed-route pricing.
- Do not return blank amounts or breakdowns.
- Return JSON only.
