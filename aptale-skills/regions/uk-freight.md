# United Kingdom Freight (Origin: GB)

## Coverage
Use for freight leg when `origin_country=GB`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean freight route/rate workflows |
| CMA CGM | `https://www.cma-cgm.com` | `browser_navigate` | Ocean lane/service references |
| Kuehne+Nagel | `https://home.kuehne-nagel.com` | `web_search` + `web_extract` | Forwarding quote references |
| IAG Cargo | `https://www.iagcargo.com` | `browser_navigate` | Air cargo references |

## Query Patterns
- `"UK to {destination_country} freight quote"`
- `"Felixstowe to {destination_port} shipping rate"`
- `"UK air cargo quote {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If portal paths fail:
1. Use open-web discovery for lane-specific references.
2. Cross-check source values before output.
3. Include complete citation metadata.
4. Set `source_type=open_web` where allowed.
5. Fail fast on ambiguous route pricing.

## Fail-Fast Rules
- Do not return route-agnostic averages as final quote.
- Return strict JSON only.
