import pytest
import asyncio
from typing import AsyncGenerator

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_client() -> AsyncGenerator:
    from fastapi.testclient import TestClient
    from api_service import app
    
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_intent():
    return {
        "action_type": "transfer_funds",
        "parameters": {
            "amount": 100000,
            "entity_id": "TEST_001",
            "counterparty": "TEST_002"
        },
        "agent_id": "AGENT_TEST_001",
        "domain": "fintech",
        "context": {}
    }
