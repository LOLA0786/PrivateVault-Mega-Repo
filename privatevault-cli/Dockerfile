# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go mod download
RUN CGO_ENABLED=0 GOOS=linux go build -o privatevault .

# Final stage
FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/privatevault /usr/local/bin/privatevault
ENTRYPOINT ["privatevault"]
CMD ["--help"]
