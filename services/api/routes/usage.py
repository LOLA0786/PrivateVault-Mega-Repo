from fastapi import APIRouter, Request
from services.api.usage_tracker import get_usage

router = APIRouter(prefix="/usage", tags=["usage"])

@router.get("")
async def usage(request: Request):
    return {
        "api_key": request.state.api_key,
        "events": get_usage(request.state.api_key),
    }
