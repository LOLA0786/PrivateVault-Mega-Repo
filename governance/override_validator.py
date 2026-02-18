from datetime import datetime
from governance.authority_registry import load_authority_registry

registry = load_authority_registry()

def validate_override(token):
    authority = registry[token.decision_type]

    if token.mode == "standard":
        return authority.owner_role in token.approvers

    if token.mode == "break_glass":
        return len(token.approvers) >= 2

    if token.mode == "quorum":
        required = set(authority.quorum_roles)
        return required.issubset(set(token.approvers))

    return False
