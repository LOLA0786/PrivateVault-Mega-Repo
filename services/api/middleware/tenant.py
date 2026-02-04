from typing import Optional

from fastapi import HTTPException, Request

from services.api.middleware.auth import AuthContext


def resolve_tenant(request: Request, auth: AuthContext) -> Optional[str]:
    header_tenant = request.headers.get("X-PV-Tenant")
    if auth.tenant_id:
        if header_tenant and header_tenant != auth.tenant_id:
            raise HTTPException(status_code=403, detail="TENANT_SCOPE_VIOLATION")
        return auth.tenant_id
    return header_tenant


def require_tenant(tenant_id: Optional[str]) -> str:
    if not tenant_id:
        raise HTTPException(status_code=400, detail="TENANT_REQUIRED")
    return tenant_id
