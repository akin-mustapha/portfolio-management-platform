#!/usr/bin/env bash
# Start a Prefect process worker against the local API (default http://127.0.0.1:4200/api).
# Workers require PREFECT_API_URL; this script sets it if unset.
#
# Usage (from repo root):
#   bash scripts/prefect_worker_local.sh start --pool asset-monitoring-pool --work-queue default
#
# Ensure `prefect server start` is running elsewhere, or use scripts/deploy/prefect_deploy.sh.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  source venv/bin/activate
fi

export PREFECT_API_URL="${PREFECT_API_URL:-http://127.0.0.1:4200/api}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

exec prefect worker "$@"
