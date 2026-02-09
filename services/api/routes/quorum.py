from fastapi import APIRouter

router = APIRouter(prefix="/quorum", tags=["quorum"])

def _load_rules_snapshot():
    return []

@router.get("/")
async def get_quorum():
    return {"rules": _load_rules_snapshot()}
