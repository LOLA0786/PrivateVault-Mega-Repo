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

        request.state.api_key = api_key
        request.state.tenant_id = "test-tenant"

        # 🔥 TEMP: allow real tracebacks during debug
        response = await call_next(request)
        return response
