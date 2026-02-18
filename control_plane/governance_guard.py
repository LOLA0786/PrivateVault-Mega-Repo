from control_plane.governance_flow import evaluate_governance

class GovernanceBlocked(Exception):
    pass

def enforce_governance(intent, risk, policy, override_token=None):
    gov = evaluate_governance(
        decision_type=intent.type,
        risk_score=risk.score,
        policy_rule=policy.rule,
        override_token=override_token
    )

    if not gov.allowed:
        raise GovernanceBlocked(gov.explanation)

    return gov
