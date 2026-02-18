from fastapi import APIRouter
from governance.approval_service import issue_override

router = APIRouter()

@router.post("/approve")
def approve_action(data: dict):
    token = issue_override(
        decision_type=data["decision_type"],
        approvers=data["approvers"],
        justification=data.get("justification", ""),
        mode=data.get("mode", "standard")
    )
    return {"override_token": token.__dict__}

@router.post("/break-glass")
def break_glass(data: dict):
    token = issue_override(
        decision_type=data["decision_type"],
        approvers=data["approvers"],
        justification=data["justification"],
        mode="break_glass"
    )
    return {"override_token": token.__dict__}
