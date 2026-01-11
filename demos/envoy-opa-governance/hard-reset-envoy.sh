#!/usr/bin/env bash
set -euo pipefail
NS="governance"

# delete envoy deployment entirely
kubectl -n "$NS" delete deploy/envoy --ignore-not-found
sleep 3

# recreate envoy deployment (fresh, guaranteed mounting envoy-config)
cat <<'YAML' | kubectl apply -n "$NS" -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: envoy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: envoy
  template:
    metadata:
      labels:
        app: envoy
    spec:
      containers:
      - name: envoy
        image: envoyproxy/envoy:v1.30-latest
        args: ["-c", "/etc/envoy/envoy.yaml", "--log-level", "info"]
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
          items:
          - key: envoy.yaml
            path: envoy.yaml
YAML

kubectl -n "$NS" rollout status deploy/envoy
kubectl -n "$NS" get pods -l app=envoy -o wide
