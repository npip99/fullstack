#!/bin/bash
set -euo pipefail
error_handler() {
    echo "Error on line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
}
trap 'error_handler' ERR

if [[ ! -f credentials/credentials.toml ]]; then
  echo "Error: credentials.toml not found. Please create it with the necessary API keys."
  exit 1
fi

POSTGRES_HOST="$(yq '.database.host' ./credentials/credentials.toml)"
POSTGRES_USER="$(yq '.database.username' ./credentials/credentials.toml)"
POSTGRES_PASSWORD="$(yq '.database.password' ./credentials/credentials.toml)"
POSTGRES_DB="$(yq '.database.dbname' ./credentials/credentials.toml)"

psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_DB" "$@"
