#!/usr/bin/env bash
set -euo pipefail
NS="governance"

cat <<'YAML' | kubectl apply -n "$NS" -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: opa-policy
data:
  policy.rego: |
    package envoy.authz

    # default deny
    default allow = false
    default require_approval = false

    method := upper(input.attributes.request.http.method)
    path := input.attributes.request.http.path

    # allow safe reads
    allow {
      method == "GET"
    }

    # hard deny destructive action
    deny {
      method == "POST"
      path == "/delete"
    }

    # approval gate
    require_approval {
      method == "POST"
      path == "/deploy"
    }

    # allow only if NOT denied and not approval-required
    allow {
      not deny
      not require_approval
      method == "POST"
      path == "/"
    }
YAML

kubectl -n "$NS" rollout restart deploy/opa
kubectl -n "$NS" rollout status deploy/opa
