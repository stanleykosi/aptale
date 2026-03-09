#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"

directories=(
  "${HERMES_HOME}"
  "${HERMES_HOME}/cron"
  "${HERMES_HOME}/sessions"
  "${HERMES_HOME}/logs"
  "${HERMES_HOME}/memories"
  "${HERMES_HOME}/skills"
  "${HERMES_HOME}/pairing"
  "${HERMES_HOME}/hooks"
  "${HERMES_HOME}/image_cache"
  "${HERMES_HOME}/audio_cache"
  "${HERMES_HOME}/whatsapp/session"
  "${REPO_ROOT}/runtime/exports"
  "${REPO_ROOT}/runtime/exports/pdf"
  "${REPO_ROOT}/runtime/exports/csv"
)

for directory in "${directories[@]}"; do
  mkdir -p "${directory}"
done

echo "Bootstrapped Aptale directories:"
printf ' - %s\n' "${directories[@]}"
