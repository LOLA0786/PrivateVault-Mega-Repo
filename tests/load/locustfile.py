"""
Load testing with Locust
"""
from locust import HttpUser, task, between
import random

class GalaniUser(HttpUser):
    """Simulate user behavior"""
    
    wait_time = between(0.5, 2.0)  # Wait 0.5-2 seconds between requests
    
    def on_start(self):
        """Login once at start"""
        response = self.client.post(
            "/api/v1/auth/login",
            json={"username": f"user_{random.randint(1, 100)}", "password": "test"}
        )
        if response.status_code == 200:
            self.token = response.json()['access_token']
        else:
            self.token = None
    
    @task(3)  # 60% of requests
    def credit_check(self):
        """Perform credit check"""
        if not self.token:
            return
        
        self.client.post(
            "/api/v1/credit/check",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "applicant_id": f"APP{random.randint(1000, 9999)}",
                "amount": random.uniform(10000, 500000),
                "term_months": random.choice([12, 24, 36, 48, 60])
            },
            name="/api/v1/credit/check"
        )
    
    @task(1)  # 20% of requests
    def fraud_check(self):
        """Perform fraud detection"""
        if not self.token:
            return
        
        self.client.post(
            "/api/v1/fraud/detect",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "transaction_id": f"TXN{random.randint(10000, 99999)}",
                "amount": random.uniform(10, 10000),
                "merchant": random.choice(["Amazon", "Walmart", "Target"]),
                "card_last4": f"{random.randint(1000, 9999)}"
            },
            name="/api/v1/fraud/detect"
        )
    
    @task(1)  # 20% of requests
    def check_status(self):
        """Check agent status"""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/v1/profile"
        )

# Run load test:
"""
# Install locust
pip install locust

# Run test with 100 users, spawning 10 per second
locust -f tests/load/locustfile.py --users 100 --spawn-rate 10

# View results at http://localhost:8089
"""
