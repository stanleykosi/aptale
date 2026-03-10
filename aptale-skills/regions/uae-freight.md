# UAE Freight (Origin: AE)

## Coverage
Use for freight leg when `origin_country=AE`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| DP World | `https://www.dpworld.com` | `browser_navigate` | Port/logistics route references |
| Emirates SkyCargo | `https://www.skycargo.com` | `browser_navigate` | Air cargo route/quote references |
| Etihad Cargo | `https://www.etihadcargo.com` | `browser_navigate` | Air freight lane references |
| Maersk UAE references | `https://www.maersk.com` | `browser_navigate` | Ocean lane/rate references |

## Query Patterns
- `"UAE to {destination_country} freight quote"`
- `"Jebel Ali to {destination_port} shipping rate"`
- `"UAE air cargo {destination_country} {weight_kg}kg"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If portal extraction fails:
1. Switch to open-web discovery with carrier/port official pages.
2. Cross-check at least two lane-specific sources.
3. Keep full citations and retrieval metadata.
4. Set `source_type=open_web` when schema allows.
5. Fail fast on unverifiable route pricing.

## Fail-Fast Rules
- Do not mix sea and air values without explicit mode.
- Return JSON object only.
