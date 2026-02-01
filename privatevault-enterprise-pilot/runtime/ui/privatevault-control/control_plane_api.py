from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import shadow_mode
import policy_registry
from control_plane_normalize import normalize_audit
from control_plane_audit_reader import read_recent_audits

app = FastAPI(title="PrivateVault Sovereign Control Plane")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    from replay_protection import replay_intent

    return replay_intent(intent_hash)
