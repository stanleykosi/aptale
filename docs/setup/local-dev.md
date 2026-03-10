# Aptale Local Development Setup

This guide covers local Aptale setup using the Step 6 operational scripts.

Supported operator environments:

- Linux
- macOS
- WSL2

## Prerequisites

- Hermes CLI installed and available on `PATH`
- Node.js v22+ installed
  - Hermes docs require Node.js for browser automation and the WhatsApp bridge.
- Aptale runtime env configured under `~/.hermes/.env`
- Hermes config present at `~/.hermes/config.yaml` (from `hermes/config/config.yaml`)

## Script Entry Points

- `scripts/setup_local.sh`
  - Bootstraps runtime directories
  - Installs Hermes CLI with the official Hermes installer when `hermes` is not present
  - Checks Hermes CLI and Node.js version requirements
  - Installs repo dependencies when dependency files are present
  - Runs `hermes config check` and `hermes doctor`
- `scripts/check_system.sh`
  - Runs runtime validation checks:
  - `hermes doctor`
  - `hermes config check`
  - `hermes status`
  - `hermes gateway status`
- `scripts/start_gateway.sh`
  - Starts Hermes gateway in foreground with Aptale runtime files
- `scripts/install_gateway_service.sh`
  - Installs Hermes gateway as a system service and prints service status

## Recommended Flow

1. Run local setup:

   ```bash
   ./scripts/setup_local.sh
   ```

2. Run full checks:

   ```bash
   ./scripts/check_system.sh
   ```

3. Start gateway in foreground (development):

   ```bash
   ./scripts/start_gateway.sh
   ```

4. Optional: install gateway as a service (operations):

   ```bash
   ./scripts/install_gateway_service.sh
   ```

## Hermes Notes Used By This Setup

- `hermes doctor` is the primary diagnostics command.
- `hermes config check` validates config compatibility.
- `hermes gateway` runs messaging and cron in foreground.
- `hermes gateway install` installs a long-running service on Linux/macOS.
