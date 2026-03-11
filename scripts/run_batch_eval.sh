#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

DATASET_FILE="${APTALE_BATCH_ROUTING_DATASET:-${REPO_ROOT}/data/eval_invoices.jsonl}"
METRICS_FILE="${APTALE_BATCH_ROUTING_METRICS_PATH:-${REPO_ROOT}/runtime/evals/batch_routing_metrics.json}"

if [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "[aptale batch eval] ERROR: python3 is required." >&2
  exit 1
fi

if [[ ! -f "${DATASET_FILE}" ]]; then
  echo "[aptale batch eval] ERROR: dataset file not found: ${DATASET_FILE}" >&2
  exit 1
fi

mkdir -p "$(dirname "${METRICS_FILE}")"

echo "[aptale batch eval] Dataset: ${DATASET_FILE}"
echo "[aptale batch eval] Metrics output: ${METRICS_FILE}"
echo "[aptale batch eval] Running routing evaluation harness..."

APTALE_BATCH_ROUTING_DATASET="${DATASET_FILE}" \
APTALE_BATCH_ROUTING_METRICS_PATH="${METRICS_FILE}" \
"${PYTHON_BIN}" -m pytest -q "${REPO_ROOT}/tests/evals/test_batch_routing.py" "$@"

echo "[aptale batch eval] Completed. Metrics written to ${METRICS_FILE}"
