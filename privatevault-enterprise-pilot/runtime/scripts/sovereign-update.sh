#!/usr/bin/env bash
set -e

echo "--- [1/4] RETRIEVING SOURCE FROM VAULT ---"
cp ~/PrivateVault-Source-Vault/policy-v2.rego ~/PrivateVault-Mega-Repo/pkg/enforcement/policies/

echo "--- [2/4] COMPILING HARDENED BINARY ---"
~/PrivateVault-Mega-Repo/scripts/compile-wasm.sh

echo "--- [3/4] SANITIZING AND LOCKING IP ---"
bash ~/PrivateVault-Mega-Repo/scripts/sanitize-ip.sh

echo "--- [4/4] SYNCING GITHUB ---"
git add .
git commit -m "build: hardened sovereign update $(date +%Y%m%d-%H%M)"
git push origin main

echo ">>> UPDATE COMPLETE. LOGIC IS PROTECTED AND LIVE."
