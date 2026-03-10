#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

failures=0

run_check() {
  local name="$1"
  shift

  echo "[aptale check] ${name}"
  if "$@"; then
    echo "[aptale check] PASS: ${name}"
  else
    echo "[aptale check] FAIL: ${name}" >&2
    failures=$((failures + 1))
  fi
}

if ! command -v hermes >/dev/null 2>&1; then
  echo "[aptale check] FAIL: Hermes CLI is not installed or not on PATH." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "[aptale check] FAIL: Node.js is required for browser automation and WhatsApp bridge." >&2
  exit 1
fi

node_major="$(node -v | sed -E 's/^v([0-9]+).*/\1/')"
if [[ -z "${node_major}" ]] || (( node_major < 22 )); then
  echo "[aptale check] FAIL: Node.js v22+ is required. Current: $(node -v 2>/dev/null || echo unknown)" >&2
  exit 1
fi

run_check "Bootstrap directories" "${REPO_ROOT}/scripts/bootstrap_dirs.sh"
run_check "Hermes doctor" hermes doctor
run_check "Hermes config check" hermes config check
run_check "Hermes status" hermes status
run_check "Hermes gateway status" hermes gateway status

if (( failures > 0 )); then
  echo "[aptale check] Completed with ${failures} failure(s)." >&2
  exit 1
fi

echo "[aptale check] All checks passed."
