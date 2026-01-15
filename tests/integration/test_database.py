"""
Integration tests for database operations
"""
import pytest
import socket

def _postgres_running(host="127.0.0.1", port=5432, timeout=0.2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

import asyncpg
from decimal import Decimal

@pytest.mark.asyncio
@pytest.mark.skipif(not _postgres_running(), reason="Postgres not running on localhost:5432")
class TestDatabaseOperations:
    """Test database operations"""
    
    async def test_create_agent(self, db_pool):
        """Test creating an agent in database"""
        async with db_pool.acquire() as conn:
            # Insert agent
            await conn.execute("""
                INSERT INTO agents (agent_id, name, status, permissions)
                VALUES ($1, $2, $3, $4)
            """, 'AGT123', 'Test Agent', 'active', ['credit_check'])
            
            # Verify created
            row = await conn.fetchrow(
                "SELECT * FROM agents WHERE agent_id = $1",
                'AGT123'
            )
            
            assert row['agent_id'] == 'AGT123'
            assert row['name'] == 'Test Agent'
            assert row['status'] == 'active'
    
    async def test_audit_log_immutable(self, db_pool):
        """Test audit log cannot be modified"""
        async with db_pool.acquire() as conn:
            # Insert audit entry
            await conn.execute("""
                INSERT INTO audit_log (agent_id, action, risk_score)
                VALUES ($1, $2, $3)
            """, 'AGT123', 'credit_check', 0.4)
            
            # Try to update (should fail due to WORM)
            with pytest.raises(asyncpg.exceptions.InsufficientPrivilegeError):
                await conn.execute("""
                    UPDATE audit_log
                    SET risk_score = $1
                    WHERE agent_id = $2
                """, 0.5, 'AGT123')
    
    async def test_transaction_rollback(self, db_pool):
        """Test transaction rollback on error"""
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                try:
                    # Insert valid data
                    await conn.execute("""
                        INSERT INTO agents (agent_id, name, status)
                        VALUES ($1, $2, $3)
                    """, 'AGT999', 'Test', 'active')
                    
                    # Insert invalid data (should fail)
                    await conn.execute("""
                        INSERT INTO agents (agent_id, name, status)
                        VALUES ($1, $2, $3)
                    """, 'AGT999', 'Test2', 'active')  # Duplicate ID
                except:
                    pass
            
            # First insert should be rolled back
            row = await conn.fetchrow(
                "SELECT * FROM agents WHERE agent_id = $1",
                'AGT999'
            )
            assert row is None


@pytest.fixture
async def db_pool():
    """Create database connection pool for tests"""
    pool = await asyncpg.create_pool(
        'postgresql://galani:test_password@localhost:5432/galani_test'
    )
    
    # Setup test database
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id VARCHAR(64) PRIMARY KEY,
                name VARCHAR(200),
                status VARCHAR(20),
                permissions TEXT[]
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                agent_id VARCHAR(64),
                action VARCHAR(100),
                risk_score DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
    
    yield pool
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DROP TABLE IF EXISTS agents")
        await conn.execute("DROP TABLE IF EXISTS audit_log")
    
    await pool.close()
