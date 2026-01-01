import httpx, os
from fastapi import FastAPI, HTTPException
from indestructible_engine import IndestructibleEngine

app = FastAPI()
engine = IndestructibleEngine()

@app.post("/secure_optimize")
async def secure_optimize(payload: dict):
    async with httpx.AsyncClient() as client:
        # Pass actor and mode to UAAL
        uaal_resp = await client.post("http://127.0.0.1:8000/authorize-intent", 
                                    json={
                                        "actor": payload.get("actor", "gateway"),
                                        "mode": payload.get("mode", "ENFORCE"),
                                        "raw_gradient": payload.get("raw_gradient", 0.0)
                                    })
        auth = uaal_resp.json()
        
        if not auth.get("allowed"):
            raise HTTPException(status_code=403, detail=auth.get("reason"))

        val, _ = engine.step(payload.get("current_val", 100), payload.get("raw_gradient", 0))
        return {"optimized_value": val, "evidence_hash": auth.get("evidence_hash")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
