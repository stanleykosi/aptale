# Router Examples

This file provides route-mapping and sourcing examples for the Aptale master router skill.

## 1. Route Key Normalization
- Input: `origin_country="cn"`, `destination_country="ng"`
- Normalized key: `CN->NG`

- Input: `origin_country="tr"`, `destination_country="ng"`
- Normalized key: `TR->NG`

## 2. Route Mapping Patterns
Use these patterns until lane-specific files in `regions/` are available.

| Pattern | Freight routing | Customs routing |
|---|---|---|
| `CN->NG` | Prefer lane file `regions/china-freight.md`; otherwise open-web discovery | Prefer `regions/nigeria-customs.md` for destination |
| `TR->NG` | Prefer lane file `regions/turkey-freight.md`; otherwise open-web discovery | Prefer `regions/nigeria-customs.md` for destination |
| `EU->NG` | Prefer lane file `regions/eu-import-lane.md`; otherwise open-web discovery | Prefer `regions/nigeria-customs.md` for destination |
| Unknown lane | Open-web discovery with route-scoped queries | Destination-country official customs discovery |

## 3. Query Templates
### Freight (open-web discovery)
- `"air freight rate {origin_port} to {destination_port} {weight_kg}kg"`
- `"freight forwarder quote {origin_country} to {destination_country}"`
- `"carrier shipping rates {origin_country} {destination_country}"`

### Customs (official-first discovery)
- `"official customs tariff {destination_country} HS {hs_code}"`
- `"{destination_country} customs import duty schedule"`
- `"{destination_country} customs legal reference HS code"`

### FX
- `"official exchange rate {base_currency} to {quote_currency}"`
- `"parallel market rate {base_currency} {quote_currency}"`

## 4. Browserbase-First Example
Use Browserbase if a tariff or quote tool needs interaction:
1. `browser_navigate` to portal.
2. Interact with controls (search form, HS lookup, lane selector).
3. Capture values and metadata.
4. Include portal URL and retrieval time in `sources`.

## 5. Open-Web Switch Example
If Browserbase hits persistent CAPTCHA or outage:
1. Stop repeating blocked portal attempts.
2. Use `web_search` to locate alternative authoritative sources.
3. Use `web_extract` to capture rate/duty details.
4. Set `source_type` to `open_web` where schema supports it.
5. If no verifiable source is found, fail fast instead of guessing.

## 6. Citation Mini-Checklist
For each `sources[]` entry:
- `source_url` is absolute URL.
- `source_title` is human-readable.
- `retrieved_at` is ISO-8601 UTC timestamp.
- `method` matches schema-allowed values.

For FX:
- Include `rate_type` on each source.
- Include `official_rate.source_url`.

## 7. JSON-Only Output Reminder
Final response must be one JSON object matching the required schema and nothing else.

## 8. Extended Country Coverage Index
### Customs files
- `regions/usa-customs.md` (`US`)
- `regions/canada-customs.md` (`CA`)
- `regions/russia-customs.md` (`RU`)
- `regions/japan-customs.md` (`JP`)
- `regions/india-customs.md` (`IN`)
- `regions/uk-customs.md` (`GB`)
- `regions/uae-customs.md` (`AE`)
- `regions/brazil-customs.md` (`BR`)
- `regions/germany-customs.md` (`DE`)
- `regions/france-customs.md` (`FR`)
- `regions/italy-customs.md` (`IT`)
- `regions/spain-customs.md` (`ES`)
- `regions/netherlands-customs.md` (`NL`)
- `regions/nigeria-customs.md` (`NG`)

### Freight files
- `regions/usa-freight.md` (`US`)
- `regions/canada-freight.md` (`CA`)
- `regions/russia-freight.md` (`RU`)
- `regions/japan-freight.md` (`JP`)
- `regions/india-freight.md` (`IN`)
- `regions/uk-freight.md` (`GB`)
- `regions/uae-freight.md` (`AE`)
- `regions/brazil-freight.md` (`BR`)
- `regions/germany-freight.md` (`DE`)
- `regions/france-freight.md` (`FR`)
- `regions/italy-freight.md` (`IT`)
- `regions/spain-freight.md` (`ES`)
- `regions/netherlands-freight.md` (`NL`)
- `regions/nigeria-freight.md` (`NG`)
- `regions/china-freight.md` (`CN`)
- `regions/turkey-freight.md` (`TR`)
- `regions/eu-import-lane.md` (EU lane pattern)
