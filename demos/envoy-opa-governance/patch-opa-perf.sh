#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" patch deploy/opa --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/resources","value":{
    "requests":{"cpu":"500m","memory":"256Mi"},
    "limits":{"cpu":"2000m","memory":"512Mi"}
  }}
]' 2>/dev/null || true

kubectl -n "$NS" rollout restart deploy/opa
kubectl -n "$NS" rollout status deploy/opa
