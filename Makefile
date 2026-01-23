.PHONY: help lint test verify verify2 verify3 run clean

help:
	@echo "Targets:"
	@echo "  make run      - full pipeline (lint + tests + dashboard)"
	@echo "  make verify   - lint + core tests"
	@echo "  make verify2  - verify + multi-agent + sandbox"
	@echo "  make verify3  - verify2 + dashboard"
	@echo "  make clean    - delete generated artifacts"

lint:
	@echo "============================================================="
	@echo "🔎 Lint (syntax check)"
	@echo "============================================================="
	python3 -m py_compile \
		ai_firewall_core.py \
		tool_authorization.py \
		drift_detection_fixed.py \
		decision_ledger.py \
		multi_agent_workflow.py \
		sandbox_simulation.py \
		compliance_mapper.py \
		ciso_dashboard_report.py
	@echo "✅ Python compile OK"

test:
	@echo "============================================================="
	@echo "🔥 TEST: Core firewall"
	@echo "============================================================="
	python3 ai_firewall_core.py

	@echo "============================================================="
	@echo "🔐 TEST: Tool authorization"
	@echo "============================================================="
	python3 tool_authorization.py

	@echo "============================================================="
	@echo "📊 TEST: Drift detection"
	@echo "============================================================="
	python3 drift_detection_fixed.py

	@echo "============================================================="
	@echo "📝 TEST: Decision ledger"
	@echo "============================================================="
	python3 decision_ledger.py

verify: lint test
	@echo "✅ verify complete"

verify2: verify
	@echo "============================================================="
	@echo "🔄 TEST: Multi-Agent Workflow"
	@echo "============================================================="
	python3 multi_agent_workflow.py

	@echo "============================================================="
	@echo "🧪 TEST: Sandbox Simulation"
	@echo "============================================================="
	python3 sandbox_simulation.py

	@echo "✅ verify2 complete"

verify3: verify2
	@echo "============================================================="
	@echo "📈 GENERATE: CISO Dashboard"
	@echo "============================================================="
	python3 -c "from ciso_dashboard_report import generate_report; generate_report(); print('✅ Dashboard generated')"
	@echo "✅ verify3 complete"

run: verify3
	@echo "✅ Full run complete"

clean:
	rm -f audit_report.json
	rm -f ai_firewall_ledger.jsonl
	rm -f *.pyc
	rm -rf __pycache__
	@echo "🧹 Clean complete"
