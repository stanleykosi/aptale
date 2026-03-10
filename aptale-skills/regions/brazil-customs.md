# Brazil Customs (Destination: BR)

## Coverage
Use for customs leg when `destination_country=BR`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Receita Federal (Brazil) | `https://www.gov.br/receitafederal` | `web_search` + `web_extract` | Primary federal tax/customs authority information |
| Government legal publications | discover via `site:.gov.br customs tariff` | `web_search` + `web_extract` | Tariff and legal notice references |
| Trade/customs guidance portals | discover via `site:.gov.br importacao` | `web_search` + `web_extract`; `browser_navigate` as needed | Import process and duty context |

## Query Patterns
- `"Brazil customs duty NCM {hs_code}"`
- `"site:gov.br receitafederal importacao tarifa"`
- `"site:.gov.br customs tariff import duty"`
- `"Brazil customs VAT import tax basis"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If primary authority pages are unavailable:
1. Switch to open-web discovery focused on official `.gov.br` sources.
2. Cross-check key rates and legal references before output.
3. Keep complete citation metadata in `sources[]`.
4. Set `source_type=open_web` where schema allows.
5. Fail fast if data is incomplete or unverified.

## Fail-Fast Rules
- Do not rely on unofficial calculators without authoritative source backing.
- If NCM/HS mapping is ambiguous, return explicit failure.
- Return strict schema-bound JSON only.
