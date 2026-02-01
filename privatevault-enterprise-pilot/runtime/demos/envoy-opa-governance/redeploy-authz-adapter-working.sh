#!/usr/bin/env bash
set -euo pipefail
NS="governance"

cat <<'YAML' | kubectl apply -n "$NS" -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: authz-adapter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: authz-adapter
  template:
    metadata:
      labels:
        app: authz-adapter
    spec:
      containers:
      - name: authz-adapter
        image: python:3.11-slim
        ports:
        - containerPort: 8000
        command: ["bash","-lc"]
        args:
          - |
            pip -q install fastapi uvicorn httpx && \
            cat >/app.py <<'PY'
            from fastapi import FastAPI, Request, Response
            import httpx, os

            OPA_URL = os.getenv("OPA_URL", "http://opa:8181/v1/data/envoy/authz")

            app = FastAPI()

            @app.get("/health")
            def health():
                return {"ok": True}

            @app.post("/authz")
            async def authz(req: Request):
                # Envoy ext_authz sends headers; method/path in headers
                method = req.headers.get(":method") or req.headers.get("x-forwarded-method") or req.headers.get("x-envoy-original-method") or "GET"
                path = req.headers.get(":path") or req.headers.get("x-forwarded-uri") or req.headers.get("x-envoy-original-path") or "/"

                payload = {"input": {"attributes": {"request": {"http": {"method": method, "path": path}}}}}

                async with httpx.AsyncClient(timeout=0.3) as client:
                    r = await client.post(OPA_URL, json=payload)

                data = r.json()
                result = data.get("result", {})
                allow = bool(result.get("allow", False))
                approval = bool(result.get("require_approval", False))

                if allow:
                    return Response(status_code=200)

                headers = {
                    "x-dbg-method": method,
                    "x-dbg-path": path,
                }
                if approval:
                    headers["x-approval-required"] = "true"
                return Response(status_code=403, headers=headers)
            PY

            uvicorn app:app --host 0.0.0.0 --port 8000
        env:
        - name: OPA_URL
          value: "http://opa:8181/v1/data/envoy/authz"
---
apiVersion: v1
kind: Service
metadata:
  name: authz-adapter
spec:
  selector:
    app: authz-adapter
  ports:
  - name: http
    port: 8000
    targetPort: 8000
YAML

kubectl -n "$NS" rollout restart deploy/authz-adapter
kubectl -n "$NS" rollout status deploy/authz-adapter
