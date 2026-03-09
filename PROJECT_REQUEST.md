## Project Description
Aptale is an autonomous AI freight and customs broker built on the Hermes Agent framework. It operates entirely over WhatsApp, assisting SMBs and importers globally with cross-border trade. By ingesting photos of commercial invoices, the agent translates foreign documents, uses vision to extract data, and spawns parallel subagents to scrape country-specific shipping portals, official customs duties, and real-time FX rates. It calculates total landed costs, generates downloadable breakdowns with custom skills, and proactively monitors the market to alert merchants when profitable arbitrage windows open.

## Target Audience
- Small and Medium Businesses (SMBs) engaged in global cross-border trade.
- Importers and merchants who rely heavily on WhatsApp for business communication.
- Users operating in regions with complex customs duties and volatile foreign exchange rates (e.g., parallel/black markets in emerging economies like Nigeria).

## Desired Features
### 1. Ingestion, Vision & Translation
- [ ] WhatsApp Gateway Integration
    - [ ] Accept images of commercial invoices and shipping manifests via WhatsApp DM.
- [ ] Multilingual Document Processing
    - [ ] Automatically detect and translate foreign invoices (e.g., Chinese, Turkish) to the user's local language before processing.
- [ ] Invoice Data Extraction & Validation
    - [ ] Use `vision_analyze` to extract line items, weights, quantities, and origin/destination.
    - [ ] Automatically identify or infer HS (Harmonized System) codes for extracted items.
    - [ ] **Validation Step:** Use the `clarify` tool or conversational pausing to present an "Extraction Summary" to the user. Require explicit user confirmation (or correction) before spawning the heavy sourcing subagents.

### 2. Multinational Sourcing (Dynamic Subagents)
- [ ] Context-Aware Routing
    - [ ] Automatically infer the user's country/route from the document or chat history, or explicitly ask if unknown.
-[ ] Universal Freight & Customs Sourcing
    - [ ] Subagent 1 (Freight): Use `browser_navigate` to dynamically locate and scrape regional shipping portals for current rates.
    - [ ] Subagent 2 (Customs): Use `browser_navigate` to query specific official government customs portals for import duty percentages.
    -[ ] **Dynamic Open-Internet Capability:** Ensure skills accommodate all countries. If a specific legacy portal isn't explicitly known, subagents must autonomously use `web_search` and `web_extract` to find the required customs and freight data on the open internet.
- [ ] FX Rate Sourcing
    - [ ] Subagent 3 (FX): Use `web_search` to find real-time foreign exchange rates, automatically contrasting official bank rates with parallel/black-market rates where applicable.

### 3. Data Crunching & Export
- [ ] Landed Cost Calculation
    - [ ] Use `execute_code` to write a Python script aggregating freight, duties, and FX data.
    - [ ] Calculate the total landed cost in the user's local currency, factoring in their saved profit margins.
- [ ] Liability Disclaimer
    - [ ] Automatically append a standard legal/accuracy disclaimer (e.g., *"Estimates only, subject to final customs assessment and market fluctuations"*) immediately following any cost calculation or quote.
- [ ] Cost Breakdown Export
    - [ ] Generate a formatted PDF or CSV detailing the cost breakdown.
    - [ ] **Document Branding:** Include a simple, professional branded footer (TradeWeaver text/logo) on the exported documents.
    - [ ] Send the generated file back to the user as a WhatsApp document attachment.

### 4. Custom Skills Integration (Private Repo)
- [ ] Dynamic Routing Skill (`SKILL.md`)
    - [ ] Design a master sourcing skill that acts as a dynamic router, giving the agent the procedures to map regions to portals, or execute open-web searches if portals are unavailable.
- [ ] Private Hub Hosting
    - [ ] Store all custom skills (PDF generation, regional routing, arbitrage calculation) in a private GitHub repository.
    - [ ] Use `hermes skills tap add` with Git authentication to deploy and seamlessly update skills to the agent.

### 5. Memory & User Profiling
- [ ] Persistent Preferences (Hermes Memory)
    - [ ] Use Hermes' built-in `USER.md` and `MEMORY.md` to remember the merchant's default profit margins, preferred shipping routes, and currency.
    - [ ] **Timezone Management:** Explicitly save the user's local timezone to ensure scheduled alerts trigger at the correct local time.
- [ ] Deep User Modeling (Honcho)
    - [ ] Integrate Honcho API to build cross-session profiles (e.g., tracking business goals, preferred communication style, and historical trade volume).

### 6. Proactive Alerts & Automation
- [ ] Natural Language Scheduling
    - [ ] Allow users to set target price/rate thresholds via chat.
- [ ] Automated Background Monitoring
    - [ ] Use `schedule_cronjob` to run the parallel sourcing and crunching workflow daily (e.g., at 8 AM local time).
- [ ] WhatsApp Delivery
    - [ ] Send automated WhatsApp alerts to the user the moment the shipping/FX arbitrage window matches their criteria.

## Design Requests
- [ ] Conversational UX
    - [ ] The entire user experience must remain inside WhatsApp—no external dashboards for the merchant.
    - [ ] Responses should be formatted cleanly using WhatsApp markdown (bolding, lists).
- [ ] Dynamic Bot Personality (`SOUL.md`)
    - [ ] Baseline personality must be professional, conversational, and helpful (acting as a trusted broker).
    - [ ] Use Honcho's `query_user_context` to dynamically adjust tone and brevity based on the user's historical behavior (e.g., adapting to users who prefer quick numbers vs. those who need detailed explanations).
- [ ] Phased Rollout Security
    - [ ] Restrict initial MVP access using Hermes' `WHATSAPP_ALLOWED_USERS` whitelist for selected beta testers.

## Other Notes
- **Framework:** Built on the Hermes Agent framework by Nous Research.
- **Private Skill Authentication:** Deployment environment must be configured with a GitHub PAT (Personal Access Token) to allow Hermes to pull updates from the private skills repository.
- **Scraping Resiliency:** Requires Browserbase API configured with `BROWSERBASE_PROXIES=true` to bypass aggressive CAPTCHAs on legacy government and shipping portals.
- **WhatsApp Stability:** The Baileys WhatsApp bridge requires a highly available Docker deployment. Implement monitoring to alert the admin if the WhatsApp Web session disconnects and requires QR re-pairing.
- **Data Structuring:** Needs robust prompt engineering to ensure subagents strictly return structured JSON data to the parent agent to avoid calculation errors.
- **Graceful Error Handling:** If a government portal is completely offline or a search fails, the agent must proactively inform the user of the outage rather than hanging or returning a silent error.
- **Token Optimization:** Vision analysis + 3 parallel subagents (`delegate_task`) + Browserbase is token-intensive. Recommend using a high-tier but cost-effective model (like Claude 3.5 Sonnet or a fast open-weight model) via OpenRouter to balance reasoning capability with API costs.
- **Data Privacy (PII):** Invoices contain highly sensitive supplier and pricing data. Include a privacy notice to users regarding data handling, and ensure the deployment environment logs are securely managed and periodically flushed.