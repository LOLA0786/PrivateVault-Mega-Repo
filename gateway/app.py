import json
import logging
import time
import uuid
from typing import Optional

from fastapi import FastAPI, Header, Request, Response
from fastapi.responses import JSONResponse
import requests

app = FastAPI(title="PrivateIntent OS")

INTENT_ENGINE = "http://localhost:8000"
PRIVATE_VAULT = "http://localhost:8001"
REQUEST_TIMEOUT_SECS = 10


logger = logging.getLogger("gateway")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def log_event(event: dict) -> None:
    logger.info(json.dumps(event, separators=(",", ":"), sort_keys=True))


def resolve_request_id(x_request_id: Optional[str]) -> str:
    return x_request_id or str(uuid.uuid4())


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = resolve_request_id(request.headers.get("x-request-id"))
    request.state.request_id = request_id
    start = time.time()
    response: Response
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = int((time.time() - start) * 1000)
        log_event(
            {
                "event": "gateway_request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
                "error": str(exc),
            }
        )
        raise
    duration_ms = int((time.time() - start) * 1000)
    response.headers["x-request-id"] = request_id
    log_event(
        {
            "event": "gateway_request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }
    )
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/execute")
def execute(payload: dict, request: Request, x_request_id: Optional[str] = Header(None)):
    request_id = request.state.request_id or resolve_request_id(x_request_id)
    headers = {"x-request-id": request_id}
    try:
        decision_resp = requests.post(
            f"{INTENT_ENGINE}/authorize-intent",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECS,
        )
    except requests.RequestException as exc:
        log_event(
            {
                "event": "intent_engine_error",
                "request_id": request_id,
                "error": str(exc),
            }
        )
        return JSONResponse(
            status_code=502,
            content={"status": "ERROR", "reason": "Intent engine unavailable"},
        )

    if decision_resp.status_code >= 500:
        return JSONResponse(
            status_code=502,
            content={"status": "ERROR", "reason": "Intent engine error"},
        )
    if decision_resp.status_code >= 400:
        return JSONResponse(
            status_code=400,
            content={"status": "ERROR", "reason": "Bad request"},
        )

    decision = decision_resp.json()

    if not decision.get("allowed"):
        return JSONResponse(
            status_code=403,
            content={
                "status": "BLOCKED",
                "reason": decision.get("reason"),
                "policy": decision.get("policy_version"),
                "evidence": decision.get("evidence_id"),
            },
        )

    try:
        vault_resp = requests.post(
            f"{PRIVATE_VAULT}/vault/secure-action",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECS,
        )
    except requests.RequestException as exc:
        log_event(
            {
                "event": "vault_error",
                "request_id": request_id,
                "error": str(exc),
            }
        )
        return JSONResponse(
            status_code=502,
            content={"status": "ERROR", "reason": "Vault unavailable"},
        )

    if vault_resp.status_code >= 500:
        return JSONResponse(
            status_code=502,
            content={"status": "ERROR", "reason": "Vault error"},
        )
    if vault_resp.status_code >= 400:
        return JSONResponse(
            status_code=400,
            content={"status": "ERROR", "reason": "Bad request"},
        )

    result = vault_resp.json()

    return {
        "status": "EXECUTED",
        "vault_result": result,
        "evidence": decision.get("evidence_id"),
    }
