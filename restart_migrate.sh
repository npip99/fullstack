#!/bin/bash
set -euo pipefail
error_handler() {
    echo "Error on line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
}
trap 'error_handler' ERR

# Parse args
PROD=0
RESET_DB=0
for arg in "$@"; do
    if [[ "$arg" == "--prod" ]]; then
        PROD=1
    fi
    if [[ "$arg" == "--reset-db" ]]; then
        RESET_DB=1
    fi
done

if [[ -z "${VIRTUAL_ENV:-}" && -d ".venv" ]]; then
    source .venv/bin/activate
fi

# Kill the current backend, if it exists
pkill -2 -f "src.main:app" || true
while (screen -list || true) | grep -q "backend"; do
    sleep 0.1
done

# Sync requirements
uv sync

# Upgrade database
if [[ "$RESET_DB" -eq 1 ]]; then
    POSTGRES_HOST="$(yq '.database.host' ./credentials/credentials.toml)"
    POSTGRES_USER="$(yq '.database.username' ./credentials/credentials.toml)"
    POSTGRES_PASSWORD="$(yq '.database.password' ./credentials/credentials.toml)"
    POSTGRES_DB="$(yq '.database.dbname' ./credentials/credentials.toml)"
    psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432" -c "DROP DATABASE IF EXISTS $POSTGRES_DB WITH (FORCE);"
    psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432" -c "CREATE DATABASE $POSTGRES_DB;"
fi
alembic upgrade head

# Run backend
if [[ "$PROD" -eq 1 ]]; then
    ./run_bg.sh --prod
else
    ./run_bg.sh
fi
