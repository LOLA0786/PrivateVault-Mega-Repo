# PrivateVault Demo / Onboarding Pack (February 2026)

This pack lets new users spin up a realistic, safe demo in under 10 minutes. All data is synthetic and scoped to a demo tenant for **February 2026**.

**What You Get**
1. Sample tenant configuration
2. Sample quorum rules (Quorum v2)
3. Sample context keys (fake)
4. Preloaded audit events (Feb 1–Feb 28, 2026)
5. Fake approvals
6. Demo policies
7. Bootstrap + reset scripts

**Safety Guarantees**
1. No secrets in the demo assets
2. No production paths touched
3. Output restricted to demo root

## Quick Start (Under 10 Minutes)

**1) Bootstrap the demo pack**
```bash
python scripts/demo_bootstrap.py --demo-mode
```

This creates a demo root at `./.demo` and writes an env file at `./.demo/.env.demo`.

**2) Load demo environment**
```bash
source .demo/.env.demo
```

**3) Start the control plane**
Run your app normally (from repo root or from `.demo`). The demo uses:
- `PV_AUDIT_LOG_PATH` -> `./.demo/audit.log`
- `PV_CONTEXT_KEYS` -> demo keys
- `PV_QUORUM_RULES_V2` -> demo quorum rules
- `PV_DECISION_LEDGER_PATH` -> `./.demo/decision-ledger.jsonl`

**4) Export evidence (demo)**
```bash
python export_evidence.py --tenant tenant-demo --from 2026-02-01T00:00:00Z --to 2026-02-28T23:59:59Z
```

## Demo Assets (Repo)
- `demo/tenant-configs/tenant-demo.json`
- `demo/quorum-rules/demo-quorum.json`
- `demo/context-keys/demo-context-keys.json`
- `demo/audit-events/audit-demo.jsonl`
- `demo/approvals/demo-approvals.jsonl`
- `demo/policies/demo-policies.json`
- `demo/decision-ledger/demo-ledger.jsonl`

## Reset Demo Data
```bash
scripts/demo_reset.sh
```

## Using a Custom Demo Root
```bash
python scripts/demo_bootstrap.py --root /var/lib/privatevault/demo --demo-mode
```

## Notes
1. The demo data is **tenant-scoped** to `tenant-demo`.
2. Policy data lives under the demo root as `policies.json`.
3. The audit log is preloaded with synthetic events from **February 2026**.
4. Approval data is synthetic and stored separately for inspection.

## Troubleshooting
- If audit events are missing, check `PV_AUDIT_LOG_PATH`.
- If quorum checks fail, confirm `PV_QUORUM_RULES_V2` is set.
- If evidence export warns about the decision ledger, confirm `PV_DECISION_LEDGER_PATH`.
