from fastapi import FastAPI

from services.api.middleware.api_key import APIKeyMiddleware

from services.api.routes import (
    status,
    tenants,
    api_keys,
    usage,
    chat,
    audit_policy,
)


def create_app() -> FastAPI:
    # Root app (public)
    app = FastAPI(title="PrivateVault Platform API")

    # Versioned API (API key enforced)
    api = FastAPI(title="PrivateVault API v1", version="v1")
    api.add_middleware(APIKeyMiddleware)

    # Core routes
    api.include_router(status.router)
    api.include_router(chat.router)

    # Tenant & governance
    api.include_router(tenants.router)
    api.include_router(audit_policy.router)

    # Keys + usage
    api.include_router(api_keys.router)
    api.include_router(usage.router)

    # OpenAPI passthrough
    @api.get("/openapi.json")
    def openapi_spec():
        return api.openapi()

    app.mount("/api/v1", api)
    return app


app = create_app()
