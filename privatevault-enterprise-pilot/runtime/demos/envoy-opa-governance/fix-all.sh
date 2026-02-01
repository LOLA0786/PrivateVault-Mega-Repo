#!/usr/bin/env bash
set -euo pipefail
NS="governance"

echo "[0] Cleanup old"
kubectl delete ns "$NS" --ignore-not-found=true
sleep 5
kubectl create ns "$NS"

echo "[1] Deploy demo upstream (always returns OK_FROM_DEMO)"
cat <<'YAML' | kubectl apply -n "$NS" -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo
spec:
  replicas: 1
  selector:
    matchLabels: { app: demo }
  template:
    metadata:
      labels: { app: demo }
    spec:
      containers:
      - name: demo
        image: hashicorp/http-echo:1.0.0
        args: ["-text=OK_FROM_DEMO","-listen=:9000"]
        ports:
        - containerPort: 9000
---
apiVersion: v1
kind: Service
metadata:
  name: demo
spec:
  selector: { app: demo }
  ports:
  - name: http
    port: 9000
    targetPort: 9000
YAML

echo "[2] Deploy OPA with correct policy"
cat <<'YAML' | kubectl apply -n "$NS" -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: opa-policy
data:
  policy.rego: |
    package envoy.authz

    default allow = false
    default deny = false
    default require_approval = false

    # allow simple read
    allow {
      input.attributes.request.http.method == "GET"
      input.attributes.request.http.path == "/"
    }

    # delete is blocked
    deny {
      input.attributes.request.http.method == "POST"
      input.attributes.request.http.path == "/delete"
    }

    # deploy requires approval
    require_approval {
      input.attributes.request.http.method == "POST"
      input.attributes.request.http.path == "/deploy"
    }

    allow {
      not deny
      not require_approval
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opa
spec:
  replicas: 1
  selector:
    matchLabels: { app: opa }
  template:
    metadata:
      labels: { app: opa }
    spec:
      containers:
      - name: opa
        image: openpolicyagent/opa:latest
        args:
          - "run"
          - "--server"
          - "--addr=0.0.0.0:8181"
          - "--set=decision_logs.console=true"
          - "/policies/policy.rego"
        ports:
          - containerPort: 8181
        volumeMounts:
          - name: policy
            mountPath: /policies
      volumes:
        - name: policy
          configMap:
            name: opa-policy
---
apiVersion: v1
kind: Service
metadata:
  name: opa
spec:
  selector: { app: opa }
  ports:
  - name: http
    port: 8181
    targetPort: 8181
YAML

echo "[3] Deploy REAL authz-adapter (translator) on port 8000 with /authz"
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
            import httpx

            OPA_URL = "http://opa:8181/v1/data/envoy/authz"
            app = FastAPI()

            @app.get("/health")
            def health():
                return {"ok": True}

            @app.post("/authz")
            async def authz(req: Request):
                method = req.headers.get(":method") or req.headers.get("x-forwarded-method") or "GET"
                path = req.headers.get(":path") or req.headers.get("x-forwarded-uri") or "/"

                payload = {"input": {"attributes": {"request": {"http": {"method": method, "path": path}}}}}

                async with httpx.AsyncClient(timeout=0.5) as client:
                    r = await client.post(OPA_URL, json=payload)

                data = r.json()
                result = data.get("result", {})
                allow = bool(result.get("allow", False))
                approval = bool(result.get("require_approval", False))
                denied = bool(result.get("deny", False))

                if allow:
                    return Response(status_code=200)

                headers = {
                    "x-dbg-method": method,
                    "x-dbg-path": path,
                }
                if approval:
                    headers["x-approval-required"] = "true"
                reason = "denied" if denied else ("approval_required" if approval else "blocked")
                return Response(status_code=403, headers=headers, content=f'{{"allowed":false,"reason":"{reason}"}}')
            PY
            uvicorn app:app --host 0.0.0.0 --port 8000
---
apiVersion: v1
kind: Service
metadata:
  name: authz-adapter
spec:
  selector: { app: authz-adapter }
  ports:
  - name: http
    port: 8000
    targetPort: 8000
YAML

echo "[4] Deploy ENVOY with correct: route -> demo, ext_authz -> adapter"
cat <<'YAML' | kubectl apply -n "$NS" -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: envoy-config
data:
  envoy.yaml: |
    static_resources:
      listeners:
      - name: listener_http
        address:
          socket_address: { address: 0.0.0.0, port_value: 8080 }
        filter_chains:
        - filters:
          - name: envoy.filters.network.http_connection_manager
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
              stat_prefix: ingress_http
              normalize_path: true
              route_config:
                name: local_route
                virtual_hosts:
                - name: backend
                  domains: ["*"]
                  routes:
                  - match: { prefix: "/" }
                    route: { cluster: demo_service }
              http_filters:
              - name: envoy.filters.http.ext_authz
                typed_config:
                  "@type": type.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
                  transport_api_version: V3
                  failure_mode_allow: false
                  status_on_error: { code: Forbidden }
                  http_service:
                    server_uri:
                      uri: http://authz-adapter:8000
                      cluster: authz_adapter
                      timeout: 0.5s
                    path_prefix: "/authz"
                    authorization_request:
                      allowed_headers:
                        patterns:
                        - exact: ":method"
                        - exact: ":path"
                        - exact: "x-forwarded-uri"
                        - exact: "x-forwarded-method"
                        - exact: "authorization"
              - name: envoy.filters.http.router
                typed_config:
                  "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
      clusters:
      - name: demo_service
        connect_timeout: 0.25s
        type: STRICT_DNS
        lb_policy: ROUND_ROBIN
        load_assignment:
          cluster_name: demo_service
          endpoints:
          - lb_endpoints:
            - endpoint:
                address:
                  socket_address: { address: demo, port_value: 9000 }
      - name: authz_adapter
        connect_timeout: 0.25s
        type: STRICT_DNS
        lb_policy: ROUND_ROBIN
        load_assignment:
          cluster_name: authz_adapter
          endpoints:
          - lb_endpoints:
            - endpoint:
                address:
                  socket_address: { address: authz-adapter, port_value: 8000 }
    admin:
      access_log_path: /tmp/admin_access.log
      address:
        socket_address: { address: 0.0.0.0, port_value: 9901 }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: envoy
spec:
  replicas: 1
  selector:
    matchLabels: { app: envoy }
  template:
    metadata:
      labels: { app: envoy }
    spec:
      containers:
      - name: envoy
        image: envoyproxy/envoy:v1.30.2
        args: ["-c","/etc/envoy/envoy.yaml","--log-level","info"]
        ports:
        - containerPort: 8080
        - containerPort: 9901
        volumeMounts:
        - name: config
          mountPath: /etc/envoy
      volumes:
      - name: config
        configMap:
          name: envoy-config
---
apiVersion: v1
kind: Service
metadata:
  name: envoy
spec:
  selector: { app: envoy }
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  - name: admin
    port: 9901
    targetPort: 9901
YAML

echo "[5] Wait rollouts"
kubectl -n "$NS" rollout status deploy/demo
kubectl -n "$NS" rollout status deploy/opa
kubectl -n "$NS" rollout status deploy/authz-adapter
kubectl -n "$NS" rollout status deploy/envoy

echo
echo "✅ DONE. Run tests:"
echo "kubectl -n governance run curl --rm -i --restart=Never --image=curlimages/curl:8.5.0 -- sh -lc '"
echo "  curl -i http://envoy:8080/ ; echo"
echo "  curl -i -XPOST http://envoy:8080/delete ; echo"
echo "  curl -i -XPOST http://envoy:8080/deploy ; echo"
echo "'"
