#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"

fail() {
  printf '[aptale gateway] ERROR: %s\n' "$1" >&2
  exit 1
}

if ! command -v hermes >/dev/null 2>&1; then
  fail "Hermes CLI is not installed or not on PATH."
fi

if [[ ! -f "${HERMES_HOME}/config.yaml" ]]; then
  fail "Missing ${HERMES_HOME}/config.yaml. Copy or symlink ${REPO_ROOT}/hermes/config/config.yaml."
fi

if [[ ! -f "${HERMES_HOME}/.env" ]]; then
  fail "Missing ${HERMES_HOME}/.env. Create it with required Aptale runtime variables."
fi

echo "[aptale gateway] Starting Hermes gateway in foreground."
exec hermes gateway
