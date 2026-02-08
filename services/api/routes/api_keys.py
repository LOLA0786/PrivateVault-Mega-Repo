from fastapi import APIRouter, HTTPException, Query

from services.api.storage.api_keys import create_api_key

router = APIRouter(prefix="/keys", tags=["api-keys"])

@router.post("/create")
def create_key(
    plan: str = Query(..., enum=["starter", "pro", "enterprise"])
):
    try:
        record = create_api_key(plan=plan)
        return {
            "api_key": record["api_key"],
            "plan": record["plan"],
            "monthly_limit": record["monthly_limit"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
