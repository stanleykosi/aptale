# United Kingdom Customs (Destination: GB)

## Coverage
Use for customs leg when `destination_country=GB`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| HM Revenue & Customs (HMRC) | `https://www.gov.uk/government/organisations/hm-revenue-customs` | `web_search` + `web_extract` | Primary UK customs authority |
| UK Trade Tariff | `https://www.trade-tariff.service.gov.uk` | `browser_navigate` for lookup interactions | Commodity code duty lookup |
| GOV.UK customs pages | `https://www.gov.uk` | `web_search` + `web_extract` | Policy, duties, and VAT references |

## Query Patterns
- `"UK customs duty commodity code {hs_code}"`
- `"site:trade-tariff.service.gov.uk {hs_code}"`
- `"site:gov.uk import duty VAT customs"`
- `"HMRC import tariff schedule"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If tariff service or HMRC pages are unavailable:
1. Switch to open-web discovery across official GOV.UK domains.
2. Cross-check commodity code results and duty/VAT references.
3. Include complete source metadata for each extracted value.
4. Set `source_type=open_web` where schema allows.
5. Fail fast when values cannot be verified.

## Fail-Fast Rules
- Do not return duties from non-official mirrors without corroboration.
- If tariff lookup fails for the HS code, return explicit failure.
- Return strict JSON only.
