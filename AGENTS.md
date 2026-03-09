You are developing Aptale, an autonomous AI freight and customs broker built on the Hermes Agent framework. It operates over WhatsApp to ingest invoices, scrape customs/freight data via Browserbase, calculate landed costs via Python scripts, and schedule proactive alerts.

## Architecture
- **Core Framework:** Hermes Agent (Python 3.11+)
- **Messaging Gateway:** WhatsApp bridge (via Baileys/Node.js)
- **Scraping/Web:** Browserbase (`browser` toolset) with `BROWSERBASE_PROXIES=true`
- **Memory/State:** Hermes native memory (`MEMORY.md`, `USER.md`) + Honcho API integration
- **Extensions:** Custom skills hosted in a private GitHub repository

## Hard-Cut Product Policy
- This application currently has no external installed user base; optimize for one canonical current-state implementation, not compatibility with historical local states.
- Do not preserve or introduce compatibility bridges, migration shims, fallback paths, compact adapters, or dual behavior for old local states unless the user explicitly asks for that support.
- Prefer:
  - one canonical current-state codepath
  - fail-fast diagnostics
  - explicit recovery steps
over:
  - automatic migration
  - compatibility glue
  - silent fallbacks
  - "temporary" second paths
- If temporary migration or compatibility code is introduced for debugging or a narrowly scoped transition, it must be called out in the same diff with:
  - why it exists
  - why the canonical path is insufficient
  - exact deletion criteria
  - the ADR/task that tracks its removal
- Default stance across the app: delete old-state compatibility code rather than carrying it forward.

## Hermes-Specific Development Conventions
- **Subagent Delegation:** When using `delegate_task` for parallel sourcing, ALWAYS pass exhaustive context. Subagents have zero knowledge of the parent's conversation history.
- **Structured Data Extraction:** Subagents scraping portals must return strict JSON payloads to the parent agent. Do not pass unstructured text to the cost calculation step.
- **Error Handling (Fail-Fast):** Aligning with the Hard-Cut policy, if a government portal is offline or a CAPTCHA fails permanently, do not use silent fallbacks. Fail fast, inform the user explicitly of the outage, and offer to switch to an open-web search.
- **Custom Skills (`SKILL.md`):** Write all new portal routing and extraction logic as Hermes Skills. Use progressive disclosure to minimize token usage. 
- **Security & PII:** Invoices contain sensitive data. Do not write supplier names, prices, or PII into standard `print()` statements outside of the direct WhatsApp response pipeline.