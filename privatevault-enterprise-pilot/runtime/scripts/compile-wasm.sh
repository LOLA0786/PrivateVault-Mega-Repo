#!/usr/bin/env bash
set -e

echo "--- STARTING BINARY HARDENING (REGO -> WASM) ---"

# The entrypoint must match the 'package' line in your .rego file
# Current package: envoy.authz -> entrypoint: envoy/authz/allow
~/.local/bin/opa build -t wasm -e 'envoy/authz/allow' ~/PrivateVault-Mega-Repo/pkg/enforcement/policies/

# Move bundle to the hardened path
mv bundle.tar.gz ~/PrivateVault-Mega-Repo/pkg/enforcement/policies/policy-hardened.wasm.tar.gz

echo ">>> SUCCESS: Binary policy created at pkg/enforcement/policies/policy-hardened.wasm.tar.gz"
