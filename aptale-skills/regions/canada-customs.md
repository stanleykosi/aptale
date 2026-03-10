# Canada Customs (Destination: CA)

## Coverage
Use for customs leg when `destination_country=CA`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Canada Border Services Agency (CBSA) | `https://www.cbsa-asfc.gc.ca` | `web_search` + `web_extract`; `browser_navigate` as needed | Primary import/customs authority |
| Government of Canada tariff finder pages | `https://www.canada.ca` | `web_search` + `web_extract` | Official tariff and tax references |
| Canada Gazette / legal notices | discover via `site:canada.ca customs tariff` | `web_search` + `web_extract` | Regulatory verification |

## Query Patterns
- `"Canada customs duty HS {hs_code}"`
- `"site:cbsa-asfc.gc.ca tariff classification"`
- `"site:canada.ca import customs duty schedule"`
- `"Canada customs GST import assessment basis"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If official portals fail:
1. Use open-web discovery anchored on official Canadian government domains.
2. Confirm values across multiple authoritative pages.
3. Include complete citations for each sourced value.
4. Set `source_type=open_web` when schema permits.
5. Fail fast on weak or missing evidence.

## Fail-Fast Rules
- Do not return non-authoritative blog/forum values as customs rates.
- If HS line cannot be mapped to an official tariff reference, return explicit failure.
- Return strict JSON only.
