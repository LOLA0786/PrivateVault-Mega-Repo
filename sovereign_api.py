import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from indestructible_engine import IndestructibleEngine

app = FastAPI()
engine = IndestructibleEngine()
mock_db = {}

class Req(BaseModel):
    client_id: str
    metric_name: str
    current_val: float
    raw_gradient: float

@app.get("/health")
async def health():
    return {"status": "online", "engine": "indestructible"}

@app.post("/optimize")
async def optimize(req: Req):
    # Quick state management
    state_key = f"{req.client_id}:{req.metric_name}"
    state = mock_db.get(state_key, {"v": 0.0, "e": 0.0})
    
    engine.velocity = state["v"]
    engine.denoiser.estimate = state["e"]
    
    val, info = engine.step(req.current_val, req.raw_gradient)
    
    mock_db[state_key] = {"v": engine.velocity, "e": engine.denoiser.estimate}
    return {"optimized_value": val}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
