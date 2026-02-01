#!/usr/bin/env bash
echo "--- PRE-DEMO SANITIZATION START ---"
# Remove any leftover bundle files in the root
rm -f ~/PrivateVault-Mega-Repo/bundle.tar.gz
# Ensure the policies folder only has the binary wasm
find ~/PrivateVault-Mega-Repo/pkg/enforcement/policies/ -type f ! -name '*.wasm.tar.gz' -delete
echo ">>> REPO IS CLEAN AND PRODUCTION-READY."
