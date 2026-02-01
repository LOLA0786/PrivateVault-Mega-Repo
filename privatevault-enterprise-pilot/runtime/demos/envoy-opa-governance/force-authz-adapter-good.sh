#!/usr/bin/env bash
set -euo pipefail
NS=governance

# 1) python app source (REAL ext_authz behavior)
cat <<'PY' > /tmp/main.py
from fastapi import FastAPI, Request, Response
import httpx
import os

OPA_URL = os.environ.get("OPA_URL", "http://opa:8181/v1/data/envoy/authz")

app = FastAPI()

@app.post("/authz")
async def authz(req: Request):
    headers = req.headers
    method = headers.get("x-forwarded-method") or headers.get(":method") or "GET"
    path   = headers.get("x-forwarded-uri") or headers.get(":path") or "/"

    payload = {
        "input": {
            "attributes": {
                "request": {
                    "http": {
                        "method": method,
                        "path": path
                    }
                }
            }
        }
    }

    async with httpx.AsyncClient(timeout=1.0) as client:
        r = await client.post(OPA_URL, json=payload)
        data = r.json()

    result = data.get("result", {})
    allow = bool(result.get("allow", False))
    require_approval = bool(result.get("require_approval", False))

    if allow:
        return Response(status_code=200)

    resp = Response(status_code=403)
    if require_approval:
        resp.headers["x-approval-required"] = "true"
    return resp
PY

# 2) configmap for code
kubectl -n "$NS" delete cm authz-adapter-code --ignore-not-found
kubectl -n "$NS" create cm authz-adapter-code --from-file=main.py=/tmp/main.py

# 3) deploy adapter on 8000, /authz POST
kubectl -n "$NS" delete deploy authz-adapter --ignore-not-found
kubectl -n "$NS" apply -f - <<YAML
apiVersion: apps/v1
kind: Deployment
metadata:
  name: authz-adapter
  namespace: $NS
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
        env:
        - name: OPA_URL
          value: "http://opa:8181/v1/data/envoy/authz"
        command: ["sh","-lc"]
        args:
        - |
          pip install --no-cache-dir fastapi uvicorn httpx >/dev/null
          uvicorn main:app --host 0.0.0.0 --port 8000
        workingDir: /app
        volumeMounts:
        - name: code
          mountPath: /app/main.py
          subPath: main.py
      volumes:
      - name: code
        configMap:
          name: authz-adapter-code
---
apiVersion: v1
kind: Service
metadata:
  name: authz-adapter
  namespace: $NS
spec:
  selector:
    app: authz-adapter
  ports:
  - name: http
    port: 8000
    targetPort: 8000
YAML

kubectl -n "$NS" rollout status deploy/authz-adapter

# 4) restart envoy so ext_authz reconnects cleanly
kubectl -n "$NS" rollout restart deploy/envoy
kubectl -n "$NS" rollout status deploy/envoy

echo "✅ authz-adapter fixed (real ext_authz) + envoy restarted"
