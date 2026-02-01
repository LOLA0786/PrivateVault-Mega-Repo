#!/usr/bin/env bash
set -euo pipefail

IMAGE="ghcr.io/lola0786/pv-authority-resolver:latest"

docker build -t "${IMAGE}" -f - . <<'DOCKER'
FROM golang:1.22 AS build
WORKDIR /src
COPY . .
RUN go mod download
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /out/resolver ./cmd/pv-authority-resolver

FROM gcr.io/distroless/static:nonroot
COPY --from=build /out/resolver /resolver
EXPOSE 8081
ENTRYPOINT ["/resolver"]
DOCKER

docker push "${IMAGE}"
