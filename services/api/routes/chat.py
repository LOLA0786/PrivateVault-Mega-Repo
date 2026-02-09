from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import json
from pathlib import Path

router = APIRouter(prefix="/chat", tags=["chat"])


# ---------
# Models
# ---------

class ChatRequest(BaseModel):
    request_id: str


class ChatResponse(BaseModel):
    message: str


# ---------
# Load synthetic evidence + templates
# (later this can be DB-backed, no API change)
# ---------

BASE = Path(__file__).resolve().parents[3]

with open(BASE / "synthetic_data/evidence_store.json") as f:
    EVIDENCE = json.load(f)

with open(BASE / "synthetic_data/chat_responses.json") as f:
    TEMPLATES = json.load(f)


# ---------
# Endpoint
# ---------

@router.post("/respond", response_model=ChatResponse)
def chat_respond(payload: ChatRequest):
    evt = next(
        (e for e in EVIDENCE if e["request_id"] == payload.request_id),
        None,
    )

    if not evt:
        raise HTTPException(status_code=404, detail="REQUEST_NOT_FOUND")

    template = (
        TEMPLATES["why_blocked"]["template"]
        if evt["decision"] == "BLOCK"
        else TEMPLATES["why_allowed"]["template"]
    )

    message = template.format(
        policy=evt["policy"],
        reason="Policy enforcement",
        hash=evt["hash"],
        timestamp=evt["timestamp"],
    )

    return ChatResponse(message=message)
