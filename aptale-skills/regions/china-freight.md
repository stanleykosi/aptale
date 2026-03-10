# China to Nigeria Freight (CN->NG)

## Coverage
Use for freight leg when `origin_country=CN` and `destination_country=NG`.

## Known Portals
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Freightos | `https://www.freightos.com` | `browser_navigate` for quote workflows | Aggregated freight quote comparisons |
| Maersk | `https://www.maersk.com` | `browser_navigate` | Ocean freight schedules and indicative pricing |
| CMA CGM | `https://www.cma-cgm.com` | `browser_navigate` | Ocean freight routing and schedules |
| Hapag-Lloyd | `https://www.hapag-lloyd.com` | `browser_navigate` | Ocean freight lanes and service details |
| Forwarder/open listings | discover by query | `web_search` + `web_extract` | Non-interactive rate references and market checks |

## Query Patterns
- `"freight quote Guangzhou to Lagos {weight_kg}kg"`
- `"sea freight China to Nigeria rate"`
- `"air cargo China to Nigeria forwarder quote"`
- `"LCL FCL China Nigeria shipping cost"`

## Expected Fields (freight_quote)
Return JSON fields needed for `freight_quote`:
- `quote_id`, `extraction_id`, `provider_name`
- `origin_country`, `destination_country`, `origin_port`, `destination_port`
- `mode`, `service_level`, `transit_time_days`
- `currency`, `quote_amount`, `charge_breakdown[]`, `valid_until`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If browser quote portals are unavailable or blocked:
1. Switch to open-web discovery for carrier/forwarder lane pricing references.
2. Use at least one lane-specific source and one cross-check source.
3. Keep source metadata complete (`source_url`, `source_title`, `retrieved_at`, `method`).
4. Set `source_type=open_web` when schema allows.
5. If no verifiable route quote is available, fail fast instead of estimating.

## Fail-Fast Rules
- Do not return blank `charge_breakdown`.
- Do not mix different lane directions in a single quote.
- Do not output prose wrappers; return JSON object only.
