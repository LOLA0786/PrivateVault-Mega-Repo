#!/bin/bash
# Start Galani with all services

set -e

echo "🚀 Starting Galani Protocol v2.0"
echo "================================="
echo ""

# Check if Vault is running
if ! docker ps | grep -q galani-vault; then
    echo "Starting Vault..."
    docker-compose -f docker-compose.vault.yml up -d
    sleep 5
fi

# Check if monitoring is running
if ! docker ps | grep -q galani-prometheus; then
    echo "Starting monitoring stack..."
    docker-compose -f docker-compose.monitoring.yml up -d
    sleep 5
fi

echo ""
echo "Starting Galani application..."
python3 main_vault_integrated.py &
APP_PID=$!

echo ""
echo "Waiting for app to start..."
sleep 3

# Check if app is running
if curl -s http://localhost:8000/health/live > /dev/null 2>&1; then
    echo "✅ Application is running!"
    echo ""
    echo "Access points:"
    echo "  - Application: http://localhost:8000"
    echo "  - API Docs:    http://localhost:8000/docs"
    echo "  - Metrics:     http://localhost:8000/metrics"
    echo "  - Health:      http://localhost:8000/health/ready"
    echo "  - Vault:       http://localhost:8200"
    echo "  - Prometheus:  http://localhost:9090"
    echo "  - Grafana:     http://localhost:3000"
    echo ""
    echo "Run tests with: python3 test_integration.py"
    echo ""
    echo "Press Ctrl+C to stop"
    
    # Wait for interrupt
    trap "kill $APP_PID" INT
    wait $APP_PID
else
    echo "❌ Application failed to start"
    kill $APP_PID
    exit 1
fi
