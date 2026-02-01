PYTHON ?= python3

.PHONY: verify verify_all evidence_manifest bundle_export clean_reports

verify:
	@$(PYTHON) scripts/verify.py

evidence_manifest:
	@$(PYTHON) scripts/verify_evidence_hashchain.py

bundle_export:
	@$(PYTHON) scripts/verify_bundle_export.py

verify_all: verify evidence_manifest bundle_export
	@echo "✅ VERIFY_ALL COMPLETE (tests + evidence + bundle)"

clean_reports:
	@rm -rf reports/vv privatevault/reports/evidence/*.jsonl
	@mkdir -p reports/vv privatevault/reports/evidence
