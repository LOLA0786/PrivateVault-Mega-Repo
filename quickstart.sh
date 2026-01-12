#!/bin/bash

echo "🚀 PrivateVault IP Marketplace - Quick Start"
echo "============================================"

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down

# Build and start all services
echo "Building and starting services..."
docker-compose up --build -d

# Wait for services
echo "Waiting for services to be ready..."
sleep 10

# Check health
echo ""
echo "📋 Service Health Check:"
curl -s http://localhost:3001/health | jq
curl -s http://localhost:3002/health | jq
curl -s http://localhost:3003/health | jq

echo ""
echo "✅ All services are running!"
echo ""
echo "📚 Available endpoints:"
echo "  License Service:  http://localhost:3001"
echo "  Usage Tracker:    http://localhost:3002"
echo "  Billing Service:  http://localhost:3003"
echo ""
echo "Run './test-e2e.sh' to verify end-to-end functionality"
