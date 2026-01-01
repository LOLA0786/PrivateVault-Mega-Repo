import os, httpx, hmac, hashlib, json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
KERNEL_KEY = os.getenv("SOVEREIGN_KERNEL_KEY", "DEVELOPMENT_INSECURE_KEY").encode()

def verify_signature(data: dict, received_hash: str):
    # MUST MATCH UAAL EXACTLY
    clean_data = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    expected_hash = f"0x{hmac.new(KERNEL_KEY, clean_data, hashlib.sha256).hexdigest()}"
    return hmac.compare_digest(expected_hash, received_hash)

class OptimizeRequest(BaseModel):
    current_val: float
    raw_gradient: float
    mode: str = "ENFORCE"
    actor: str = "mumbai_founder"

@app.post("/secure_optimize")
async def secure_optimize(payload: OptimizeRequest):
    async with httpx.AsyncClient() as client:
        auth_response = await client.post("http://127.0.0.1:8000/authorize-intent", json=payload.dict())
        auth_data = auth_response.json()

        if not auth_data["allowed"]:
            raise HTTPException(status_code=403, detail="🛑 KERNEL_BLOCK: Unauthorized Risk.")

        # Reconstruct the dict that was signed
        payload_to_verify = {
            "actor": payload.actor,
            "gradient": round(payload.raw_gradient, 6),
            "mode": payload.mode
        }

        if not verify_signature(payload_to_verify, auth_data["evidence_hash"]):
            raise HTTPException(status_code=401, detail="⚠️ SECURITY_ALERT: Signature Mismatch!")

        optimized_val = payload.current_val - (0.01 * payload.raw_gradient)
        return {"status": "SUCCESS", "optimized_value": optimized_val, "evidence_hash": auth_data["evidence_hash"]}
