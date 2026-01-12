#!/usr/bin/env bash
set -e

echo "--- [SHIELD] STARTING IP SANITIZATION ---"

# 1. Create a 'Vault' directory for your source code (not to be pushed)
mkdir -p ~/PrivateVault-Source-Vault

# 2. Move all human-readable Rego and Policy files to the Vault
find . -name "*.rego" -exec mv {} ~/PrivateVault-Source-Vault/ \;

# 3. Ensure the .gitignore prevents accidental leakage of source code
if ! grep -q "*.rego" .gitignore; then
  echo "*.rego" >> .gitignore
  echo "policy-v2.rego" >> .gitignore
  echo ".rego" >> .gitignore
fi

echo ">>> SUCCESS: Human-readable source code moved to ~/PrivateVault-Source-Vault"
echo ">>> SUCCESS: .gitignore updated to prevent IP leakage."
