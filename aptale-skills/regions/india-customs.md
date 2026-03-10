# India Customs (Destination: IN)

## Coverage
Use for customs leg when `destination_country=IN`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Central Board of Indirect Taxes and Customs (CBIC) | `https://www.cbic.gov.in` | `web_search` + `web_extract` | Primary customs/tariff notifications |
| Indian Customs portal sections | discover via `site:cbic.gov.in customs tariff` | `web_search` + `web_extract`; `browser_navigate` as needed | Duty schedule and related notices |
| Government legal publications | discover via `site:.gov.in customs notification` | `web_search` + `web_extract` | Legal cross-check references |

## Query Patterns
- `"India customs duty HS {hs_code}"`
- `"site:cbic.gov.in customs tariff HS {hs_code}"`
- `"site:.gov.in customs notification import duty"`
- `"India customs IGST import assessment basis"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If portal pages are blocked or unavailable:
1. Switch to open-web discovery prioritizing official `.gov.in` sources.
2. Cross-check rate components from primary notifications and guidance pages.
3. Keep citation metadata complete and method-tagged.
4. Use `source_type=open_web` where permitted.
5. Fail fast on incomplete legal/rate evidence.

## Fail-Fast Rules
- Do not infer duty/VAT components from summaries without legal references.
- If tariff data is not current or traceable, return explicit failure.
- Return JSON object only.
