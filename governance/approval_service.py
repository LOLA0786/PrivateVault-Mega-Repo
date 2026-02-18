from datetime import datetime, timedelta
from governance.override_token import OverrideToken

def issue_override(
    decision_type,
    approvers,
    justification,
    mode="standard",
    ttl_minutes=30
):
    return OverrideToken(
        decision_type=decision_type,
        approvers=approvers,
        justification=justification,
        mode=mode,
        issued_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes)
    )
