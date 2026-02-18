import yaml
from governance.decision_authority_schema import DecisionAuthority

def load_authority_registry(path="governance/authority_registry.yaml"):
    with open(path) as f:
        raw = yaml.safe_load(f)

    registry = {}
    for decision, cfg in raw.items():
        registry[decision] = DecisionAuthority(
            decision_type=decision,
            owner_role=cfg.get("owner_role"),
            delegates=cfg.get("delegates", []),
            escalation_role=cfg.get("escalation_role"),
            quorum_required=cfg.get("quorum_required", False),
            quorum_roles=cfg.get("quorum_roles", []),
            jurisdiction=cfg.get("jurisdiction", []),
            risk_threshold=cfg.get("risk_threshold", 0),
        )
    return registry
