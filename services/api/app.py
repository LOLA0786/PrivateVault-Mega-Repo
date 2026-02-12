from fastapi import FastAPI

from services.api.middleware.api_key import APIKeyMiddleware
from services.api.routes import (
    status,
    tenants,
    api_keys,
    usage,
    chat,
    audit_policy,
    quorum,
    audit,
    approvals,
    evidence,
    auth,
)

def create_app() -> FastAPI:
    app = FastAPI(title="PrivateVault Platform API")

    api = FastAPI(title="PrivateVault API v1", version="v1")
    api.add_middleware(APIKeyMiddleware)

    # Core
    api.include_router(status.router)
    api.include_router(auth.router)
    api.include_router(chat.router)

    # Governance
    api.include_router(tenants.router)
    api.include_router(quorum.router)
    api.include_router(audit.router)
    api.include_router(approvals.router)
    api.include_router(evidence.router)
    api.include_router(audit_policy.router)

    # Keys + usage
    api.include_router(api_keys.router)
    api.include_router(usage.router)

    app.mount("/api/v1", api)

    return app


app = create_app()
