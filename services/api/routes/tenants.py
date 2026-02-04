from fastapi import APIRouter, Depends, HTTPException, Request

from services.api.middleware.auth import AuthContext, require_auth, require_scope
from services.api.middleware.tenant import resolve_tenant, require_tenant
from services.api.models import TenantCreateRequest, TenantResponse, TenantUpdateRequest
from services.api import store

router = APIRouter()


@router.post("/tenants", response_model=TenantResponse)
def create_tenant(payload: TenantCreateRequest, auth: AuthContext = Depends(require_auth)):
    require_scope(auth, "tenant:write")
    if store.get_tenant(payload.tenant_id):
        raise HTTPException(status_code=409, detail="TENANT_EXISTS")
    tenant = TenantResponse(**payload.model_dump())
    return store.create_tenant(tenant)


@router.get("/tenants", response_model=list[TenantResponse])
def list_tenants(auth: AuthContext = Depends(require_auth)):
    require_scope(auth, "tenant:read")
    return store.list_tenants()


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: str, auth: AuthContext = Depends(require_auth)):
    require_scope(auth, "tenant:read")
    if auth.tenant_id and tenant_id != auth.tenant_id:
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_VIOLATION")
    tenant = store.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="TENANT_NOT_FOUND")
    return tenant


@router.patch("/tenants/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: str,
    payload: TenantUpdateRequest,
    auth: AuthContext = Depends(require_auth),
):
    require_scope(auth, "tenant:write")
    if auth.tenant_id and tenant_id != auth.tenant_id:
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_VIOLATION")
    updated = store.update_tenant(tenant_id, payload.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="TENANT_NOT_FOUND")
    return updated


@router.delete("/tenants/{tenant_id}")
def delete_tenant(tenant_id: str, auth: AuthContext = Depends(require_auth)):
    require_scope(auth, "tenant:write")
    if auth.tenant_id and tenant_id != auth.tenant_id:
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_VIOLATION")
    deleted = store.delete_tenant(tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="TENANT_NOT_FOUND")
    return {"deleted": True}
