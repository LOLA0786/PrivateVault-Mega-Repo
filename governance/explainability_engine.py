def build_explanation(decision, policy_rule, risk_score, blocked, remediation=None):
    machine = {
        "decision": decision,
        "policy_rule": policy_rule,
        "risk_score": risk_score,
        "blocked": blocked
    }

    human = (
        f"Action '{decision}' was "
        + ("blocked" if blocked else "approved")
        + f" due to policy rule '{policy_rule}'. "
        + f"Risk score evaluated at {risk_score}."
    )

    if remediation:
        human += f" Recommended action: {remediation}."

    executive = {
        "risk_prevented": blocked,
        "policy_triggered": policy_rule,
        "exposure_prevented": risk_score > 70
    }

    return {
        "machine_explanation": machine,
        "human_explanation": human,
        "executive_summary": executive
    }
