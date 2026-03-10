#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"

log() {
  printf '[aptale setup] %s\n' "$1"
}

fail() {
  printf '[aptale setup] ERROR: %s\n' "$1" >&2
  exit 1
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    fail "Missing required command: $1"
  fi
}

uname_s="$(uname -s)"
case "${uname_s}" in
  Linux|Darwin) ;;
  *)
    fail "Unsupported platform '${uname_s}'. Aptale setup supports Linux/macOS/WSL2."
    ;;
esac

if grep -qi 'microsoft' /proc/version 2>/dev/null; then
  log "WSL2 environment detected."
fi

require_cmd git

if ! command -v hermes >/dev/null 2>&1; then
  require_cmd curl
  log "Hermes CLI not found. Installing via official Hermes installer."
  curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
  export PATH="${HOME}/.local/bin:${PATH}"
fi

require_cmd hermes
require_cmd node

node_major="$(node -v | sed -E 's/^v([0-9]+).*/\1/')"
if [[ -z "${node_major}" ]]; then
  fail "Unable to detect Node.js version."
fi
if (( node_major < 22 )); then
  fail "Node.js v22+ is required for Browserbase browser tools and WhatsApp bridge."
fi

log "Bootstrapping runtime directories."
"${REPO_ROOT}/scripts/bootstrap_dirs.sh"

if [[ ! -f "${HERMES_HOME}/config.yaml" ]]; then
  fail "Hermes config not found at ${HERMES_HOME}/config.yaml. Copy or symlink hermes/config/config.yaml first."
fi

if [[ -f "${REPO_ROOT}/package.json" ]]; then
  log "Installing Node.js dependencies from package.json."
  (cd "${REPO_ROOT}" && npm install)
else
  log "No package.json found in repo; skipping npm install."
fi

if [[ -f "${REPO_ROOT}/requirements.txt" ]]; then
  log "Installing Python dependencies from requirements.txt."
  python3 -m pip install -r "${REPO_ROOT}/requirements.txt"
elif [[ -f "${REPO_ROOT}/pyproject.toml" ]]; then
  log "Installing Python dependencies from pyproject.toml."
  python3 -m pip install -e "${REPO_ROOT}"
else
  log "No Python dependency manifest found in repo; skipping Python dependency install."
fi

log "Running Hermes baseline checks."
hermes config check
hermes doctor

log "Local setup completed."
