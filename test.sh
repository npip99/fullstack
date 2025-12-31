#!/bin/bash
set -euo pipefail
error_handler() {
    echo "Error on line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
}
trap 'error_handler' ERR

if [[ -z "${VIRTUAL_ENV:-}" && -d ".venv" ]]; then
    source .venv/bin/activate
fi

if [[ "${1:-}" == "--verbose" ]]; then
    # -rP so that stdout shows even in cases of success
    # https://github.com/pytest-dev/pytest/issues/11731
    pytest -rP
else
    pytest -W "ignore::PendingDeprecationWarning:starlette.*:"
fi
