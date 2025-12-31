#!/bin/bash
set -euo pipefail
error_handler() {
    echo "Error on line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
}
trap 'error_handler' ERR

if [[ -z "${VIRTUAL_ENV:-}" && -d ".venv" ]]; then
    source .venv/bin/activate
fi

if [[ "${1:-}" == "--check" ]]; then
    ruff check .
    basedpyright
    ruff format --check
    ./generate_ts_openapi_types.sh --check
    cd frontend
    npm run lint
else
    ruff check --fix .
    basedpyright
    ruff format
    ./generate_ts_openapi_types.sh
    cd frontend
    npm run lint:fix
fi
