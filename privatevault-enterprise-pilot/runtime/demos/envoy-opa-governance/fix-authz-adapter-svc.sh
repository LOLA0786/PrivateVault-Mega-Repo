#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" apply -f - <<'YAML'
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

kubectl -n "$NS" get svc authz-adapter -o wide
