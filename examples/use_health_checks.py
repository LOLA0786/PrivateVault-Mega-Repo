"""
Example: How to add health checks to your app
"""

from fastapi import FastAPI
from monitoring.health.health_check import add_health_endpoints

app = FastAPI()

# Add health check endpoints
add_health_endpoints(app)

# Now you have three health endpoints:
# 1. http://localhost:8000/health/live    - Liveness probe
# 2. http://localhost:8000/health/ready   - Readiness probe
# 3. http://localhost:8000/health/detailed - Detailed status

# Test with curl:
"""
# Liveness
curl http://localhost:8000/health/live
# Response: {"status": "alive"}

# Readiness
curl http://localhost:8000/health/ready
# Response: {"status": "healthy", "checks": {...}}

# Detailed
curl http://localhost:8000/health/detailed
# Response: Full health status of all dependencies
"""

# Use in Kubernetes:
"""
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: galani
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
"""
