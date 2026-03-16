# Aptale

Aptale is an autonomous **AI Freight & Customs Broker** built on the [Hermes Agent framework](https://github.com/NousResearch/hermes-agent). Designed for SMBs and global importers, Aptale operates exclusively via **WhatsApp** to automate cross-border trade workflows.

It ingests invoices, scrapes live customs/freight/FX data using parallel subagents, calculates landed costs, and provides proactive market alerts—all within a single conversational thread.

---

## Key Features

- **WhatsApp-Native Interaction:** No external dashboards; manage your entire supply chain through WhatsApp DMs.
- **Multilingual Vision Ingestion:** Upload photos of invoices (Chinese, Turkish, etc.); Aptale translates and extracts line items automatically.
- **Parallel Data Sourcing:** Spawns specialized subagents to scrape government customs portals, shipping rates, and parallel FX markets in real-time.
- **Landed Cost Engine:** Deterministic Python-based calculation of duties, freight, and margins with formatted PDF/CSV exports.
- **Autonomous Monitoring:** Schedule daily market checks and receive alerts when arbitrage windows (FX/shipping) open.
- **Private Skill Extensibility:** Custom regional routing and business logic delivered via a private GitHub skills tap.

---

## Architecture At A Glance

- **Core Agent Runtime:** [Hermes Agent](https://github.com/NousResearch/hermes-agent) (Python 3.11+)
- **Messaging Surface:** WhatsApp via Hermes' built-in Baileys bridge (Node.js 22+)
- **Web Sourcing:** [Browserbase](https://browserbase.com/)-backed browser workflows with stealth proxies.
- **Memory & State:** SQLite-backed Hermes memory augmented with [Honcho](https://honcho.dev/) for deep user profiling.
- **Sourcing Engine:** Parallel delegation via `delegate_task` for high-throughput data gathering.

---

## Local Installation

### Prerequisites

- **OS:** Linux, macOS, or WSL2.
- **Python:** 3.11 or higher.
- **Node.js:** v22.x or higher (v25 recommended via `nvm`).
- **Hermes CLI:** Installed (the setup script will handle this if missing).

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/stanleykosi/aptale.git
   cd aptale
   ```

2. **Run the local setup script:**
   This script bootstraps runtime directories, installs the Hermes CLI, checks versions, and prepares the environment.
   ```bash
   ./scripts/setup_local.sh
   ```

3. **Verify the installation:**
   ```bash
   ./scripts/check_system.sh
   ```

---

## Configuration

Aptale relies on the Hermes runtime configuration located in `~/.hermes/`.

### 1. Environment Variables
Copy the example environment file and fill in your secrets:
```bash
cp .env.example ~/.hermes/.env
```
**Required Secrets:**
- `OPENROUTER_API_KEY`: For LLM orchestration (Claude 3.5 Sonnet recommended).
- `BROWSERBASE_API_KEY` & `PROJECT_ID`: For web scraping resilience.
- `HONCHO_API_KEY`: For cross-session memory.
- `GITHUB_PERSONAL_ACCESS_TOKEN`: For private skills tap access.

### 2. Provider Config
Copy the Aptale-optimized Hermes config:
```bash
cp hermes/config/config.yaml ~/.hermes/config.yaml
```

### 3. Install Private Skills
Aptale uses specialized skills for regional routing. Add your private tap:
```bash
./scripts/install_skills_tap.sh --repo owner/repo
```

---

## Running Aptale

### Starting the Gateway
To start the WhatsApp bridge and agent runtime in the foreground:
```bash
./scripts/start_gateway.sh
```

### WhatsApp Pairing
1. Once started, a QR code will appear in your terminal.
2. Open WhatsApp on your phone -> **Linked Devices** -> **Link a Device**.
3. Scan the terminal QR code.
4. Once paired, you can message the bot number directly.

### Running as a Service (Linux/macOS)
To run Aptale in the background as a system service:
```bash
./scripts/install_gateway_service.sh
```

---

## Repository Layout

```text
aptale/
├── src/                # Core Python logic and agent extensions
├── scripts/            # Operational scripts (setup, start, install)
├── hermes/             # Default Hermes configuration templates
├── docs/               # Technical specs, architecture, and ADRs
├── aptale-skills/      # Local skill definitions (synced from tap)
├── runtime/            # Generated exports (PDF/CSV) and logs
├── tests/              # Pytest suite for core logic
└── fixtures/           # Mock data for testing and development
```

---

## Development & Skills

### Syncing Local Skills
If you are developing custom logic inside the `aptale-skills/` directory, you can sync your changes to the active Hermes runtime without a full tap update:
```bash
./scripts/sync_local_skill.sh
```

### Prompt Engineering
Aptale's personality and operational boundaries are defined in `SOUL.md`. For deep customization, modify the prompt templates in the `aptale-skills/` directory and re-sync.

---

## Hard-Cut Policy

Aptale operates on a **Single Canonical Path** philosophy:
- **No Migration Shims:** We optimize for the current state.
- **Fail-Fast Diagnostics:** If a data source or portal changes, the system informs the user explicitly rather than guessing or hallucinating.
- **Transparency:** All automated actions are grounded in verifiable sources provided in the chat.

---

## License & Attribution

built with love by [stanleykosi](https://github.com/stanleykosi) as part of the Aptale Project.
Powered by [Hermes Agent](https://github.com/NousResearch/hermes-agent).
