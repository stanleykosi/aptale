# Germany Freight (Origin: DE)

## Coverage
Use for freight leg when `origin_country=DE`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Hapag-Lloyd | `https://www.hapag-lloyd.com` | `browser_navigate` | Ocean lane/schedule references |
| DB Schenker | `https://www.dbschenker.com` | `web_search` + `web_extract`; `browser_navigate` as needed | Multimodal forwarding references |
| Lufthansa Cargo | `https://www.lufthansa-cargo.com` | `browser_navigate` | Air cargo route references |
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean lane/rate references |

## Query Patterns
- `"Germany to {destination_country} freight quote"`
- `"Hamburg to {destination_port} shipping rate"`
- `"Germany air cargo quote {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If interactive flows fail:
1. Switch to open-web discovery with official carrier/forwarder sources.
2. Cross-check lane-specific values before returning output.
3. Keep complete citation metadata.
4. Set `source_type=open_web` where schema allows.
5. Fail fast if values cannot be validated.

## Fail-Fast Rules
- Do not return uncited route values.
- Return one JSON object only.
