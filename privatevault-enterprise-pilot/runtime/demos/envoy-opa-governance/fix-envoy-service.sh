#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" apply -f - <<'YAML'
apiVersion: v1
kind: Service
metadata:
  name: envoy
spec:
  selector:
    app: envoy
  ports:
    - name: http
      port: 8080
      targetPort: 8080
    - name: admin
      port: 9901
      targetPort: 9901
YAML

kubectl -n "$NS" get svc envoy -o wide
kubectl -n "$NS" get endpoints envoy -o wide
