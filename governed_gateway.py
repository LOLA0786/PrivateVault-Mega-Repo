import os, hashlib, hmac, httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
KERNEL_KEY = os.getenv("SOVEREIGN_KERNEL_KEY", "GALANI_FORCE_2026").encode()
UAAL_ENDPOINT = "http://127.0.0.1:8000/authorize-intent"


def canonical_sign(actor, mode, gradient):
    msg = f"{actor}|{mode}|{float(gradient):.6f}".encode()
    return hmac.new(KERNEL_KEY, msg, hashlib.sha256).hexdigest()


class OptimizationRequest(BaseModel):
    current_val: float
    raw_gradient: float
    mode: str
    actor: str


@app.post("/secure_optimize")
async def secure_optimize(req: OptimizationRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(UAAL_ENDPOINT, json=req.dict())

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="⚠️ SECURITY_ALERT: Kernel Desync")

    auth_data = resp.json()
    if not auth_data.get("allowed"):
        raise HTTPException(
            status_code=403, detail="🛑 KERNEL_BLOCK: Unauthorized Risk."
        )

    optimized_val = req.current_val - (req.raw_gradient * 0.01)
    return {
        "optimized_value": optimized_val,
        "evidence_hash": auth_data.get("evidence_hash"),
    }
