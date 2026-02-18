from governance.authority_registry import load_authority_registry
from governance.override_validator import validate_override
from governance.explainability_engine import build_explanation

authority_registry = load_authority_registry()

class GovernanceResult:
    def __init__(self, allowed, reason=None, explanation=None):
        self.allowed = allowed
        self.reason = reason
        self.explanation = explanation

def evaluate_governance(
    decision_type,
    risk_score,
    policy_rule,
    override_token=None,
):
    authority = authority_registry.get(decision_type)

    if not authority:
        return GovernanceResult(False, "UnknownDecisionType")

    # quorum requirement
    if authority.quorum_required and not override_token:
        return GovernanceResult(
            False,
            "ApprovalRequired",
            build_explanation(
                decision_type,
                policy_rule,
                risk_score,
                True,
                "Quorum approval required"
            )
        )

    # override validation
    if override_token and not validate_override(override_token):
        return GovernanceResult(False, "InvalidOverride")

    explanation = build_explanation(
        decision_type,
        policy_rule,
        risk_score,
        False
    )

    return GovernanceResult(True, explanation=explanation)
