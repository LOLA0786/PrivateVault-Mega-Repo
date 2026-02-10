from fastapi import APIRouter
from services.api.governance.policy_loader import invalidate_policy_cache


from services.api.models import HealthResponse, StatusResponse

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def status():
    return {"status": "ok", "version": "v1"}


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}

from services.api.governance.policy_loader import invalidate_policy_cache


@router.post("/reload-policies")
def reload_policies():
    invalidate_policy_cache()
    return {"status": "policy_cache_cleared"}

@router.post("/status/reload-policies")
def reload_policies():
    invalidate_policy_cache()
    return {"status": "ok", "message": "policy cache reloaded"}
