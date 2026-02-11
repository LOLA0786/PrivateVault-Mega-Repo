from fastapi import APIRouter, Request
from services.gateway.enforcement import enforce

router = APIRouter(prefix="/gateway", tags=["gateway"])


@router.post("/evaluate")
async def evaluate_gateway(request: Request):
    body = await request.json()

    action = body.get("action", "unknown")
    payload = body.get("payload", {})
    tenant_id = body.get("tenant_id", "default")

    result = enforce(
        action=action,
        payload=payload,
        tenant_id=tenant_id
    )

    return result
