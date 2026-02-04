from fastapi import HTTPException, Request
from services.api.errors import http_exception_handler

from services.api.middleware.auth import AuthContext, require_auth
from services.api.middleware.tenant import resolve_tenant


def is_public_path(path: str) -> bool:
    return path in ["/api/v1/status", "/api/v1/health", "/api/v1/openapi.json"]


async def auth_tenant_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/v1") and not is_public_path(request.url.path):
        try:
            auth = require_auth(request)
            request.state.auth = auth
            request.state.tenant_id = resolve_tenant(request, auth)
        except HTTPException as exc:
            return http_exception_handler(request, exc)
    return await call_next(request)
