# Russia Customs (Destination: RU)

## Coverage
Use for customs leg when `destination_country=RU`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Federal Customs Service of Russia | `https://customs.gov.ru` | `browser_navigate` for interactive resources; `web_extract` for static pages | Primary customs authority information |
| Eurasian Economic Commission tariff references | discover via `site:.eaeunion.org` queries | `web_search` + `web_extract` | EAEU tariff/legal context where applicable |
| Government legal publications | discover via `site:.gov.ru customs tariff` | `web_search` + `web_extract` | Statutory or regulatory references |

## Query Patterns
- `"Russia customs duty HS {hs_code}"`
- `"site:customs.gov.ru tariff HS {hs_code}"`
- `"site:.gov.ru import customs duty schedule"`
- `"EAEU customs tariff HS {hs_code}"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If official portals are inaccessible or blocked:
1. Use open-web discovery restricted to government/statutory domains first.
2. Use multiple authoritative references before returning final rates.
3. Include full `sources[]` metadata for every extracted value.
4. Set `source_type=open_web` when schema allows.
5. Fail fast if evidence is incomplete or contradictory.

## Fail-Fast Rules
- Do not return customs rates without source-backed legal/tariff references.
- If portal data is stale or unclear for the HS line, return explicit failure.
- Return schema-bound JSON only.
