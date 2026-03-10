# Italy Freight (Origin: IT)

## Coverage
Use for freight leg when `origin_country=IT`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| MSC | `https://www.msc.com` | `browser_navigate` | Ocean lane schedule/rate references |
| Grimaldi Group | `https://www.grimaldi.napoli.it` | `web_search` + `web_extract`; `browser_navigate` as needed | RoRo/ocean service references |
| DHL Global Forwarding | `https://www.dhl.com` | `web_search` + `web_extract` | Forwarding references |
| ITA Airways cargo references | discover by query | `web_search` + `web_extract` | Air cargo checks |

## Query Patterns
- `"Italy to {destination_country} freight quote"`
- `"Genoa to {destination_port} shipping rate"`
- `"Italy air cargo quote {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If quote portals fail:
1. Switch to open-web discovery for lane-specific carrier/forwarder references.
2. Cross-check at least two authoritative sources.
3. Keep complete source metadata.
4. Set `source_type=open_web` when allowed.
5. Fail fast on unverifiable values.

## Fail-Fast Rules
- Do not return mixed-mode values without mode clarity.
- Return JSON object only.
