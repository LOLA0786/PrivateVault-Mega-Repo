from pathlib import Path
from services.api.governance.policy_loader import get_policy

BASE_DIR = Path(__file__).resolve().parents[3]
POLICY_DIR = BASE_DIR / "policy_store" / "tenants"

def evaluate_policy(message: str, tenant_id: str = "default"):

    policy_path = POLICY_DIR / f"{tenant_id}.yaml"

    if not policy_path.exists():
        policy_path = POLICY_DIR / "default.yaml"

    policy = get_policy(policy_path)

    mode = policy.get("mode", "monitor")
    rules = policy.get("rules", [])

    for rule in rules:
        keywords = rule.get("match", {}).get("keywords", [])
        for kw in keywords:
            if kw.lower() in message.lower():
                return {
                    "decision": rule.get("action", "ALLOW"),
                    "policy_id": rule.get("id"),
                    "severity": rule.get("severity", "LOW"),
                    "mode": mode,
                    "policy_version": policy.get("version", "1.0.0"),
                }

    return {
        "decision": "ALLOW",
        "policy_id": "allow_all",
        "severity": "LOW",
        "mode": mode,
        "policy_version": policy.get("version", "1.0.0"),
    }
