#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" delete deploy/authz-adapter --ignore-not-found
kubectl -n "$NS" delete svc/authz-adapter --ignore-not-found

cat <<'YAML' | kubectl apply -n "$NS" -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: authz-adapter
spec:
  replicas: 1
  selector:
    matchLabels: { app: authz-adapter }
  template:
    metadata:
      labels: { app: authz-adapter }
    spec:
      containers:
      - name: app
        image: python:3.12-slim
        ports:
          - containerPort: 8000
        command: ["/bin/bash","-lc"]
        args:
          - |
            pip install --no-cache-dir fastapi uvicorn httpx >/dev/null
            cat >/app.py <<'PY'
            from fastapi import FastAPI, Request
            from fastapi.responses import JSONResponse
            import httpx, os

            OPA = os.getenv("OPA_URL","http://opa:8181")
            app = FastAPI()

            def mk_input(req: Request):
                headers = {k.lower(): v for k,v in req.headers.items()}
                method = headers.get(":method") or headers.get("x-forwarded-method") or req.method
                path   = headers.get(":path") or headers.get("x-forwarded-uri") or req.url.path
                return {
                    "attributes": {
                        "request": {
                            "http": {
                                "method": method,
                                "path": path,
                                "headers": headers
                            }
                        }
                    }
                }

            async def decide(req: Request):
                inp = mk_input(req)
                async with httpx.AsyncClient(timeout=1.0) as client:
                    r = await client.post(f"{OPA}/v1/data/envoy/authz", json={"input": inp})
                    r.raise_for_status()
                    return r.json().get("result", {})

            @app.get("/check")
            @app.post("/check")
            async def check(req: Request):
                try:
                    decision = await decide(req)
                    allow = bool(decision.get("allow", False))
                    require_approval = bool(decision.get("require_approval", False))

                    if require_approval:
                        return JSONResponse(
                            status_code=403,
                            content={"allowed": False, "reason": "approval_required"},
                            headers={"x-approval-required": "true"}
                        )
                    if allow:
                        return JSONResponse(
                            status_code=200,
                            content={"allowed": True},
                            headers={"x-ext-authz": "allow"}
                        )
                    return JSONResponse(
                        status_code=403,
                        content={"allowed": False, "reason": "denied"},
                        headers={"x-ext-authz": "deny"}
                    )
                except Exception as e:
                    return JSONResponse(
                        status_code=403,
                        content={"allowed": False, "reason": "authz_error", "error": str(e)},
                        headers={"x-ext-authz": "error"}
                    )
            PY
            uvicorn app:app --host 0.0.0.0 --port 8000
        env:
          - name: OPA_URL
            value: "http://opa:8181"
---
apiVersion: v1
kind: Service
metadata:
  name: authz-adapter
spec:
  selector: { app: authz-adapter }
  ports:
    - port: 8000
      targetPort: 8000
YAML

kubectl -n "$NS" rollout status deploy/authz-adapter
