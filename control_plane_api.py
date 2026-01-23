from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import shadow_mode
import policy_registry
from control_plane_normalize import normalize_audit
from control_plane_audit_reader import read_recent_audits
from control_plane_replay import replay_from_audit

app = FastAPI(title="PrivateVault Sovereign Control Plane")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://supportprivatevault.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status")
def status():
    return {
        "node": "ONLINE",
        "mode": ["SHADOW", "ENFORCE"],
        "policy_version": policy_registry.get_active_policy_version(),
    }


@app.get("/intents/recent")
def recent_intents(limit: int = 50):
    raw = read_recent_audits(limit)
    return [normalize_audit(r) for r in raw]


@app.get("/shadow/summary")
def shadow_summary():
    if hasattr(shadow_mode, "shadow_stats"):
        return shadow_mode.shadow_stats()
    return {"would_block": 0, "exposure_prevented": 0, "violations": []}


@app.get("/replay/{intent_hash}")
def replay(intent_hash: str):
    return replay_from_audit(intent_hash)


from fintech_final_demo import run_fintech_intent
from medtech_final_demo import run_medtech_intent
import time


@app.post("/api/emit/fintech")
def emit_fintech(payload: dict):
    start = time.time()
    result = run_fintech_intent(payload)
    result["latency_ms"] = int((time.time() - start) * 1000)
    return result


@app.post("/api/emit/medtech")
def emit_medtech(payload: dict):
    start = time.time()
    result = run_medtech_intent(payload)
    result["latency_ms"] = int((time.time() - start) * 1000)
    return result


from fastapi import HTTPException
import time


def safe_call(fn, payload, domain):
    start = time.time()
    try:
        result = fn(payload)
        if not isinstance(result, dict):
            result = {"result": str(result)}
        result["latency_ms"] = int((time.time() - start) * 1000)
        return result
    except Exception as e:
        # NEVER crash demo
        return {
            "domain": domain,
            "decision": "ERROR",
            "reason": str(e),
            "latency_ms": int((time.time() - start) * 1000),
        }


@app.post("/api/emit/fintech")
def emit_fintech(payload: dict):
    from fintech_final_demo import run_fintech_intent

    return safe_call(run_fintech_intent, payload, "fintech")


@app.post("/api/emit/medtech")
def emit_medtech(payload: dict):
    from medtech_final_demo import run_medtech_intent

    return safe_call(run_medtech_intent, payload, "medtech")
