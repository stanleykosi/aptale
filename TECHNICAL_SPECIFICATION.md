# Aptale Technical Specification

## 1. System Overview

**Aptale** is an autonomous AI freight and customs broker tailored for SMBs and global importers. Built entirely on the Hermes Agent framework, it operates exclusively via WhatsApp. It automates the highly manual cross-border trade process by ingesting commercial invoices via image, extracting and translating data, parallel-sourcing live freight/customs/FX data from the web using sandboxed subagents, calculating landed costs, and proactively alerting merchants to profitable arbitrage windows.

### 1.1 Core Principles (Hard-Cut Policy)
- **Single Canonical Path:** The system optimizes for the current state. No fallback shims or legacy compatibility code. If a government portal changes and breaks a subagent, the system fails fast, informs the user, and explicitly asks to route to an open-web search.
- **Fail-Fast Diagnostics:** Silent errors or guessed calculations are strictly prohibited.
- **Data Privacy:** Supplier pricing and PII extracted from invoices must not be persisted in plain-text logs outside of the WhatsApp response pipeline.

### 1.2 System Architecture
- **Core Framework:** Hermes Agent (Python 3.11+).
- **Messaging Layer:** Hermes WhatsApp Gateway (Baileys/Node.js bridge) in `bot` mode.
- **Model Routing:** OpenRouter (Claude 3.5 Sonnet recommended for optimal vision and complex tool-calling).
- **Web/Scraping:** Browserbase via `browser` toolset (`BROWSERBASE_PROXIES=true`).
- **State & Memory:** Hermes SQLite `state.db`, `USER.md`, `MEMORY.md`, and Honcho API for cross-session dialectic user modeling.
- **Skill Deployment:** Private GitHub repository connected via `hermes skills tap add`.

---

## 2. Project Structure

Aptale's infrastructure is managed via the Hermes configuration directory and a remote private GitHub repository for skills.

```text
~/.hermes/
├── config.yaml               # Core agent, terminal, memory, and provider config
├── .env                      # API Keys (OpenRouter, Browserbase, Honcho, WhatsApp)
├── SOUL.md                   # Aptale's dynamic personality definition
├── hooks/
│   ├── pii-redactor/         # Hook to scrub PII from agent logs
│   └── whatsapp-monitor/     # Hook to monitor Baileys bridge health
├── skills/                   # Pulled automatically via git tap
│   └── .hub/                 # Lockfiles mapping to the private Aptale repo
└── cron/                     # Automated alert jobs

# Aptale Private Skills Repository (GitHub)
aptale-skills/
├── SKILL.md                  # Master Routing Skill
├── calculate-landed-cost/    # PDF/CSV Generation instructions
└── regions/
    ├── nigeria-customs.md    # Specific portal scraping instructions
    └── turkey-freight.md
```

---

## 3. Feature Specification

### 3.1 Ingestion, Vision & Translation
- **Requirements:** Accept images of commercial invoices via WhatsApp. Detect language, translate, extract line items, weights, quantities, origins, and infer HS codes. 
- **Implementation Steps:**
  1. User sends an image to the WhatsApp bot number. Hermes receives the base64 image and passes it to the LLM.
  2. The system prompt instructs the agent to use `vision_analyze` (if needed for deep extraction) or rely on native multimodal ingestion to parse the document.
  3. The agent translates the text to the user's local language (fetched from Honcho or `USER.md`).
  4. The agent structures the data into a strict internal JSON format (Items, HS Codes, Values, Quantities, Weights).
  5. **Validation (Clarify):** The agent calls the `clarify` tool with a markdown-formatted summary of the extracted data. Execution pauses until the user replies "Confirmed" or provides corrections.
- **Edge Cases:** Illegible images. *Handling:* Fail fast. Prompt user: "The invoice is blurry. I cannot extract the origin port and weights reliably. Please upload a clearer photo or type them manually."

### 3.2 Multinational Sourcing (Dynamic Subagents)
- **Requirements:** Spawn 3 parallel subagents to source Freight, Customs Duties, and FX rates based on the extracted data.
- **Implementation Steps:**
  1. The parent agent calls `delegate_task` passing a `tasks` array of length 3.
  2. **Crucial Context Binding:** The parent MUST pass the validated JSON extraction into the `context` parameter for EVERY subagent, alongside the user's country and default margins. *Subagents have zero memory of the parent conversation.*
  3. **Task 1 (Freight):** Uses `browser_navigate` and `browser_snapshot` (with Browserbase proxies) to scrape regional shipping portals.
  4. **Task 2 (Customs):** Uses `browser_navigate` to query government duty portals based on HS codes.
  5. **Task 3 (FX):** Uses `web_search` and `web_extract` to fetch official vs. parallel market exchange rates.
  6. **Open-Internet Fallback:** If `browser_navigate` hits a 404 or persistent CAPTCHA block, the subagent explicitly reports the failure to the parent and immediately uses `web_search` to find the data on alternative open-web sources.
  7. **Strict JSON Return:** Subagents are prompted via their initial system instruction to return ONLY a structured JSON payload detailing the rates found and the source URLs.

### 3.3 Data Crunching & Export
- **Requirements:** Calculate landed costs in local currency, add a legal disclaimer, and generate a branded PDF/CSV returned to the user via WhatsApp.
- **Implementation Steps:**
  1. Parent agent receives the 3 JSON payloads from the subagents.
  2. Agent calls `execute_code`.
  3. The Python script within `execute_code` takes the raw numbers, calculates the total landed cost `((Invoice + Freight) * FX) + (Customs % * Invoice)`, and adds the user's profit margin (from `USER.md`).
  4. The script generates a PDF using a standard library (e.g., `fpdf` or `reportlab`, assuming they are baked into the `docker` terminal backend image) or writes a clean CSV. The document includes a branded footer: *"Generated by Aptale - Estimates only, subject to final customs assessment."*
  5. The script saves the file to the local workspace and prints the file path.
  6. The agent reads the file path and uses the WhatsApp native media delivery (via `terminal` to copy to a public serve dir, or via Hermes' built-in file attachment mapping if supported) to send the document to the user.

### 3.4 Proactive Alerts & Automation
- **Requirements:** Monitor market arbitrage windows daily and alert the user via WhatsApp.
- **Implementation Steps:**
  1. User requests an alert: "Let me know when the parallel FX rate for NGN drops below 1400."
  2. Agent invokes `schedule_cronjob`.
  3. Parameters: `prompt` = "Check FX rates for NGN using web_search. If the parallel rate is under 1400, alert the user with the current rate. Otherwise, say nothing.", `schedule` = "0 8 * * *", `deliver` = "origin".
  4. The Hermes Gateway cron daemon runs this independently every day at 8 AM. If the condition is met, the WhatsApp message is dispatched automatically.

---

## 4. State & Configuration Management

### 4.1 Hermes Configuration (`config.yaml`)
```yaml
terminal:
  backend: docker
  docker_image: "python:3.11-slim"   # Base image for execute_code and terminal tools
  container_persistent: true
  timeout: 300
memory:
  memory_enabled: true
  user_profile_enabled: true
provider_routing:
  sort: "price"
  require_parameters: true
code_execution:
  timeout: 300
```

### 4.2 Honcho User Modeling
- **Workspace:** `aptale-production`
- **Dialectic Tracking:** The agent will use the `query_user_context` tool to retrieve:
  - User's local timezone.
  - Preferred profit margins.
  - Historical logistics lanes (e.g., China -> Nigeria).
  - Risk tolerance and communication brevity preference.

---

## 5. Server Actions (Tool Mapping)

### 5.1 `delegate_task` (Parallel Sourcing)
- **Description:** Spawns isolated worker agents for data scraping.
- **Input Parameters:**
  ```json
  {
    "tasks":[
      {
        "goal": "Find freight costs from Guangzhou to Lagos for 500kg electronics.",
        "context": "JSON: {...}. Use browserbase to check standard Chinese forwarding portals.",
        "toolsets": ["browser", "web"]
      },
      ...
    ]
  }
  ```
- **Error Handling:** If a subagent times out or errors, the parent agent must catch the exception, inform the user ("Failed to fetch official freight rates due to portal timeout"), and offer a manual estimation path. No silent data hallucination.

### 5.2 `execute_code` (Landed Cost Engine)
- **Description:** Runs a sandboxed Python script to do deterministic math and file generation.
- **Script Constraints:**
  - Cannot access external APIs directly without using `from hermes_tools import web_search`.
  - Must write the PDF/CSV to `/workspace/` and print the exact absolute path to stdout.

---

## 6. Conversational UX & Design System

Since Aptale is WhatsApp-native, the UI is entirely text and media-based.

### 6.1 WhatsApp Markdown Standards
- **Headers:** Use bolding `*Header*`
- **Lists:** Use `- ` or `1. `
- **Data Points:** Use code blocks ` ``` ` for exact HS codes or numeric identifiers to make them easy for users to copy-paste.
- **Spacing:** Double line breaks between major sections (e.g., Freight vs. Customs).

### 6.2 Bot Personality (`SOUL.md`)
```markdown
# Aptale Persona

You are Aptale, an elite autonomous freight and customs broker. You speak directly to SMB importers on WhatsApp.

## Tone & Style
- Professional, concise, and highly accurate.
- Do not use flowery language. Time is money for merchants.
- Format all numeric breakdowns using clear WhatsApp markdown (bullet points and bold text).

## Operating Rules
- ALWAYS explicitly state when a cost is an estimate vs. an official government quote.
- If a user asks for a calculation, NEVER guess the HS code without confirming it via the `clarify` tool first.
- Attach the standard liability disclaimer to all finalized quotes.
```

---

## 7. Authentication & Authorization

### 7.1 End-User Access (MVP Phase)
- **Whitelist Enforcement:** Managed via `~/.hermes/.env`:
  ```bash
  WHATSAPP_ENABLED=true
  WHATSAPP_MODE=bot
  WHATSAPP_ALLOWED_USERS=15551234567,447123456789,2348012345678
  ```
- Any unauthorized number messaging the WhatsApp bot will be silently ignored by the Gateway.

### 7.2 Private Skill Hub Authentication
- The deployment environment must have `GITHUB_PERSONAL_ACCESS_TOKEN` exported.
- Add the tap via Hermes CLI before starting the gateway:
  `hermes skills tap add https://<token>@github.com/YourOrg/aptale-skills.git`

---

## 8. Data Privacy & Security

### 8.1 PII Redaction Hook
To ensure supplier names and invoice data are not leaked into server logs, implement a Hermes Event Hook.
- **Location:** `~/.hermes/hooks/pii-redactor/handler.py`
- **Logic:** Subscribes to `agent:step` and `agent:end`. Uses regex to sanitize strings resembling credit cards, exact street addresses, or proper supplier names from the `context` dictionary before writing to the local `activity.log`.

### 8.2 WhatsApp Session Monitoring Hook
- **Location:** `~/.hermes/hooks/whatsapp-monitor/handler.py`
- **Logic:** Subscribes to `gateway:startup` and `session:start`. If the Baileys session throws a disconnect exception, the hook makes an HTTP POST request to an admin alerting system (e.g., PagerDuty/Slack webhook) to notify the admin that a QR re-pairing is required.

---

## 9. Testing Strategy

### 9.1 Prompt & Skill Evaluation
- Use the `batch_runner.py` (Hermes Batch Processing) to evaluate the routing logic.
- **Dataset:** 100 sample JSON invoices (`data/eval_invoices.jsonl`).
- **Criteria:** Verify that `delegate_task` is called correctly 100% of the time, and that the subagents successfully return structured JSON.

### 9.2 Python Sandbox Tests
- Unit test the Python scripts that the LLM is expected to generate inside `execute_code`.
- Ensure standard libraries available in `python:3.11-slim` are sufficient for the PDF/CSV generation, or explicitly add dependencies via a custom Dockerfile configured in `terminal.docker_image`.

### 9.3 Gateway Resiliency
- Simulate network drops on the host machine to verify Baileys/WhatsApp automatic reconnection logic.
- Test the rate-limiting and authorization denial for non-whitelisted phone numbers.
```