import time, hashlib, json

class UAALGovernor:
    def __init__(self, policy_path="config/policies.json"):
        self.policy_path = policy_path

    def authorize(self, actor, mode, gradient):
        is_violation = gradient > 1.0 # Default policy
        allowed = not (is_violation and mode == "ENFORCE")
        evidence_hash = hashlib.sha256(f"{time.time()}{gradient}".encode()).hexdigest()
        
        return {
            "allowed": allowed,
            "evidence_hash": f"0x{evidence_hash}",
            "reason": "Policy Violation" if is_violation else "Success"
        }
