from governance.authority_registry import load_authority_registry
from governance.evidence_bundle import build_evidence_bundle, export_bundle

registry = load_authority_registry()
authority = registry["payment_release"]

bundle = build_evidence_bundle(
    decision="payment_release",
    intent_hash="abc123hash",
    authority=authority,
    policy_rule="threshold_limit_policy",
    risk_score=92,
    override={
        "mode": "quorum",
        "approvers": ["FinanceController", "ComplianceOfficer"],
        "justification": "Emergency vendor settlement"
    },
    crypto_proof="merkle_root_hash_here"
)

export_bundle(bundle, "audit_payment_release.json")
print("Audit bundle generated.")
