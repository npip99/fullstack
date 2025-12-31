#!/bin/bash
set -euo pipefail
error_handler() {
    echo "Error on line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
}
trap 'error_handler' ERR

if [[ -z "${VIRTUAL_ENV:-}" && -d ".venv" ]]; then
    source .venv/bin/activate
fi

export PYTHONUNBUFFERED=1
UVICORN_PORT=8080
if [[ "${1:-}" == "--prod" ]]; then
    # Reload can cause issues, so we don't run it in production
    # Also, we use localhost so that it's not accessible except via the loadbalancer
    uvicorn src.main:app --proxy-headers --host localhost --port "$UVICORN_PORT"
else
    uvicorn src.main:app --proxy-headers --host 0.0.0.0 --port "$UVICORN_PORT" --reload --reload-dir src
fi
