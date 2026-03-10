# Nigeria Customs (Destination: NG)

## Coverage
Use for customs leg when `destination_country=NG`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Nigeria Customs Service (NCS) | `https://customs.gov.ng` | `browser_navigate` for interactive pages; `web_extract` for static publications | Primary government authority for import duty/tariff guidance |
| Nigeria Trade Portal | `https://trade.gov.ng` | `web_search` + `web_extract` | Trade and border-procedure references |
| Federal Government legal publications (customs/tariff notices) | discover via `site:.gov.ng` query | `web_search` + `web_extract` | Legal/reference confirmation when duty notes are not clear |

## Query Patterns
- `"Nigeria customs duty HS {hs_code}"`
- `"site:customs.gov.ng tariff HS {hs_code}"`
- `"site:.gov.ng Nigeria customs import duty schedule"`
- `"Nigeria import VAT customs assessment basis CIF FOB"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If official portal navigation fails (offline, 404/5xx, persistent CAPTCHA):
1. Switch to open-web discovery with government-domain-first queries.
2. Prefer sources that publish duty or legal references tied to HS codes.
3. Keep `source_type=open_web` when schema allows and citations are complete.
4. If rates cannot be verified from authoritative sources, fail fast (do not guess).

## Fail-Fast Rules
- If HS code is missing for a required line, return explicit failure to parent.
- If retrieved source has no verifiable duty or tax values, return explicit failure.
- Never emit prose where schema-bound JSON is required.
