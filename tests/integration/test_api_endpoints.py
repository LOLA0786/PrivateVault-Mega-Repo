"""
Integration tests for API endpoints
"""
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
import asyncio

@pytest.mark.asyncio
class TestAPIEndpoints:
    """Test API endpoints end-to-end"""
    
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/health/live")
        assert response.status_code == 200
        assert response.json()['status'] == 'alive'
    
    async def test_login_flow(self, client: AsyncClient):
        """Test complete login flow"""
        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "test_user", "password": "test_pass"}
        )
        assert response.status_code == 200
        token = response.json()['access_token']
        assert token is not None
        
        # Use token to access protected endpoint
        response = await client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()['user_id'] == 'test_user'
    
    async def test_credit_check_flow(self, client: AsyncClient):
        """Test complete credit check flow"""
        # Get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "test_user", "password": "test_pass"}
        )
        token = login_response.json()['access_token']
        
        # Submit credit check
        response = await client.post(
            "/api/v1/credit/check",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "applicant_id": "APP123",
                "amount": 50000.0,
                "term_months": 60
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'risk_score' in result
        assert 0 <= result['risk_score'] <= 1
    
    async def test_rate_limiting(self, client: AsyncClient):
        """Test rate limiting works"""
        # Get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "test_user", "password": "test_pass"}
        )
        token = login_response.json()['access_token']
        
        # Make requests until rate limited
        for i in range(15):
            response = await client.post(
                "/api/v1/credit/check",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "applicant_id": f"APP{i}",
                    "amount": 50000.0,
                    "term_months": 60
                }
            )
            
            if i < 10:
                assert response.status_code == 200
            else:
                # Should be rate limited
                assert response.status_code == 429
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access is blocked"""
        response = await client.post(
            "/api/v1/credit/check",
            json={"applicant_id": "APP123", "amount": 50000.0, "term_months": 60}
        )
        assert response.status_code == 401
    
    async def test_invalid_token(self, client: AsyncClient):
        """Test invalid token is rejected"""
        response = await client.post(
            "/api/v1/credit/check",
            headers={"Authorization": "Bearer invalid_token"},
            json={"applicant_id": "APP123", "amount": 50000.0, "term_months": 60}
        )
        assert response.status_code == 401


@pytest.fixture
async def client():
    """Create test client"""
    from main import app  # Your FastAPI app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
