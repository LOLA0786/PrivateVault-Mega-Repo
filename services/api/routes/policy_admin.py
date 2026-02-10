from fastapi import APIRouter, HTTPException
from services.api.governance.policy_loader import set_active_policy

router = APIRouter(prefix="/policy", tags=["policy-admin"])

@router.post("/switch")
def switch_policy(tenant_id: str, policy_name: str):
    try:
        set_active_policy(tenant_id, policy_name)
        return {"status": "ok", "active_policy": policy_name}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="POLICY_NOT_FOUND")
