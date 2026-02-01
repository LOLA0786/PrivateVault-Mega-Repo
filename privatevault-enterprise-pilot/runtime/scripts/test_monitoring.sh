#!/bin/bash
# Test that monitoring is working

set -e

echo "Testing monitoring setup..."

# Test 1: Check if Prometheus is up
echo "1. Testing Prometheus..."
if curl -s http://localhost:9090/-/healthy | grep -q "Prometheus"; then
    echo "   ✅ Prometheus is healthy"
else
    echo "   ❌ Prometheus is not responding"
    exit 1
fi

# Test 2: Check if Grafana is up
echo "2. Testing Grafana..."
if curl -s http://localhost:3000/api/health | grep -q "ok"; then
    echo "   ✅ Grafana is healthy"
else
    echo "   ❌ Grafana is not responding"
    exit 1
fi

# Test 3: Check if metrics endpoint works
echo "3. Testing metrics endpoint..."
if curl -s http://localhost:8000/metrics | grep -q "galani"; then
    echo "   ✅ Metrics endpoint is working"
else
    echo "   ❌ Metrics endpoint is not working"
    exit 1
fi

# Test 4: Check health endpoints
echo "4. Testing health endpoints..."
if curl -s http://localhost:8000/health/live | grep -q "alive"; then
    echo "   ✅ Liveness check working"
else
    echo "   ❌ Liveness check failed"
    exit 1
fi

echo ""
echo "✅ All monitoring tests passed!"
