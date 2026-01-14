"""
Prometheus metrics for monitoring
"""
from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# Request metrics
request_count = Counter(
    'galani_requests_total',
    'Total requests processed',
    ['endpoint', 'method', 'status']
)

request_duration = Histogram(
    'galani_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0]
)

# Business metrics
risk_decisions = Counter(
    'galani_risk_decisions_total',
    'Risk decisions made',
    ['decision_type', 'risk_level']
)

# System metrics
active_agents = Gauge(
    'galani_active_agents',
    'Number of active agents'
)

ledger_size = Gauge(
    'galani_ledger_blocks_total',
    'Total audit blocks in ledger'
)

# Application info
app_info = Info(
    'galani_application',
    'Application information'
)
app_info.info({
    'version': '2.0',
    'environment': 'production'
})

def track_request_metrics(endpoint: str):
    """Decorator to track request metrics"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                # Record metrics
                duration = time.time() - start_time
                request_count.labels(
                    endpoint=endpoint,
                    method='POST',
                    status=status
                ).inc()
                request_duration.labels(endpoint=endpoint).observe(duration)
        
        return wrapper
    return decorator

def record_risk_decision(decision_type: str, risk_score: float):
    """Record a risk decision metric"""
    if risk_score < 0.3:
        risk_level = 'low'
    elif risk_score < 0.7:
        risk_level = 'medium'
    else:
        risk_level = 'high'
    
    risk_decisions.labels(
        decision_type=decision_type,
        risk_level=risk_level
    ).inc()
