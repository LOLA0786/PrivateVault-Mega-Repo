from fastapi import FastAPI, HTTPException

from services.api.middleware.api_key import APIKeyMiddleware

from services.api.routes import (
    audit,
    auth,
    quorum,
    status,
    tenants,
    approvals,
    evidence,
    api_keys,
    usage,
)


def create_app() -> FastAPI:
    # Root app (no auth here)
    app = FastAPI(title="PrivateVault Platform API", version="v1")


    # Versioned API (API key enforced here)
    api = FastAPI(title="PrivateVault API v1", version="v1")

    api.add_middleware(APIKeyMiddleware)

    # Public / core routes
    api.include_router(status.router)
    api.include_router(auth.router)

    # Tenant + governance
    api.include_router(tenants.router)
    api.include_router(quorum.router)
    api.include_router(audit.router)
    api.include_router(approvals.router)
    api.include_router(evidence.router)
    from services.api.routes import usage
    api.include_router(usage.router)
    from services.api.routes import usage
    api.include_router(usage.router)

    # API key management + usage
    api.include_router(api_keys.router)
    api.include_router(usage.router)

    @api.get("/openapi.json")
    def openapi_spec():
        return api.openapi()

    app.mount("/api/v1", api)
    return app


app = create_app()
