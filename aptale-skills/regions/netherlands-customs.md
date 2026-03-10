# Netherlands Customs (Destination: NL)

## Coverage
Use for customs leg when `destination_country=NL`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Dutch Customs (Belastingdienst Douane) | `https://www.belastingdienst.nl/wps/wcm/connect/nl/douane` | `web_search` + `web_extract`; `browser_navigate` as needed | Primary customs authority |
| TARIC (EU tariff system) | `https://ec.europa.eu/taxation_customs/dds2/taric` | `browser_navigate` | EU tariff duty lookup |
| Dutch government legal references | discover via `site:.overheid.nl douane tarief` | `web_search` + `web_extract` | Regulatory support |

## Query Patterns
- `"Netherlands customs duty HS {hs_code}"`
- `"site:belastingdienst.nl douane tarief"`
- `"EU TARIC {hs_code}"`
- `"Netherlands import VAT customs basis"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If primary pages are unavailable:
1. Switch to open-web discovery with official Dutch/EU sources.
2. Cross-check HS-specific rates and import tax context.
3. Keep citations complete and method-tagged.
4. Use `source_type=open_web` where allowed.
5. Fail fast on unclear or conflicting tariff evidence.

## Fail-Fast Rules
- Do not output duties without authoritative references.
- If HS mapping cannot be validated, return explicit failure.
- Return strict JSON only.
