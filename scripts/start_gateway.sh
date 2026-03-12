#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"
NVM_DIR="${NVM_DIR:-${HOME}/.nvm}"
APTALE_NODE_VERSION="${APTALE_NODE_VERSION:-25}"
APTALE_MIN_NODE_MAJOR="${APTALE_MIN_NODE_MAJOR:-20}"

fail() {
  printf '[aptale gateway] ERROR: %s\n' "$1" >&2
  exit 1
}

if ! command -v hermes >/dev/null 2>&1; then
  fail "Hermes CLI is not installed or not on PATH."
fi

HERMES_BIN="$(command -v hermes)"
HERMES_PYTHON="$(head -n 1 "${HERMES_BIN}" | sed -e 's/^#!//')"
if [[ -z "${HERMES_PYTHON}" || ! -x "${HERMES_PYTHON}" ]]; then
  fail "Unable to resolve Hermes Python runtime from ${HERMES_BIN}."
fi

if [[ -s "${NVM_DIR}/nvm.sh" ]]; then
  # shellcheck source=/dev/null
  . "${NVM_DIR}/nvm.sh"
  if ! nvm use "${APTALE_NODE_VERSION}" >/dev/null 2>&1; then
    fail "Node ${APTALE_NODE_VERSION} is not available in nvm. Run: nvm install ${APTALE_NODE_VERSION}"
  fi
else
  printf '[aptale gateway] WARN: %s\n' "Missing ${NVM_DIR}/nvm.sh; continuing without nvm." >&2
fi

if ! command -v node >/dev/null 2>&1; then
  fail "Node.js is not installed or not on PATH."
fi

NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
if (( NODE_MAJOR < APTALE_MIN_NODE_MAJOR )); then
  fail "Node.js $(node -v) is too old. Need >=${APTALE_MIN_NODE_MAJOR}. Set nvm version with: nvm use ${APTALE_NODE_VERSION}"
fi

if [[ ! -f "${HERMES_HOME}/config.yaml" ]]; then
  fail "Missing ${HERMES_HOME}/config.yaml. Copy or symlink ${REPO_ROOT}/hermes/config/config.yaml."
fi

if [[ ! -f "${HERMES_HOME}/.env" ]]; then
  printf '[aptale gateway] WARN: %s\n' "Missing ${HERMES_HOME}/.env; continuing with current process environment." >&2
else
  # Load Hermes runtime env before gateway starts so STT/TTS keys are available
  # to pre-agent audio handling paths.
  set -a
  set +u
  # shellcheck source=/dev/null
  . "${HERMES_HOME}/.env"
  set -u
  set +a
fi

export APTALE_REPO_ROOT="${APTALE_REPO_ROOT:-${REPO_ROOT}}"
export MESSAGING_CWD="${MESSAGING_CWD:-${REPO_ROOT}}"
export APTALE_QUOTE_LOOP_ENABLED="${APTALE_QUOTE_LOOP_ENABLED:-true}"
export APTALE_SCOPE_ENFORCE="${APTALE_SCOPE_ENFORCE:-false}"
export APTALE_HERMES_BRIDGE_PATCH="${APTALE_HERMES_BRIDGE_PATCH:-true}"
export APTALE_LOCAL_STT_ENABLED="${APTALE_LOCAL_STT_ENABLED:-true}"
export APTALE_STT_PROVIDER="${APTALE_STT_PROVIDER:-local}"
export APTALE_STT_MODEL="${APTALE_STT_MODEL:-small}"
export APTALE_STT_DEVICE="${APTALE_STT_DEVICE:-auto}"
export APTALE_STT_COMPUTE_TYPE="${APTALE_STT_COMPUTE_TYPE:-int8}"
export APTALE_STT_BEAM_SIZE="${APTALE_STT_BEAM_SIZE:-1}"
export APTALE_AUDIO_IN_AUDIO_OUT="${APTALE_AUDIO_IN_AUDIO_OUT:-true}"
export APTALE_AUDIO_REPLY_MODE="${APTALE_AUDIO_REPLY_MODE:-audio_only}"
export ORT_LOG_SEVERITY_LEVEL="${ORT_LOG_SEVERITY_LEVEL:-3}"
export HERMES_TOOL_PROGRESS_MODE="${HERMES_TOOL_PROGRESS_MODE:-off}"
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

if [[ "${APTALE_LOCAL_STT_ENABLED}" =~ ^(1|true|yes|on)$ ]] && [[ "${APTALE_STT_PROVIDER}" != "openai" ]]; then
  if ! "${HERMES_PYTHON}" -m pip --version >/dev/null 2>&1; then
    echo "[aptale gateway] Bootstrapping pip in Hermes runtime..."
    "${HERMES_PYTHON}" -m ensurepip --upgrade >/dev/null 2>&1 \
      || fail "Failed to bootstrap pip for Hermes runtime (${HERMES_PYTHON})."
  fi
  if ! "${HERMES_PYTHON}" - <<'PY'
import importlib.util
import sys
sys.exit(0 if importlib.util.find_spec("faster_whisper") else 1)
PY
  then
    echo "[aptale gateway] Installing faster-whisper for local voice transcription..."
    "${HERMES_PYTHON}" -m pip install --disable-pip-version-check --quiet "faster-whisper>=1.1.0,<2" \
      || fail "Failed to install faster-whisper into Hermes runtime (${HERMES_PYTHON})."
  fi
fi

APTALE_BRIDGE_SOURCE="${REPO_ROOT}/scripts/whatsapp_bridge.js"
APTALE_BRIDGE_TARGET="${HERMES_HOME}/hermes-agent/scripts/whatsapp-bridge/bridge.js"
if [[ -f "${APTALE_BRIDGE_SOURCE}" && -f "${APTALE_BRIDGE_TARGET}" ]]; then
  cp "${APTALE_BRIDGE_SOURCE}" "${APTALE_BRIDGE_TARGET}"
elif [[ -f "${APTALE_BRIDGE_SOURCE}" ]]; then
  printf '[aptale gateway] WARN: %s\n' "Bridge target missing at ${APTALE_BRIDGE_TARGET}; skipping Aptale bridge sync." >&2
fi

cd "${REPO_ROOT}"

echo "[aptale gateway] Node $(node -v) at $(command -v node)"
echo "[aptale gateway] Starting Hermes gateway in foreground."
exec hermes gateway
