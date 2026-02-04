import time

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

import shadow_mode
import policy_registry
from control_plane_normalize import normalize_audit
from control_plane_audit_reader import read_recent_audits
from control_plane_replay import replay_from_audit
from audit_logger import build_request_audit_event, log_audit_event
from security_context import require_signed_context
from quorum import require_quorum_for_emit

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


@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start = time.time()
    error_detail = None
    response = None
    try:
        response = await call_next(request)
        return response
    except HTTPException as exc:
        error_detail = str(exc.detail)
        raise
    except Exception as exc:
        error_detail = str(exc)
        raise
    finally:
        status_code = response.status_code if response else 500
        decision = "ALLOW" if status_code < 400 else "DENY"
        latency_ms = int((time.time() - start) * 1000)
        context = getattr(request.state, "pv_context", None)
        quorum = getattr(request.state, "pv_quorum", None)
        client_ip = request.client.host if request.client else None
        event = build_request_audit_event(
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            decision=decision,
            latency_ms=latency_ms,
            context=context,
            quorum=quorum,
            error=error_detail,
            client_ip=client_ip,
        )
        log_audit_event(event)


@app.get("/status")
def status(context=Depends(require_signed_context)):
    return {
        "node": "ONLINE",
        "mode": ["SHADOW", "ENFORCE"],
        "policy_version": policy_registry.get_active_policy_version(),
    }


@app.get("/intents/recent")
def recent_intents(limit: int = 50, context=Depends(require_signed_context)):
    raw = read_recent_audits(limit)
    return [normalize_audit(r) for r in raw]


@app.get("/shadow/summary")
def shadow_summary(context=Depends(require_signed_context)):
    if hasattr(shadow_mode, "shadow_stats"):
        return shadow_mode.shadow_stats()
    return {"would_block": 0, "exposure_prevented": 0, "violations": []}


@app.get("/replay/{intent_hash}")
def replay(intent_hash: str, context=Depends(require_signed_context)):
    return replay_from_audit(intent_hash)


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
def emit_fintech(
    payload: dict,
    context=Depends(require_signed_context),
    quorum=Depends(require_quorum_for_emit),
):
    from fintech_final_demo import run_fintech_intent

    return safe_call(run_fintech_intent, payload, "fintech")


@app.post("/api/emit/medtech")
def emit_medtech(
    payload: dict,
    context=Depends(require_signed_context),
    quorum=Depends(require_quorum_for_emit),
):
    from medtech_final_demo import run_medtech_intent

    return safe_call(run_medtech_intent, payload, "medtech")
