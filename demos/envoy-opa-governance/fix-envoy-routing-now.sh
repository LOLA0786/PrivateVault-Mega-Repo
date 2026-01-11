#!/usr/bin/env bash
set -euo pipefail
NS="governance"

echo "[1] Overwrite envoy-config with correct routing + ext_authz"
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
YAML

echo "[2] Restart envoy to pick new config"
kubectl -n "$NS" rollout restart deploy/envoy
kubectl -n "$NS" rollout status deploy/envoy

echo "[3] Show live envoy config route cluster target (must be demo_service)"
pkill -f "kubectl -n governance port-forward" || true
kubectl -n "$NS" port-forward svc/envoy 9901:9901 >/tmp/pf-envoy.log 2>&1 &
sleep 2
curl -s http://127.0.0.1:9901/config_dump | grep -n 'cluster": "demo_service' | head -n 5 || true

echo
echo "DONE ✅"
