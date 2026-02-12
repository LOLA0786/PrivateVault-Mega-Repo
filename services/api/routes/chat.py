from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/respond")
def chat_respond():
    return {
        "message": "🚫 BLOCKED - GDPR_PII_RESTRICTION"
    }
