from fastapi import APIRouter

router = APIRouter(prefix="/quorum", tags=["quorum"])

_rules = {}


@router.put("/rules")
def set_rules(payload: dict):
    global _rules
    _rules = payload.get("rules", {})
    return {"status": "ok"}


@router.get("/rules")
def get_rules():
    return {"rules": _rules}


@router.post("/validate")
def validate(payload: dict):
    approvals = payload.get("approvals", [])
    approved_count = len(approvals)

    return {
        "approved": approved_count,
        "valid": approved_count >= 1
    }
