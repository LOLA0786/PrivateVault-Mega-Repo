#!/usr/bin/env bash
set -euo pipefail

SPEC="sdk/openapi/openapi.json"
OUT="sdk/python/privatevault_sdk/generated"

if ! command -v openapi-generator >/dev/null 2>&1; then
  echo "openapi-generator not installed" >&2
  exit 1
fi

openapi-generator generate -g python -i "${SPEC}" -o "${OUT}" \
  --package-name privatevault_sdk_generated
