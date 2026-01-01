import os, time, hashlib, json, hmac
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
KERNEL_KEY = os.getenv("SOVEREIGN_KERNEL_KEY", "MUMBAI_FORCE_2026").encode()
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audits.worm")

def canonical_sign(actor, mode, gradient):
    # 🎯 FORCE STRING NORMALIZATION
    msg = f"{actor}|{mode}|{float(gradient):.6f}".encode()
    return hmac.new(KERNEL_KEY, msg, hashlib.sha256).hexdigest()

class IntentRequest(BaseModel):
    actor: str
    mode: str
    raw_gradient: float
    current_val: float

@app.post("/authorize-intent")
async def authorize(payload: IntentRequest):
    is_violation = payload.raw_gradient > 1.0
    allowed = not (is_violation and payload.mode == "ENFORCE")
    
    evidence_hash = canonical_sign(payload.actor, payload.mode, payload.raw_gradient)
    
    log_entry = {
        "actor": payload.actor,
        "mode": payload.mode,
        "gradient": payload.raw_gradient,
        "hash": evidence_hash,
        "allowed": allowed,
        "timestamp": str(time.time())
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {"allowed": allowed, "evidence_hash": f"0x{evidence_hash}", "reason": "Authorized"}
