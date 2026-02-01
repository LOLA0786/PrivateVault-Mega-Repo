#!/usr/bin/env bash
set -euo pipefail

echo "[guard] scanning for forbidden policy sources (.rego) ..."
if find . -name "*.rego" | grep -q . ; then
  echo "❌ FORBIDDEN: .rego sources found in repo:"
  find . -name "*.rego"
  exit 1
fi
echo "✅ no rego sources found"

echo "[guard] scanning for obvious secrets ..."
BAD=$(git ls-files | egrep -i '(\.env$|id_rsa|id_ed25519|\.pem$|\.key$|credentials|secret|token|kubeconfig|service-account|\.p12$)' || true)
if [[ -n "${BAD}" ]]; then
  echo "❌ Potential secret/key files tracked by git:"
  echo "${BAD}"
  exit 1
fi
echo "✅ no obvious secrets tracked"
