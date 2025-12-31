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

# Dependencies
if [[ "$OSTYPE" =~ ^darwin ]]; then
  brew install yq uv python@3.12 postgresql
else
  sudo apt-get update
  sudo snap install yq
  sudo snap install --classic astral-uv
  sudo apt-get install -y python3-pip python3.12-venv
  sudo apt-get install -y postgresql postgresql-contrib
fi

# Python Setup
uv sync
source .venv/bin/activate

echo
echo "Python Setup Done!"
echo

# Setup Frontend

cd frontend

if ! command -v nvm &> /dev/null; then
  if [[ "$OSTYPE" =~ ^darwin ]]; then
    brew install nvm
    export NVM_DIR="$HOME/.nvm"
    mkdir -p "$NVM_DIR"
    [ -s "$(brew --prefix nvm)/nvm.sh" ] && \. "$(brew --prefix nvm)/nvm.sh"
  else
    wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  fi
fi
nvm install --lts

npm i
npm run build

cd ..
echo
echo "Frontend Setup Done!"
echo

# Get credentials from toml
POSTGRES_HOST=$(yq '.database.host' ./credentials/credentials.toml)
POSTGRES_USER=$(yq '.database.username' ./credentials/credentials.toml)
POSTGRES_PASSWORD=$(yq '.database.password' ./credentials/credentials.toml)
POSTGRES_DB=$(yq '.database.dbname' ./credentials/credentials.toml)

# Setup postgres, if running on localhost
if [[ "$POSTGRES_HOST" == "localhost" ]]; then
  if [[ "$OSTYPE" =~ ^darwin ]]; then
    brew services start postgresql
    psql postgres -c "CREATE USER $POSTGRES_USER WITH SUPERUSER PASSWORD '$POSTGRES_PASSWORD';"
  else
    sudo systemctl start postgresql
    sudo -iu postgres psql -c "ALTER USER $POSTGRES_USER PASSWORD '$POSTGRES_PASSWORD';"
  fi
fi

# Initialize the database
psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432" -c "CREATE DATABASE $POSTGRES_DB;"
alembic upgrade head

echo
echo "PostgreSQL Setup Done!"
echo
