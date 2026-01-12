#!/usr/bin/env bash
set -e

echo "--- [1/3] COMPILING HARDENED WASM ---"
bash ~/PrivateVault-Mega-Repo/scripts/compile-wasm.sh

echo "--- [2/3] SYNCING KUBERNETES CONFIGS ---"
# Ensure the wasm-config is up to date in the deployment folder
cp ~/PrivateVault-Mega-Repo/deployments/k8s/wasm-config.yaml ~/PrivateVault-Mega-Repo/deployments/k8s/active-config.yaml

echo "--- [3/3] PREPARING GITHUB PUSH ---"
cd ~/PrivateVault-Mega-Repo
git add .
git commit -m "feat: hardened binary policy execution with wasm"

echo ">>> SYSTEM READY FOR DEMO <<<"
