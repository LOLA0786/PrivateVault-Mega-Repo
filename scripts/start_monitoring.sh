#!/bin/bash
# Start monitoring stack

set -e

echo "Starting monitoring stack..."

# Install dependencies
pip install -r requirements-monitoring.txt

# Create logs directory
mkdir -p logs

# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

echo "Waiting for services to start..."
sleep 10

echo ""
echo "✅ Monitoring stack started!"
echo ""
echo "Access:"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana:    http://localhost:3000 (admin/admin)"
echo "  - Loki:       http://localhost:3100"
echo ""
echo "Your app metrics: http://localhost:8000/metrics"
echo "Your app health:  http://localhost:8000/health/ready"
