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
  replicas: 2
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
        resources:
          requests:
            cpu: "500m"
            memory: "256Mi"
          limits:
            cpu: "2000m"
            memory: "512Mi"
        env:
          - name: OPA_URL
            value: "http://opa:8181"
          - name: WORKERS
            value: "4"
        command: ["/bin/bash","-lc"]
        args:
          - |
            set -e
            pip install --no-cache-dir fastapi uvicorn httpx >/dev/null

            cat >/app.py <<'PY'
            from fastapi import FastAPI, Request
            from fastapi.responses import JSONResponse
            import httpx, os, time
            from collections import OrderedDict

            OPA = os.getenv("OPA_URL","http://opa:8181")
            app = FastAPI()

            # ---- tiny LRU cache for low-risk GET decisions ----
            # caches allow decisions for (method,path) for TTL seconds
            CACHE_TTL = 2.0
            CACHE_SIZE = 2048
            _cache = OrderedDict()  # key -> (expires_at, decision_dict)

            def cache_get(key):
                now = time.time()
                v = _cache.get(key)
                if not v:
                    return None
                exp, decision = v
                if exp < now:
                    _cache.pop(key, None)
                    return None
                _cache.move_to_end(key)
                return decision

            def cache_put(key, decision):
                exp = time.time() + CACHE_TTL
                _cache[key] = (exp, decision)
                _cache.move_to_end(key)
                while len(_cache) > CACHE_SIZE:
                    _cache.popitem(last=False)

            # ---- pooled http client (keepalive) ----
            limits = httpx.Limits(max_keepalive_connections=100, max_connections=400)
            timeout = httpx.Timeout(connect=0.2, read=0.8, write=0.2, pool=0.2)
            client = httpx.AsyncClient(limits=limits, timeout=timeout)

            def first(*vals):
                for v in vals:
                    if v and str(v).strip():
                        return str(v)
                return ""

            def detect(req: Request):
                h = {k.lower(): v for k,v in req.headers.items()}
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
                return method, path, h

            async def opa_decide(method: str, path: str, headers: dict):
                # cache ONLY safe reads
                if method == "GET":
                    key = f"{method}:{path}"
                    cached = cache_get(key)
                    if cached is not None:
                        return cached

                inp = {
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

                r = await client.post(f"{OPA}/v1/data/envoy/authz", json={"input": inp})
                r.raise_for_status()
                decision = r.json().get("result", {})

                if method == "GET":
                    cache_put(f"{method}:{path}", decision)

                return decision

            @app.api_route("/{full_path:path}", methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
            async def catch_all(req: Request, full_path: str):
                try:
                    method, path, headers = detect(req)
                    decision = await opa_decide(method, path, headers)

                    allow = bool(decision.get("allow", False))
                    require_approval = bool(decision.get("require_approval", False))

                    if require_approval:
                        return JSONResponse(
                            status_code=403,
                            content={"allowed": False, "reason": "approval_required"},
                            headers={"x-approval-required":"true"}
                        )
                    if allow:
                        return JSONResponse(status_code=200, content={"allowed": True})
                    return JSONResponse(status_code=403, content={"allowed": False, "reason": "denied"})

                except Exception as e:
                    # FAIL CLOSED
                    return JSONResponse(
                        status_code=403,
                        content={"allowed": False, "reason": "authz_error", "error": str(e)}
                    )
            PY

            # multi-worker uvicorn
            exec python -m uvicorn app:app --host 0.0.0.0 --port 8000 --workers ${WORKERS}
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
kubectl -n "$NS" get pods -l app=authz-adapter -o wide
