from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from services.api.storage.api_keys import get_api_key_record, increment_usage
from services.api.middleware.auth import AuthContext

PUBLIC_PATHS = {
    "/api/v1/health",
    "/api/v1/status",
    "/api/v1/openapi.json",
    "/api/v1/keys/create",
}

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS:
            return await call_next(request)

        if path.startswith("/api/v1"):
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                raise HTTPException(status_code=401, detail="API_KEY_REQUIRED")

            record = get_api_key_record(api_key)
            if not record:
                raise HTTPException(status_code=403, detail="INVALID_API_KEY")

            if record["used"] >= record["monthly_limit"]:
                raise HTTPException(status_code=429, detail="API_LIMIT_EXCEEDED")

            increment_usage(api_key)

            # 🔑 THIS IS THE FIX
            request.state.api_key = api_key
            request.state.api_plan = record["plan"]

            # Inject legacy auth context so require_auth PASSES
            request.state.auth = AuthContext(
                token=api_key,
                scopes=["tenant:read", "tenant:write"],
                tenant_id=None,
            )

        return await call_next(request)
