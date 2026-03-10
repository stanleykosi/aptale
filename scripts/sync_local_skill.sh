#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"
SOURCE_SKILL_DIR="${REPO_ROOT}/aptale-skills"
TARGET_SKILL_DIR="${HERMES_HOME}/skills/aptale/aptale-master-router"

log() {
  printf '[aptale skill sync] %s\n' "$1"
}

fail() {
  printf '[aptale skill sync] ERROR: %s\n' "$1" >&2
  exit 1
}

if [[ ! -d "${SOURCE_SKILL_DIR}" ]]; then
  fail "Source skill directory not found: ${SOURCE_SKILL_DIR}"
fi

if [[ ! -f "${SOURCE_SKILL_DIR}/SKILL.md" ]]; then
  fail "Source skill is missing SKILL.md: ${SOURCE_SKILL_DIR}/SKILL.md"
fi

mkdir -p "${TARGET_SKILL_DIR}"

if ! command -v rsync >/dev/null 2>&1; then
  fail "rsync is required but not found on PATH."
fi

log "Syncing ${SOURCE_SKILL_DIR} -> ${TARGET_SKILL_DIR}"
rsync -a --delete "${SOURCE_SKILL_DIR}/" "${TARGET_SKILL_DIR}/"

log "Sync completed."

if command -v hermes >/dev/null 2>&1; then
  skills_list_output="$(hermes skills list --source all 2>/dev/null || true)"
  if printf '%s\n' "${skills_list_output}" | grep -q "aptale-master-router"; then
    log "Verified: aptale-master-router is visible to Hermes."
  else
    log "Warning: sync completed, but aptale-master-router was not listed by Hermes."
  fi
fi
