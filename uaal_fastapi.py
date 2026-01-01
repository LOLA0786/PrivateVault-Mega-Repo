import os, time, hashlib, json, hmac
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
KERNEL_KEY = os.getenv("SOVEREIGN_KERNEL_KEY", "DEVELOPMENT_INSECURE_KEY").encode()

def canonical_sign(data: dict):
    # Fix 1: Sort keys and remove whitespace
    # Fix 2: Ensure float precision is locked
    clean_data = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(KERNEL_KEY, clean_data, hashlib.sha256).hexdigest()

class IntentRequest(BaseModel):
    actor: str
    mode: str
    raw_gradient: float
    current_val: float

@app.post("/authorize-intent")
async def authorize(payload: IntentRequest):
    # Normalize the data for signing
    payload_dict = {
        "actor": payload.actor,
        "gradient": round(payload.raw_gradient, 6),
        "mode": payload.mode
    }
    
    is_violation = payload.raw_gradient > 1.0
    allowed = not (is_violation and payload.mode == "ENFORCE")
    
    evidence_hash = canonical_sign(payload_dict)
    
    return {
        "allowed": allowed,
        "evidence_hash": f"0x{evidence_hash}",
        "reason": "Risk violation" if not allowed else "Authorized"
    }
