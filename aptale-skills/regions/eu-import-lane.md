# EU to Nigeria Import Lane (EU->NG)

## Coverage
Use for routes with EU origin and Nigeria destination.
Default reference lane: `NL (Rotterdam) -> NG (Lagos)`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Port of Rotterdam | `https://www.portofrotterdam.com` | `web_search` + `web_extract` or `browser_navigate` | EU-origin shipping lane context and schedule references |
| Maersk | `https://www.maersk.com` | `browser_navigate` | EU->West Africa ocean route discovery |
| CMA CGM | `https://www.cma-cgm.com` | `browser_navigate` | Carrier route and transit references |
| Hapag-Lloyd | `https://www.hapag-lloyd.com` | `browser_navigate` | Carrier service and lane coverage references |

For customs with `destination_country=NG`, delegate to `nigeria-customs.md` instructions.

## Query Patterns
- `"Rotterdam to Lagos freight quote"`
- `"EU to Nigeria shipping rate {weight_kg}kg"`
- `"Europe to Lagos container freight price"`
- `"official customs duty Nigeria HS {hs_code}"` (customs leg handoff)

## Expected Fields
### Freight leg (`freight_quote`)
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

### Customs leg (`customs_quote`)
Follow `nigeria-customs.md` expected fields exactly.

## Open-Web Recovery Instructions
If lane-specific carrier portals fail or are blocked:
1. Switch to open-web discovery with route-scoped carrier/forwarder queries.
2. Cross-check at least two independent sources before returning quote values.
3. Keep full citation metadata for each source.
4. Use `source_type=open_web` where schema permits.
5. If route evidence is weak or contradictory, fail fast with explicit failure.

## Fail-Fast Rules
- Do not combine EU-wide averages with specific-lane quotes without explicit labeling.
- Do not output a customs estimate from non-verifiable sources.
- Return only JSON output matching the required schema.
