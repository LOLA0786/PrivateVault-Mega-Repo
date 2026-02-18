import json
from datetime import datetime

def build_evidence_bundle(
    decision,
    intent_hash,
    authority,
    policy_rule,
    risk_score,
    override=None,
    jurisdiction=None,
    crypto_proof=None
):
    bundle = {
        "decision": decision,
        "intent_hash": intent_hash,
        "authority_owner": authority.owner_role,
        "delegates": authority.delegates,
        "policy_rule": policy_rule,
        "risk_score": risk_score,
        "jurisdiction": jurisdiction or authority.jurisdiction,
        "timestamp": datetime.utcnow().isoformat(),
        "override": override,
        "crypto_proof": crypto_proof,
    }
    return bundle

def export_bundle(bundle, path="evidence_bundle.json"):
    with open(path, "w") as f:
        json.dump(bundle, f, indent=2)
