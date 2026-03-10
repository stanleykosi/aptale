# UAE Customs (Destination: AE)

## Coverage
Use for customs leg when `destination_country=AE`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| UAE government customs references | discover via `site:.gov.ae customs tariff` | `web_search` + `web_extract` | Federal customs policy and guidance discovery |
| Dubai Customs | `https://www.dubaicustoms.gov.ae` | `browser_navigate` + `web_extract` | Emirate-level customs services and references |
| Abu Dhabi Customs | `https://www.abudhabicustoms.gov.ae` | `browser_navigate` + `web_extract` | Emirate-level customs service references |

## Query Patterns
- `"UAE customs duty HS {hs_code}"`
- `"site:.gov.ae customs tariff import duty"`
- `"Dubai customs tariff HS {hs_code}"`
- `"Abu Dhabi customs import duty schedule"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If emirate portals are unavailable:
1. Use open-web discovery across official `.gov.ae` customs sources.
2. Cross-check tariff values from at least two authoritative references.
3. Include full citation metadata per extracted value.
4. Use `source_type=open_web` when allowed.
5. Fail fast on inconsistent or unverifiable rates.

## Fail-Fast Rules
- Do not mix emirate-specific rules with federal assumptions without citation.
- If customs rates cannot be validated, return explicit failure.
- Return JSON-only output.
