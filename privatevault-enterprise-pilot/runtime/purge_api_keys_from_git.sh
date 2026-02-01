#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "🚨 Purging api_keys.json from git history..."

# Ensure git-filter-repo exists
python3 -m pip install --user -q git-filter-repo

# Remove api_keys.json from all history
git filter-repo --path api_keys.json --invert-paths

echo "✅ History rewritten locally."
echo "Checking if file still exists in history..."

if git log -- api_keys.json >/dev/null 2>&1; then
  echo "❌ Still found in history (unexpected)."
  exit 1
else
  echo "✅ api_keys.json is gone from history."
fi

echo "Adding ignore rules..."
grep -q "^api_keys.json$" .gitignore 2>/dev/null || cat >> .gitignore <<'EOG'

# Secrets
api_keys.json
*.env
.env
EOG

git add .gitignore
git commit -m "SECURITY: remove secrets from history + ignore secrets" || true

echo "🚨 Force pushing rewritten history to origin..."
git push origin --force --all
git push origin --force --tags

echo "✅ Done. Remote history rewritten."
