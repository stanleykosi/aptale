# Japan Customs (Destination: JP)

## Coverage
Use for customs leg when `destination_country=JP`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Japan Customs | `https://www.customs.go.jp` | `web_search` + `web_extract`; `browser_navigate` for interactive sections | Primary import duty and customs procedures |
| Ministry of Finance (Japan) | `https://www.mof.go.jp` | `web_search` + `web_extract` | Supporting legal and tariff policy references |
| Government publications | discover via `site:.go.jp customs tariff` | `web_search` + `web_extract` | Backup statutory references |

## Query Patterns
- `"Japan customs duty HS {hs_code}"`
- `"site:customs.go.jp tariff HS {hs_code}"`
- `"site:.go.jp import customs duty schedule"`
- `"Japan customs VAT consumption tax import"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If portal navigation fails:
1. Switch to open-web discovery with government-domain-first queries.
2. Validate HS-specific rates against at least two authoritative references.
3. Keep citations complete and method-tagged.
4. Set `source_type=open_web` where allowed.
5. Fail fast if rates cannot be verified.

## Fail-Fast Rules
- Do not output partial customs lines.
- Do not infer legal references if none are available.
- Return JSON object only.
