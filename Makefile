run:
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

	@echo "============================================================="
	@echo "🔄 TEST: Multi-Agent Workflow"
	@echo "============================================================="
	python3 multi_agent_workflow.py

	@echo "============================================================="
	@echo "🧪 TEST: Sandbox Simulation"
	@echo "============================================================="
	python3 sandbox_simulation.py

	@echo "============================================================="
	@echo "📈 GENERATE: CISO Dashboard"
	@echo "============================================================="
	python3 -c "from ciso_dashboard_report import generate_report; generate_report(); print('✅ Dashboard generated')"
