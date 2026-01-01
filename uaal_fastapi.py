import time, hashlib, json
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class IntentRequest(BaseModel):
    actor: str = "unknown"
    mode: str = "ENFORCE"
    raw_gradient: float = 0.0

@app.post("/authorize-intent")
async def authorize(payload: IntentRequest):
    gradient = payload.raw_gradient
    is_violation = gradient > 1.0
    
    # Logic: If violation AND mode is ENFORCE, we BLOCK.
    # If violation AND mode is SHADOW, we ALLOW but log the warning.
    allowed = not (is_violation and payload.mode == "ENFORCE")
    
    evidence_hash = hashlib.sha256(f"{time.time()}".encode()).hexdigest()
    
    # Write to the WORM log
    with open("audits.worm", "a") as f:
        log_entry = {"hash": evidence_hash, "actor": payload.actor, "mode": payload.mode, "gradient": gradient, "allowed": allowed}
        f.write(json.dumps(log_entry) + "\n")

    return {
        "allowed": allowed,
        "evidence_hash": f"0x{evidence_hash}",
        "mode": payload.mode,
        "reason": "Risk violation blocked" if not allowed else "Authorized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
