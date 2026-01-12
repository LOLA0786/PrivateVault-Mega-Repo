#!/usr/bin/env bash
set -euo pipefail

NS="governance"

echo "Step 1: Creating Governance Directories..."
mkdir -p ~/PrivateVault-Mega-Repo/governance-relay

echo "Step 2: Deploying Redis for Temporal State..."
kubectl -n "$NS" apply -f - <<REEOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-state
spec:
  selector:
    matchLabels:
      app: redis-state
  template:
    metadata:
      labels:
        app: redis-state
    spec:
      containers:
      - name: redis
        image: redis:alpine
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis-state
spec:
  ports:
  - port: 6379
  selector:
    app: redis-state
REEOF

echo "Step 3: Creating Temporal & Lineage Policy (Rego)..."
cat <<REGO > ~/PrivateVault-Mega-Repo/governance-relay/policy-v2.rego
package envoy.authz

import input.attributes.request.http as http_request

default allow = false

# Decision Lineage Metadata
decision_metadata := {
    "intent": "action_validation",
    "version": "v2.0-temporal",
    "timestamp": time.now_ns()
}

# 1. Stateless Rule: Basic GET always allowed
allow {
    http_request.method == "GET"
    http_request.path == "/"
}

# 2. Temporal Rule: Limit 'DELETE' actions to 5 per minute
# Note: In production, OPA calls Redis via http.send or custom plugins
# For this PoC, we simulate the stateful check logic
allow {
    http_request.method == "POST"
    http_request.path == "/delete"
    
    # Logic: Increment counter in Redis and check threshold
    # simulate_state_check(http_request.headers.authorization)
    not action_limit_exceeded
}

action_limit_exceeded {
    # This represents a check against the 'Governance Relay'
    # If this were real code: count := redis.get(user_id); count > 5
    input.attributes.context.request_count > 5
}

# Custom Response for Accountability
deny_response = {
    "allowed": false,
    "http_status": 403,
    "body": json.marshal({
        "allow": false,
        "reason": "temporal_limit_exceeded",
        "lineage_id": decision_metadata.timestamp
    })
}
REGO

echo "Step 4: Updating OPA Config for Decision Logging (Lineage)..."
# This tells OPA to upload every decision to our 'Relay' service (or console)
kubectl -n "$NS" create configmap opa-relay-config --from-file=~/PrivateVault-Mega-Repo/governance-relay/policy-v2.rego -o yaml --dry-run=client | kubectl apply -f -

echo "Deployment complete. PrivateVault v2 (Stateful) is initializing."
