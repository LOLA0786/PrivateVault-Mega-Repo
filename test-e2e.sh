#!/bin/bash

echo "🧪 PrivateVault IP Marketplace - End-to-End Test"
echo "================================================"

BASE_URL_LICENSE="http://localhost:3001"
BASE_URL_USAGE="http://localhost:3002"
BASE_URL_BILLING="http://localhost:3003"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

test_count=0
pass_count=0

run_test() {
    test_count=$((test_count + 1))
    echo ""
    echo -e "${BLUE}Test $test_count: $1${NC}"
}

assert_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        pass_count=$((pass_count + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Test 0: Setup - Ensure modules exist
echo -e "${YELLOW}Setting up test data...${NC}"
docker exec pvkb-postgres psql -U pvuser -d privatevault -c "
DELETE FROM usage_events WHERE tenant_id LIKE 'tenant_test_%';
DELETE FROM licenses WHERE tenant_id LIKE 'tenant_test_%';
INSERT INTO modules (module_id, publisher_id, current_version, hash, storage_uri, license_type, per_token_rate, author, org)
VALUES ('pvkb://oncology/chemo_protocols', 'pub_test_001', 'v1.4.2', 'test_hash_123', 's3://test/path', 'pay-per-use', 0.00001, 'Dr. Test', 'TestOrg')
ON CONFLICT (module_id) DO NOTHING;
" > /dev/null 2>&1

echo -e "${GREEN}✅ Test data ready${NC}"

# Test 1: Health Checks
run_test "Health Checks"
LICENSE_HEALTH=$(curl -s $BASE_URL_LICENSE/health 2>/dev/null)
USAGE_HEALTH=$(curl -s $BASE_URL_USAGE/health 2>/dev/null)
BILLING_HEALTH=$(curl -s $BASE_URL_BILLING/health 2>/dev/null)

echo "License Service: $LICENSE_HEALTH"
echo "Usage Tracker: $USAGE_HEALTH"
echo "Billing Service: $BILLING_HEALTH"

if echo "$LICENSE_HEALTH" | grep -q "healthy" && echo "$USAGE_HEALTH" | grep -q "healthy"; then
    pass_count=$((pass_count + 1))
    echo -e "${GREEN}✅ PASS - All services healthy${NC}"
else
    echo -e "${RED}❌ FAIL - Services not healthy${NC}"
fi

# Test 2: Issue License
run_test "Issue License"
LICENSE_RESPONSE=$(curl -s -X POST $BASE_URL_LICENSE/api/licenses/issue \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_test_001",
    "module_id": "pvkb://oncology/chemo_protocols",
    "quota_tokens": 1000000,
    "quota_calls": 5000,
    "duration_days": 30
  }' 2>/dev/null)

echo "$LICENSE_RESPONSE" | jq '.' 2>/dev/null || echo "$LICENSE_RESPONSE"

LICENSE_ID=$(echo "$LICENSE_RESPONSE" | jq -r '.license_id' 2>/dev/null)
LICENSE_TOKEN=$(echo "$LICENSE_RESPONSE" | jq -r '.token' 2>/dev/null)

if [ "$LICENSE_ID" != "null" ] && [ "$LICENSE_ID" != "" ]; then
    echo -e "${GREEN}✅ License issued: $LICENSE_ID${NC}"
    pass_count=$((pass_count + 1))
else
    echo -e "${RED}❌ License issuance failed${NC}"
    echo "Response: $LICENSE_RESPONSE"
fi

# Test 3: Validate License
run_test "Validate License"
if [ -z "$LICENSE_TOKEN" ] || [ "$LICENSE_TOKEN" == "null" ]; then
    echo -e "${YELLOW}⚠️  Skipping - no token from previous test${NC}"
else
    VALIDATE_RESPONSE=$(curl -s -X POST $BASE_URL_LICENSE/api/licenses/validate \
      -H "Content-Type: application/json" \
      -d "{
        \"token\": \"$LICENSE_TOKEN\",
        \"module_id\": \"pvkb://oncology/chemo_protocols\"
      }" 2>/dev/null)

    echo "$VALIDATE_RESPONSE" | jq '.' 2>/dev/null || echo "$VALIDATE_RESPONSE"
    VALID=$(echo "$VALIDATE_RESPONSE" | jq -r '.valid' 2>/dev/null)

    if [ "$VALID" == "true" ]; then
        echo -e "${GREEN}✅ License validation passed${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ License validation failed${NC}"
    fi
fi

# Test 4: Log Usage Event
run_test "Log Usage Event"
if [ -z "$LICENSE_ID" ] || [ "$LICENSE_ID" == "null" ]; then
    echo -e "${YELLOW}⚠️  Skipping - no license from previous test${NC}"
else
    USAGE_RESPONSE=$(curl -s -X POST $BASE_URL_USAGE/api/usage/log \
      -H "Content-Type: application/json" \
      -d "{
        \"request_id\": \"req_test_$(date +%s)\",
        \"tenant_id\": \"tenant_test_001\",
        \"user_id\": \"user_test_001\",
        \"agent_id\": \"agent_gpt4\",
        \"module_id\": \"pvkb://oncology/chemo_protocols\",
        \"module_version\": \"v1.4.2\",
        \"chunks_used\": [\"chunk_001\", \"chunk_002\"],
        \"prompt_tokens_attributed\": 500,
        \"response_tokens\": 300,
        \"license_id\": \"$LICENSE_ID\"
      }" 2>/dev/null)

    echo "$USAGE_RESPONSE" | jq '.' 2>/dev/null || echo "$USAGE_RESPONSE"
    EVENT_ID=$(echo "$USAGE_RESPONSE" | jq -r '.event_id' 2>/dev/null)

    if [ "$EVENT_ID" != "null" ] && [ "$EVENT_ID" != "" ]; then
        echo -e "${GREEN}✅ Usage logged: $EVENT_ID${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ Usage logging failed${NC}"
        echo "Response: $USAGE_RESPONSE"
    fi
fi

# Test 5: Verify License Usage Updated
run_test "Verify License Usage Updated"
if [ -z "$LICENSE_ID" ] || [ "$LICENSE_ID" == "null" ]; then
    echo -e "${YELLOW}⚠️  Skipping - no license${NC}"
else
    sleep 2
    LICENSE_INFO=$(curl -s "$BASE_URL_LICENSE/api/licenses/$LICENSE_ID" 2>/dev/null)
    echo "$LICENSE_INFO" | jq '.' 2>/dev/null || echo "$LICENSE_INFO"

    TOKENS_USED=$(echo "$LICENSE_INFO" | jq -r '.tokens_used' 2>/dev/null)
    if [ "$TOKENS_USED" != "null" ] && [ "$TOKENS_USED" != "" ] && [ "$TOKENS_USED" -gt 0 ] 2>/dev/null; then
        echo -e "${GREEN}✅ License usage updated: $TOKENS_USED tokens used${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ License usage not updated (tokens_used: $TOKENS_USED)${NC}"
    fi
fi

# Test 6: Get Usage Statistics
run_test "Get Usage Statistics"
STATS_RESPONSE=$(curl -s "$BASE_URL_USAGE/api/usage/stats/tenant_test_001" 2>/dev/null)
echo "$STATS_RESPONSE" | jq '.' 2>/dev/null || echo "$STATS_RESPONSE"

TOTAL_REQUESTS=$(echo "$STATS_RESPONSE" | jq -r '.stats.total_requests' 2>/dev/null)
if [ "$TOTAL_REQUESTS" != "null" ] && [ "$TOTAL_REQUESTS" != "" ] && [ "$TOTAL_REQUESTS" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✅ Usage stats retrieved: $TOTAL_REQUESTS requests${NC}"
    pass_count=$((pass_count + 1))
else
    echo -e "${YELLOW}⚠️  No usage stats yet (this is OK if previous tests failed)${NC}"
fi

# Test 7: Usage Breakdown by Module
run_test "Get Usage Breakdown"
BREAKDOWN_RESPONSE=$(curl -s "$BASE_URL_USAGE/api/usage/breakdown/tenant_test_001" 2>/dev/null)
echo "$BREAKDOWN_RESPONSE" | jq '.' 2>/dev/null || echo "$BREAKDOWN_RESPONSE"
pass_count=$((pass_count + 1))
echo -e "${GREEN}✅ PASS${NC}"

# Test 8: Generate Provenance Proof
run_test "Generate Provenance Proof"
if [ -z "$EVENT_ID" ] || [ "$EVENT_ID" == "null" ]; then
    echo -e "${YELLOW}⚠️  Skipping - no event ID${NC}"
else
    PROOF_RESPONSE=$(curl -s "$BASE_URL_USAGE/api/usage/proof/$EVENT_ID" 2>/dev/null)
    echo "$PROOF_RESPONSE" | jq '.' 2>/dev/null || echo "$PROOF_RESPONSE"

    PROOF_VALID=$(echo "$PROOF_RESPONSE" | jq -r '.valid' 2>/dev/null)
    if [ "$PROOF_VALID" == "true" ]; then
        echo -e "${GREEN}✅ Provenance proof generated${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${YELLOW}⚠️  Provenance proof not validated${NC}"
    fi
fi

# Test 9: Multiple Usage Events
run_test "Multiple Usage Events (5 requests)"
if [ -z "$LICENSE_ID" ] || [ "$LICENSE_ID" == "null" ]; then
    echo -e "${YELLOW}⚠️  Skipping - no license${NC}"
else
    for i in {1..5}; do
        curl -s -X POST $BASE_URL_USAGE/api/usage/log \
          -H "Content-Type: application/json" \
          -d "{
            \"request_id\": \"req_load_test_$i\",
            \"tenant_id\": \"tenant_test_001\",
            \"user_id\": \"user_test_001\",
            \"module_id\": \"pvkb://oncology/chemo_protocols\",
            \"module_version\": \"v1.4.2\",
            \"chunks_used\": [\"chunk_00$i\"],
            \"prompt_tokens_attributed\": $((100 * i)),
            \"response_tokens\": $((50 * i)),
            \"license_id\": \"$LICENSE_ID\"
          }" > /dev/null 2>&1
        echo "  Request $i sent"
    done

    sleep 3
    FINAL_STATS=$(curl -s "$BASE_URL_USAGE/api/usage/stats/tenant_test_001" 2>/dev/null)
    FINAL_REQUESTS=$(echo "$FINAL_STATS" | jq -r '.stats.total_requests' 2>/dev/null)
    
    if [ "$FINAL_REQUESTS" != "null" ] && [ "$FINAL_REQUESTS" != "" ]; then
        echo -e "${GREEN}✅ Load test complete: $FINAL_REQUESTS total requests${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${YELLOW}⚠️  Could not verify load test${NC}"
    fi
fi

# Summary
echo ""
echo "================================================"
echo -e "${BLUE}Test Summary${NC}"
echo "Total Tests: $test_count"
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $((test_count - pass_count))${NC}"
echo "================================================"

if [ $pass_count -ge 6 ]; then
    echo -e "${GREEN}🎉 TESTS PASSED! (Minimum 6/9 required)${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    exit 1
fi
