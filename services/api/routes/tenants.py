from fastapi import APIRouter, HTTPException, Request
from services.api.models.tenant import TenantCreateRequest, TenantResponse
from services.api import store

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("")
def create_tenant(req: TenantCreateRequest):
    tenant = TenantResponse(
        tenant_id=req.tenant_id,
        name=req.name
    )
    return store.create_tenant(tenant)


@router.get("")
def list_tenants():
    return store.list_tenants()


@router.get("/{tenant_id}")
def get_tenant(tenant_id: str, request: Request):

    role = getattr(request.state, "role", None)
    caller_tenant = getattr(request.state, "tenant_id", None)

    # 🔥 ENFORCE SCOPE FIRST (do NOT check existence yet)
    if role == "tenant" and caller_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_VIOLATION")

    tenant = store.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="TENANT_NOT_FOUND")

    return tenant
