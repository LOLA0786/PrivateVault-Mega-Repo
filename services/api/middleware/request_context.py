from fastapi import Request

async def auth_tenant_middleware(request: Request, call_next):
    return await call_next(request)
