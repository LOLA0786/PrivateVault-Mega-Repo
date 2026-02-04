import json
import os

from fastapi import APIRouter, Depends, HTTPException

from services.api.middleware.auth import AuthContext, require_auth, require_scope
from services.api.middleware.tenant import require_tenant, resolve_tenant
from services.api.models import QuorumValidateRequest, QuorumValidateResponse
from quorum import validate_quorum

router = APIRouter()


def _load_rules_snapshot():
    if os.getenv("PV_QUORUM_RULES_V2"):
        return json.loads(os.getenv("PV_QUORUM_RULES_V2"))
    if os.getenv("PV_QUORUM_RULES"):
        return json.loads(os.getenv("PV_QUORUM_RULES"))
    return {"min": int(os.getenv("PV_QUORUM_MIN", "2"))}


@router.get("/quorum/rules")
def get_quorum_rules(auth: AuthContext = Depends(require_auth)):
    require_scope(auth, "quorum:read")
    return _load_rules_snapshot()


@router.post("/quorum/validate", response_model=QuorumValidateResponse)
def quorum_validate(payload: QuorumValidateRequest, auth: AuthContext = Depends(require_auth)):
    require_scope(auth, "quorum:read")
    tenant_id = payload.tenant_id
    if auth.tenant_id and tenant_id and tenant_id != auth.tenant_id:
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_VIOLATION")
    result = validate_quorum(
        action=payload.action,
        payload=payload.payload,
        approvals=payload.approvals,
        tenant_id=tenant_id or auth.tenant_id,
    )
    return result
