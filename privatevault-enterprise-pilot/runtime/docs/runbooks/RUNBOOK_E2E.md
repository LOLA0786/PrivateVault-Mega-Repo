# RUNBOOK: Gold E2E Test

## Run
./scripts/test-gold.sh

## Expected
- GET / => 200 OK
- POST /delete => 403 Forbidden (delete_denied_by_policy)
- ext_authz ok/denied stats increment

## If failure
See docs/FAILURE_MODES.md
