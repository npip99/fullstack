#!/bin/bash
set -euo pipefail
error_handler() {
    echo "Error on line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
}
trap 'error_handler' ERR

# screen args
if [[ "$OSTYPE" =~ ^darwin ]]; then
    SCREENARGS=""
else
    SCREENARGS="-Logfile backend.log"
fi

# run.sh arguments
RUNARGS=()
if [[ "${1:-}" == "--prod" ]]; then
    RUNARGS=(--prod)
fi

screen -dmS backend -L "${LOGARG[@]}" bash -c "stdbuf -oL ./run.sh ${RUNARGS[*]}"
screen -S backend -X logfile flush 0
