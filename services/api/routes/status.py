from fastapi import APIRouter

from services.api.models import HealthResponse, StatusResponse

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def status():
    return {"status": "ok", "version": "v1"}


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}
