#!/bin/bash

echo "🔍 PrivateVault Debug Information"
echo "================================="

echo ""
echo "📦 Docker Containers:"
docker-compose ps

echo ""
echo "📊 Database Status:"
docker exec pvkb-postgres psql -U pvuser -d privatevault -c "
SELECT 
  'modules' as table_name, COUNT(*) as count FROM modules
UNION ALL
SELECT 'licenses', COUNT(*) FROM licenses
UNION ALL
SELECT 'usage_events', COUNT(*) FROM usage_events;
"

echo ""
echo "📝 Recent Logs:"
echo "--- License Service ---"
docker logs --tail 20 pvkb-license-service

echo ""
echo "--- Usage Tracker ---"
docker logs --tail 20 pvkb-usage-tracker

echo ""
echo "--- Billing Service ---"
docker logs --tail 20 pvkb-billing-service

echo ""
echo "🔧 Sample Modules in DB:"
docker exec pvkb-postgres psql -U pvuser -d privatevault -c "
SELECT module_id, publisher_id, license_type, per_token_rate FROM modules LIMIT 5;
"

echo ""
echo "🎫 Active Licenses:"
docker exec pvkb-postgres psql -U pvuser -d privatevault -c "
SELECT license_id, tenant_id, module_id, status, tokens_used, quota_tokens FROM licenses LIMIT 5;
"
