#!/usr/bin/env bash
set -euo pipefail

SPEC="sdk/openapi/openapi.json"
OUT="sdk/node/src/generated/openapi-types.d.ts"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not available" >&2
  exit 1
fi

npx openapi-typescript "${SPEC}" --output "${OUT}"
