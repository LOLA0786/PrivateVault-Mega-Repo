#!/bin/bash

echo "🔄 Restarting PrivateVault Services..."

# Stop containers
docker-compose down

# Remove old volumes (CAUTION: This deletes all data!)
# docker volume rm privatevault-mega-repo_postgres_data

# Start fresh
docker-compose up -d --build

echo "⏳ Waiting 15 seconds for services to initialize..."
sleep 15

# Check status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🏥 Health Checks:"
curl -s http://localhost:3001/health | jq -C 2>/dev/null || echo "License service not ready"
curl -s http://localhost:3002/health | jq -C 2>/dev/null || echo "Usage tracker not ready"
curl -s http://localhost:3003/health | jq -C 2>/dev/null || echo "Billing service not ready"

echo ""
echo "✅ Services restarted! Run './test-e2e.sh' to verify"
