---
name: aptale-master-router
description: Map route pairs to freight and customs sourcing paths, enforce Browserbase/open-web switching rules, require strict source citations, and return JSON-only schema-compliant outputs.
version: 1.0.0
metadata:
  hermes:
    tags: [aptale, routing, freight, customs, fx, browserbase, sourcing]
    related_skills: [calculate-landed-cost]
---

# Aptale Master Router Skill

## When to Use
Use this skill for delegated sourcing tasks that must return one of these canonical payloads:
- `freight_quote`
- `customs_quote`
- `fx_quote`

Load this skill only after parent validation is complete and task context includes:
- `task_type`
- route fields (`origin_country`, `destination_country`, optional ports)
- HS-code lines for customs tasks
- required output schema name

## Non-Negotiable Rules
1. Return JSON only. No markdown, no prose, no code fences.
2. Return exactly one object matching the required schema.
3. Include complete source citations for every externally sourced value.
4. Do not guess missing routing inputs. Fail fast if required fields are absent.
5. Do not expose supplier names, invoice pricing internals, or other PII outside the required output payload.

## Router Procedure
1. Normalize route key as `<ORIGIN_COUNTRY>-><DESTINATION_COUNTRY>` using ISO-2 uppercase.
2. Select sourcing leg behavior by `task_type`:
- `freight`: map route pair to freight portal strategy.
- `customs`: map destination country to official customs strategy.
- `fx`: use open-web rate sourcing strategy.
3. Apply the Browserbase/open-web decision rules below.
4. Produce final output in the required schema with citations and retrieval metadata.

For lane examples and query patterns, read `docs/router-examples.md`.

## Route Mapping Rules
### Freight (`task_type=freight`)
- If a lane-specific freight file exists in `regions/`, use it first.
- If lane file is unavailable or does not define a working portal, use open-web discovery.
- Prefer Browserbase for dynamic/interactive quote portals (login, JS-heavy pages, forms).
- Prefer `web_search` + `web_extract` for static pages and non-interactive carrier/forwarder tables.

### Customs (`task_type=customs`)
- Route by destination country customs authority.
- Prioritize official government customs sources.
- Use Browserbase for interactive tariff tools; use web tools for static tariff publications.
- If official portal is blocked/offline, switch to open-web discovery for verifiable government or statutory references.
- If no verifiable customs source is found, fail fast rather than fabricating rates.

### FX (`task_type=fx`)
- Use open-web discovery (`web_search`, `web_extract`) as canonical path.
- Return official rate and parallel rate (if available), clearly labeled by source type.

## Browserbase vs Open-Web Decision Rules
Use Browserbase when any of the following is true:
- The source requires user interaction (clicks, pagination, input forms).
- The source is rendered dynamically and key data is not visible via raw extraction.
- Anti-bot behavior requires Browserbase session handling.

Use open-web discovery when any of the following is true:
- Source pages are static and directly extractable.
- Route has no known maintained portal instruction.
- Browserbase flow repeatedly fails due unavailable pages, persistent CAPTCHA, or hard blocks.

## Open-Web Switch Rules
Switch to open-web discovery when:
- Known portal returns `404`/`5xx`/offline signals.
- Persistent CAPTCHA blocks completion.
- Lane-specific portal instructions are missing or stale.

When switched:
- Mark schema source type as `open_web` where allowed.
- Preserve explicit citation quality requirements.
- Do not silently omit failure context from citations.

## Citation Requirements
Every output must include `sources` entries with:
- `source_url`
- `source_title`
- `retrieved_at` (ISO-8601 UTC)
- `method` (`browserbase`, `web_search`, or `web_extract` per schema)

For FX:
- Include `rate_type` per source (`official` or `parallel`).
- Ensure `official_rate.source_url` is populated.

## JSON Output Requirements By Leg
- Freight: return payload compliant with `freight_quote` schema.
- Customs: return payload compliant with `customs_quote` schema.
- FX: return payload compliant with `fx_quote` schema.

Output must be a single valid JSON object and must not include any explanatory text.

## Progressive Disclosure
- For examples and lane/query templates: read `docs/router-examples.md`.
- For lane-specific instructions: read files under `regions/` only when the current route needs them.
- Do not load unrelated region files.

## Verification Checklist
- Route mapping was derived from normalized country pair.
- Tool choice follows Browserbase/open-web decision rules.
- Returned payload validates against required schema.
- All required citation fields are present and non-empty.
- Output is JSON-only with no prose.
