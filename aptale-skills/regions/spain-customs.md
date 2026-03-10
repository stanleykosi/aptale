# Spain Customs (Destination: ES)

## Coverage
Use for customs leg when `destination_country=ES`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| Agencia Tributaria - Aduanas | `https://sede.agenciatributaria.gob.es` | `browser_navigate` for interactive tools; `web_extract` for static pages | Primary customs/tax authority |
| TARIC (EU tariff system) | `https://ec.europa.eu/taxation_customs/dds2/taric` | `browser_navigate` | EU tariff lookup |
| Spanish government legal publications | discover via `site:.gob.es aduanas arancel` | `web_search` + `web_extract` | Statutory support |

## Query Patterns
- `"Spain customs duty HS {hs_code}"`
- `"site:agenciatributaria.gob.es aduanas arancel"`
- `"EU TARIC {hs_code}"`
- `"Spain import IVA customs assessment"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If customs portals are unavailable:
1. Switch to open-web discovery with `.gob.es` and EU tariff sources.
2. Cross-check duty/tax values before returning output.
3. Keep full citations for all sourced values.
4. Set `source_type=open_web` where schema supports it.
5. Fail fast on unverifiable values.

## Fail-Fast Rules
- Do not return incomplete customs lines.
- If HS lookup cannot be tied to authoritative source, return explicit failure.
- Return JSON object only.
