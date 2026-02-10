from fastapi import APIRouter
from services.api.governance.policy_audit import read_policy_audit_log

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/policy-changes")
def policy_changes():
    return read_policy_audit_log()
