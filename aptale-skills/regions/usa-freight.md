# United States Freight (Origin: US)

## Coverage
Use for freight leg when `origin_country=US`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean freight route and rate workflows |
| CMA CGM | `https://www.cma-cgm.com` | `browser_navigate` | Ocean lane service/rate references |
| UPS Supply Chain | `https://www.ups.com/us/en/supplychain` | `web_search` + `web_extract`; `browser_navigate` as needed | Logistics and forwarding references |
| FedEx Logistics | `https://www.fedex.com/en-us/logistics.html` | `web_search` + `web_extract` | Air/ocean forwarding references |

## Query Patterns
- `"freight quote {origin_port} to {destination_port} {weight_kg}kg"`
- `"US to {destination_country} sea freight rate"`
- `"US air cargo {destination_country} quote"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If interactive portals fail:
1. Switch to open-web discovery for lane-specific carrier/forwarder references.
2. Cross-check at least two authoritative sources.
3. Keep complete `sources[]` metadata.
4. Set `source_type=open_web` where allowed.
5. Fail fast when lane quote evidence is insufficient.

## Fail-Fast Rules
- Do not return empty `charge_breakdown`.
- Do not blend non-matching routes.
- Return JSON object only.
