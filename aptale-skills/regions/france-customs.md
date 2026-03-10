# France Customs (Destination: FR)

## Coverage
Use for customs leg when `destination_country=FR`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| French Customs (Douane) | `https://www.douane.gouv.fr` | `web_search` + `web_extract`; `browser_navigate` for tools | Primary customs authority |
| TARIC (EU tariff system) | `https://ec.europa.eu/taxation_customs/dds2/taric` | `browser_navigate` | EU duty lookup by commodity code |
| French government legal pages | discover via `site:.gouv.fr douane tarif` | `web_search` + `web_extract` | Regulatory reference checks |

## Query Patterns
- `"France customs duty HS {hs_code}"`
- `"site:douane.gouv.fr nomenclature tarifaire"`
- `"EU TARIC {hs_code}"`
- `"France import TVA customs basis"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If primary portals fail:
1. Use open-web discovery anchored to `.gouv.fr` and EU tariff sources.
2. Cross-check commodity code duties and import tax context.
3. Preserve complete source citations.
4. Set `source_type=open_web` when schema permits.
5. Fail fast on weak or conflicting evidence.

## Fail-Fast Rules
- Do not return uncited duty rates.
- If commodity code lookup fails, return explicit failure.
- Return JSON object only.
