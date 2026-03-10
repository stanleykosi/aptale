# Germany Customs (Destination: DE)

## Coverage
Use for customs leg when `destination_country=DE`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| German Customs (Zoll) | `https://www.zoll.de` | `web_search` + `web_extract`; `browser_navigate` for interactive pages | Primary customs/tariff authority |
| TARIC (EU tariff system) | `https://ec.europa.eu/taxation_customs/dds2/taric` | `browser_navigate` | EU customs duty lookup for commodity codes |
| Federal legal publications | discover via `site:.bund.de zoll tarif` | `web_search` + `web_extract` | Statutory reference checks |

## Query Patterns
- `"Germany customs duty HS {hs_code}"`
- `"site:zoll.de einfuhrabgaben warennummer"`
- `"EU TARIC {hs_code}"`
- `"Germany import VAT customs basis"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If Zoll/TARIC access fails:
1. Switch to open-web discovery with government/EU-domain-first queries.
2. Cross-check HS-specific rates across authoritative references.
3. Keep full citation metadata in `sources[]`.
4. Set `source_type=open_web` when schema allows.
5. Fail fast if duty/tax evidence is unverifiable.

## Fail-Fast Rules
- Do not emit customs rates without HS-linked official references.
- If HS mapping cannot be validated, return explicit failure.
- Return strict JSON only.
