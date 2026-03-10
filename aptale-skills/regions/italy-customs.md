# Italy Customs (Destination: IT)

## Coverage
Use for customs leg when `destination_country=IT`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| ADM (Italian Customs and Monopolies Agency) | `https://www.adm.gov.it` | `web_search` + `web_extract`; `browser_navigate` as needed | Primary customs/tariff authority |
| TARIC (EU tariff system) | `https://ec.europa.eu/taxation_customs/dds2/taric` | `browser_navigate` | EU duty lookup by HS code |
| Government legal publications | discover via `site:.gov.it dogane tariffa` | `web_search` + `web_extract` | Legal/tax reference support |

## Query Patterns
- `"Italy customs duty HS {hs_code}"`
- `"site:adm.gov.it tariffa doganale"`
- `"EU TARIC {hs_code}"`
- `"Italy import IVA customs basis"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If ADM/TARIC fails:
1. Switch to open-web discovery with official `.gov.it` and EU sources.
2. Validate HS-specific values across authoritative references.
3. Keep complete citation metadata.
4. Use `source_type=open_web` when allowed.
5. Fail fast when rates are not verifiable.

## Fail-Fast Rules
- Do not use unofficial summaries as final duty values.
- If HS duty cannot be confirmed, return explicit failure.
- Return strict schema-bound JSON only.
