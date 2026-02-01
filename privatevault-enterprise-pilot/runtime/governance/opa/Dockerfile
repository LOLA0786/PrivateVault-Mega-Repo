# ==========================
# Stage 1: Build WASM bundle
# ==========================
FROM alpine:3.20 AS builder

RUN apk add --no-cache curl

WORKDIR /app

# Copy policy sources
COPY policy/policy.rego /app/policy.rego
COPY policy/data.json /app/data.json

# Download OPA static binary (linux amd64)
RUN curl -sSL -o /usr/local/bin/opa \
    https://openpolicyagent.org/downloads/latest/opa_linux_amd64_static && \
    chmod +x /usr/local/bin/opa

# Compile Rego -> WASM bundle
RUN opa build -t wasm -e privatevault/authz/decision /app/policy.rego


# ==========================
# Stage 2: Runtime OPA server
# ==========================
FROM openpolicyagent/opa:0.63.0

WORKDIR /app

# Copy compiled WASM bundle from builder stage
COPY --from=builder /app/bundle.tar.gz /app/bundle.tar.gz
COPY --from=builder /app/data.json /app/data.json

# Run OPA server with bundle
CMD ["run", "--server", "--addr=0.0.0.0:8181", "--log-level=info", "/app/bundle.tar.gz", "/app/data.json"]
