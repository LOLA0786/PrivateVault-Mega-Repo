#!/usr/bin/env bash
set -euo pipefail
NS="governance"

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

              route_config:
                name: local_route
                virtual_hosts:
                - name: backend
                  domains: ["*"]
                  routes:
                  - match: { prefix: "/" }
                    route: { cluster: demo_service }

              http_filters:
              - name: envoy.filters.http.router

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

    admin:
      access_log_path: /tmp/admin_access.log
      address:
        socket_address: { address: 0.0.0.0, port_value: 9901 }
YAML

kubectl -n "$NS" rollout restart deploy/envoy
kubectl -n "$NS" rollout status deploy/envoy
kubectl -n "$NS" get pods -l app=envoy -o wide
