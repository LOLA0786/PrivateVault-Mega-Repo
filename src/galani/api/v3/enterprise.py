from fastapi import APIRouter

router = APIRouter(prefix="/api/v3", tags=["galani-v3"])

@router.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "v3.0",
        "engine": "galani-enterprise"
    }
