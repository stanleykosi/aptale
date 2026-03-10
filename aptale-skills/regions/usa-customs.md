# United States Customs (Destination: US)

## Coverage
Use for customs leg when `destination_country=US`.

## Known Portals (Official First)
| Portal | URL | Preferred Tools | Purpose |
|---|---|---|---|
| U.S. Customs and Border Protection (CBP) | `https://www.cbp.gov` | `web_search` + `web_extract`; `browser_navigate` for interactive pages | Primary authority for U.S. import/customs guidance |
| Harmonized Tariff Schedule (HTSUS) | `https://hts.usitc.gov` | `browser_navigate` for interactive HS lookup | Duty rate lookup by tariff code |
| U.S. International Trade Commission | `https://www.usitc.gov` | `web_search` + `web_extract` | Tariff/legal reference publications |

## Query Patterns
- `"US customs duty HS {hs_code}"`
- `"site:cbp.gov import duty tariff"`
- `"site:hts.usitc.gov HS {hs_code}"`
- `"US customs assessment basis CIF FOB"`

## Expected Fields (customs_quote)
Return JSON fields needed for `customs_quote`:
- `quote_id`, `extraction_id`, `destination_country`
- `assessment_basis`
- `lines[]` with `line_id`, `hs_code`, `duty_rate_pct`, `vat_rate_pct`, `additional_rate_pct`, `fixed_fee`, `fixed_fee_currency`, `legal_reference`
- `source_type`, `sources[]`, `captured_at`

## Open-Web Recovery Instructions
If primary portals are unavailable or blocked:
1. Switch to open-web discovery using official-domain-first queries.
2. Cross-check rate/legal references across at least two authoritative sources.
3. Preserve full citation metadata in `sources[]`.
4. Set `source_type=open_web` when schema allows.
5. If no verifiable tariff evidence exists, fail fast.

## Fail-Fast Rules
- Do not infer duty values from unofficial summaries without references.
- If HS mapping is unresolved, return explicit failure to parent.
- Return JSON object only, no prose wrapper.
