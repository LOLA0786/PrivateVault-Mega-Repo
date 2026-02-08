from fastapi import FastAPI, HTTPException
from services.api.middleware.api_key import APIKeyMiddleware

from services.api.errors import http_exception_handler, unhandled_exception_handler
from services.api.middleware.request_context import auth_tenant_middleware
from services.api.routes import audit, auth, quorum, status, tenants, approvals, evidence


def create_app() -> FastAPI:
    app = FastAPI(title="PrivateVault Platform API", version="v1")

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)



    # app.middleware("http")(auth_tenant_middleware)

    api = FastAPI(title="PrivateVault API v1", version="v1")
    api.add_middleware(APIKeyMiddleware)
    api.add_exception_handler(HTTPException, http_exception_handler)
    api.add_exception_handler(Exception, unhandled_exception_handler)

    api.include_router(status.router)
    api.include_router(auth.router)
    api.include_router(tenants.router)
    api.include_router(quorum.router)
    api.include_router(audit.router)
    api.include_router(approvals.router)
    api.include_router(evidence.router)
    from services.api.routes import api_keys
    api.include_router(api_keys.router)


    @api.get("/openapi.json")
    def openapi_spec():
        return api.openapi()

    app.mount("/api/v1", api)
    return app


app = create_app()


