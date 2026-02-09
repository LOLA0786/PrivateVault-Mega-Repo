from fastapi import APIRouter, Request

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/whoami")
async def whoami(request: Request):
    return {
        "tenant_id": getattr(request.state, "tenant_id", None),
        "api_key_id": getattr(request.state, "api_key_id", None),
    }
