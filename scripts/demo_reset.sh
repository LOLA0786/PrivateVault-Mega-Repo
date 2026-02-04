#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_ROOT="${REPO_ROOT}/.demo"

ROOT="${1:-$DEFAULT_ROOT}"
ROOT_REAL="$(cd "${ROOT}" 2>/dev/null && pwd || true)"

if [[ -z "${ROOT_REAL}" ]]; then
  echo "demo root not found: ${ROOT}" >&2
  exit 1
fi

if [[ "${ROOT_REAL}" != "${REPO_ROOT}"/* && "${ROOT_REAL}" != "${DEFAULT_ROOT}" && "${ROOT_REAL}" != "/var/lib/privatevault/demo"* ]]; then
  echo "refusing to delete outside allowed demo roots" >&2
  exit 1
fi

rm -rf "${ROOT_REAL}"

echo "demo reset complete: ${ROOT_REAL}"
