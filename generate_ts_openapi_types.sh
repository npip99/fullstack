#!/bin/bash
set -euo pipefail
error_handler() {
    echo "Error on line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
}
trap 'error_handler' ERR

if [[ -z "${VIRTUAL_ENV:-}" && -d ".venv" ]]; then
    source .venv/bin/activate
fi

OUTPUT_PATH="frontend/src/api_types.ts"

GENERATED="$(
{
python - <<'PY'
import json
from src.main import app

STRIP_KEYS = {
    "summary",
    "description",
    "title",
    "examples",
    "externalDocs",
    "deprecated",
}

def strip_metadata(x):
    if isinstance(x, dict):
        return {k: strip_metadata(v) for k, v in x.items() if k not in STRIP_KEYS}
    if isinstance(x, list):
        return [strip_metadata(v) for v in x]
    return x

spec = app.openapi()
spec = strip_metadata(spec)
spec["paths"] = {k: v for k, v in spec["paths"].items() if "post" in v}
print(json.dumps(spec))
PY
} \
| npx --prefix frontend openapi-typescript --stdin \
| npx --prefix frontend prettier --stdin-filepath "$OUTPUT_PATH"
)"

if [[ "${1:-}" == "--check" ]]; then
    diff <(printf '%s\n' "$GENERATED") "$OUTPUT_PATH" >/dev/null
else
    mkdir -p "$(dirname "$OUTPUT_PATH")"
    printf '%s\n' "$GENERATED" > "$OUTPUT_PATH"
fi
