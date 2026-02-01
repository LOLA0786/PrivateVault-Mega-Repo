# AI Firewall REST API

Production-ready Flask API wrapper for the AI Firewall with authentication, rate limiting, and Prometheus metrics.

## Quick Start

### 1. Setup Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and set your keys
nano .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start API

```bash
# Development
python api.py

# Production (with gunicorn)
gunicorn --bind 0.0.0.0:5000 --workers 4 api:app

# Or use the startup script
./start_api.sh
```

### 4. Test API

```bash
# In another terminal
python test_api.py
```

## Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

### Filter Input (Prompt Injection Detection)
```bash
curl -X POST http://localhost:5000/api/v1/filter/input \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "role": "analyst",
    "prompt": "What is the weather?"
  }'
```

### Authorize Tool Execution
```bash
curl -X POST http://localhost:5000/api/v1/authorize/tool \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "role": "analyst",
    "tool_name": "file_system_read",
    "parameters": {"path": "/data/file.txt"}
  }'
```

### Filter Output (PII Redaction + Drift Detection)
```bash
curl -X POST http://localhost:5000/api/v1/filter/output \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "response": "Contact john@example.com",
    "original_prompt": "Get contact info",
    "actions_taken": [
      {"tool_name": "database_query", "parameters": {}}
    ]
  }'
```

### Get Statistics
```bash
curl http://localhost:5000/api/v1/stats \
  -H "X-API-Key: your-api-key-here"
```

### Prometheus Metrics
```bash
curl http://localhost:5000/metrics
```

## Rate Limits

- Default: 100 requests/hour, 20 requests/minute per IP
- Input filtering: 50 requests/minute
- Tool authorization: 30 requests/minute
- Output filtering: 50 requests/minute

## Integration with PrivateVault

```python
import requests

FIREWALL_URL = "http://localhost:5000"
API_KEY = "your-api-key"

# Before sending to LLM
response = requests.post(
    f"{FIREWALL_URL}/api/v1/filter/input",
    headers={"X-API-Key": API_KEY},
    json={
        "user_id": user.id,
        "role": user.role,
        "prompt": user_prompt
    }
)

if response.json()["status"] == "blocked":
    return "Request blocked due to security policy"

# After LLM response
response = requests.post(
    f"{FIREWALL_URL}/api/v1/filter/output",
    headers={"X-API-Key": API_KEY},
    json={
        "user_id": user.id,
        "response": llm_response,
        "original_prompt": user_prompt,
        "actions_taken": tool_calls
    }
)

filtered_response = response.json()["filtered_response"]
```

## Monitoring

Access Prometheus metrics at `http://localhost:5000/metrics`

Key metrics:
- `ai_firewall_requests_total` - Total requests by endpoint
- `ai_firewall_blocked_inputs_total` - Blocked malicious inputs
- `ai_firewall_drift_detections_total` - Drift detection events
- `ai_firewall_pii_redactions_total` - PII redactions by type

## Production Deployment

1. Set strong `SECRET_KEY` and `API_KEY` in .env
2. Use Redis for rate limiting: `RATELIMIT_STORAGE_URL=redis://redis:6379`
3. Enable HTTPS (use nginx reverse proxy)
4. Set appropriate CORS origins
5. Configure log rotation
6. Monitor metrics with Prometheus + Grafana

## Security

- API key authentication required
- Rate limiting enabled
- CORS restrictions
- Input validation
- Comprehensive logging
- Immutable audit trail
