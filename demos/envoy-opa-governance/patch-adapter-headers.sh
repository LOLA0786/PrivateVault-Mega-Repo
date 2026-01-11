#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" delete deploy/authz-adapter --ignore-not-found

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
      labels:
        app: authz-adapter
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

            def first(*vals):
                for v in vals:
                    if v and str(v).strip():
                        return str(v)
                return ""

            def mk_input(req: Request):
                h = {k.lower(): v for k,v in req.headers.items()}

                # These are the reliable ones in Envoy ext_authz HTTP
                method = first(h.get("x-forwarded-method"), h.get(":method"), req.method)

                path = first(
                    h.get("x-envoy-original-path"),
                    h.get("x-original-uri"),
                    h.get("x-forwarded-uri"),
                    h.get(":path"),
                    req.url.path,
                )
                if not path.startswith("/"):
                    path = "/" + path

                return {
                    "attributes": {
                        "request": {
                            "http": {
                                "method": method,
                                "path": path,
                                "headers": h
                            }
                        }
                    }
                }

            async def do_check(req: Request):
                inp = mk_input(req)
                async with httpx.AsyncClient(timeout=1.0) as client:
                    r = await client.post(f"{OPA}/v1/data/envoy/authz", json={"input": inp})
                    r.raise_for_status()
                    decision = r.json().get("result", {})

                allow = bool(decision.get("allow", False))
                require_approval = bool(decision.get("require_approval", False))

                if require_approval:
                    return JSONResponse(status_code=403, content={"allowed": False, "reason": "approval_required"},
                                        headers={"x-approval-required":"true"})
                if allow:
                    return JSONResponse(status_code=200, content={"allowed": True})
                return JSONResponse(status_code=403, content={"allowed": False, "reason": "denied"})

            @app.api_route("/{full_path:path}", methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
            async def catch_all(req: Request, full_path: str):
                try:
                    return await do_check(req)
                except Exception as e:
                    return JSONResponse(status_code=403, content={"allowed": False, "reason": "authz_error", "error": str(e)})

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
  selector:
    app: authz-adapter
  ports:
    - port: 8000
      targetPort: 8000
YAML

kubectl -n "$NS" rollout status deploy/authz-adapter
