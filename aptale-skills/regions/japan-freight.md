# Japan Freight (Origin: JP)

## Coverage
Use for freight leg when `origin_country=JP`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| ONE (Ocean Network Express) | `https://www.one-line.com` | `browser_navigate` | Ocean lane schedules and quote context |
| NYK Line | `https://www.nyk.com` | `web_search` + `web_extract`; `browser_navigate` as needed | Ocean shipping references |
| Nippon Express | `https://www.nipponexpress.com` | `web_search` + `web_extract` | Forwarding and multimodal references |
| ANA Cargo | `https://www.anacargo.jp` | `browser_navigate` | Air cargo route references |

## Query Patterns
- `"Japan to {destination_country} freight quote"`
- `"Tokyo to {destination_port} shipping rate"`
- `"Japan air cargo {destination_country} {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If primary portals fail:
1. Switch to open-web discovery with carrier/forwarder official sources.
2. Cross-check rates with at least two independent sources.
3. Keep full citation metadata.
4. Use `source_type=open_web` where allowed.
5. Fail fast when rate evidence is weak.

## Fail-Fast Rules
- Do not output freight values without route match.
- Do not return prose wrappers.
- Return one schema-compliant JSON object.
