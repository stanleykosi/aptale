#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"
SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"
SERVICE_PATH="${SYSTEMD_USER_DIR}/hermes-gateway.service"

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

mkdir -p "${SYSTEMD_USER_DIR}"

cat > "${SERVICE_PATH}" <<EOF
[Unit]
Description=Hermes Agent Gateway - Aptale Launcher
After=network.target

[Service]
Type=simple
WorkingDirectory=${REPO_ROOT}
Environment=HOME=${HOME}
Environment=PATH=${HOME}/.local/bin:${HOME}/.nvm/versions/node/v25.0.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/usr/bin/env bash ${REPO_ROOT}/scripts/start_gateway.sh
ExecStop=/bin/kill -SIGTERM \$MAINPID
Restart=on-failure
RestartSec=10
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=45
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

echo "[aptale gateway service] Reloading user systemd daemon."
systemctl --user daemon-reload

echo "[aptale gateway service] Enabling service."
systemctl --user enable hermes-gateway.service >/dev/null

echo "[aptale gateway service] Restarting service."
systemctl --user restart hermes-gateway.service

echo "[aptale gateway service] Current service status:"
systemctl --user status hermes-gateway.service --no-pager
