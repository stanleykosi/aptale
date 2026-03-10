#!/usr/bin/env bash

set -euo pipefail

HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"

fail() {
  printf '[aptale gateway service] ERROR: %s\n' "$1" >&2
  exit 1
}

if ! command -v hermes >/dev/null 2>&1; then
  fail "Hermes CLI is not installed or not on PATH."
fi

if [[ ! -f "${HERMES_HOME}/config.yaml" ]]; then
  fail "Missing ${HERMES_HOME}/config.yaml."
fi

echo "[aptale gateway service] Installing Hermes gateway service."
hermes gateway install

echo "[aptale gateway service] Current service status:"
hermes gateway status
