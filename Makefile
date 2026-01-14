.PHONY: verify docs guard test gold

verify: docs guard test
	@echo "✅ VERIFY PASSED"

docs:
	@test -f docs/ARCHITECTURE.md || (echo "❌ Missing docs/ARCHITECTURE.md" && exit 1)
	@test -f docs/FAILURE_MODES.md || (echo "❌ Missing docs/FAILURE_MODES.md" && exit 1)
	@test -f docs/runbooks/RUNBOOK_E2E.md || (echo "❌ Missing docs/runbooks/RUNBOOK_E2E.md" && exit 1)
	@echo "✅ Docs OK"

guard:
	@./scripts/security-guard.sh

test:
	go test ./... -count=1

gold:
	@./scripts/test-gold.sh
