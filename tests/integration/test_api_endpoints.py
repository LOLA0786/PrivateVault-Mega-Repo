"""
Integration tests for API endpoints (REAL)
"""
import pytest
import httpx
from galani.api.app import app

@pytest.mark.asyncio
class TestAPIEndpoints:
    async def _client(self):
        transport = httpx.ASGITransport(app=app)
        return httpx.AsyncClient(transport=transport, base_url="http://test")

    async def test_intent_analyze_success(self):
        async with await self._client() as client:
            payload = {
                "prompt": "approve a loan of 300000 INR to agent_b",
                "domain": "fintech",
                # toolCall is required as STRING by schema
                "toolCall": "approve_loan",
                "params": {
                    "principal": {"id": "agent_b", "role": "agent"},
                    "context": {"amount": 300000}
                }
            }

            r = await client.post("/v1/intent/analyze", json=payload)
            assert r.status_code in (200, 201)
            body = r.json()
            assert isinstance(body, dict)

    async def test_intent_analyze_missing_body(self):
        async with await self._client() as client:
            r = await client.post("/v1/intent/analyze")
            assert r.status_code in (400, 422)

    async def test_intent_analyze_invalid_payload(self):
        async with await self._client() as client:
            r = await client.post("/v1/intent/analyze", json={"bad": "payload"})
            assert r.status_code == 422
