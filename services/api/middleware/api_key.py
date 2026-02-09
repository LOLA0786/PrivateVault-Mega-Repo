from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "API_KEY_REQUIRED"},
            )

        # Minimal, safe state injection
        request.state.api_key = api_key
        request.state.tenant_id = "test-tenant"

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # NEVER let middleware throw raw exceptions
            return JSONResponse(
                status_code=500,
                content={"detail": "INTERNAL_MIDDLEWARE_ERROR"},
            )
