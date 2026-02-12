from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # ---------------------------
        # Public Endpoints
        # ---------------------------
        if request.url.path in ["/api/v1/status", "/api/v1/health"]:
            return await call_next(request)
            return await call_next(request)

        request.state.role = None
        request.state.tenant_id = None

        auth_header = request.headers.get("Authorization")
        api_key = request.headers.get("X-API-Key")

        # Bearer token
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            if token == "token-admin":
                request.state.role = "admin"
                request.state.tenant_id = None

            elif token == "token-tenant":
                request.state.role = "tenant"
                request.state.tenant_id = "tenant-1"

            else:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "INVALID_TOKEN"},
                )

        # API key
        elif api_key:
            request.state.role = "api"
            request.state.tenant_id = "test-tenant"

        else:
            return JSONResponse(
                status_code=401,
                content={"detail": "AUTH_REQUIRED"},
            )

        return await call_next(request)
