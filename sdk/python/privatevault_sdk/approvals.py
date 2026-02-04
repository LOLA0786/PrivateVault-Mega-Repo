import hashlib
import hmac
import time
from typing import Dict


def create_approval(
    *,
    approver_id: str,
    role: str,
    region: str,
    intent_hash: str,
    key_id: str,
    secret: str,
    issued_at: int | None = None,
    expires_at: int | None = None,
    approval_id: str | None = None,
) -> Dict:
    issued = issued_at or int(time.time())
    approval = {
        "approval_id": approval_id,
        "approver_id": approver_id,
        "role": role,
        "region": region,
        "intent_hash": intent_hash,
        "issued_at": issued,
        "expires_at": expires_at or (issued + 3600),
        "key_id": key_id,
    }
    signature = hmac.new(secret.encode("utf-8"), intent_hash.encode("utf-8"), hashlib.sha256).hexdigest()
    approval["signature"] = signature
    return approval
