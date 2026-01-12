#!/usr/bin/env bash
NS="governance"

echo "Deploying Python Governance Relay..."
kubectl -n $NS apply -f - <<REEOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: governance-relay
spec:
  selector:
    matchLabels:
      app: governance-relay
  template:
    metadata:
      labels:
        app: governance-relay
    spec:
      containers:
      - name: relay
        image: python:3.9-slim
        command: ["sh", "-c"]
        args:
        - "pip install flask redis && python /mnt/relay.py"
        volumeMounts:
        - name: code
          mountPath: /mnt
      volumes:
      - name: code
        configMap:
          name: relay-code
---
apiVersion: v1
kind: Service
metadata:
  name: governance-relay
spec:
  ports:
  - port: 5000
  selector:
    app: governance-relay
REEOF

# Upload the python code into the cluster
kubectl -n $NS create configmap relay-code --from-file=~/PrivateVault-Mega-Repo/governance-relay/relay.py -o yaml --dry-run=client | kubectl apply -f -

echo "Relay is live. Use 'kubectl logs -l app=governance-relay' to watch the lineage grow."
