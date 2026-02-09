from fastapi import APIRouter, HTTPException, Request
from services.api import store

router = APIRouter()

@router.post("/tenants")
def create_tenant(payload: dict, request: Request):
    tenant_id = payload.get("tenant_id") or request.state.api_key
    if store.get_tenant(tenant_id):
        raise HTTPException(status_code=409, detail="TENANT_EXISTS")
    return store.create_tenant({
        "tenant_id": tenant_id,
        "name": payload.get("name", tenant_id),
    })

@router.get("/tenants")
def list_tenants():
    return store.list_tenants()

@router.get("/tenants/{tenant_id}")
def get_tenant(tenant_id: str):
    tenant = store.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="TENANT_NOT_FOUND")
    return tenant
