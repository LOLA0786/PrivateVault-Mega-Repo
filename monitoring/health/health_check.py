"""
Health check endpoints for Kubernetes/monitoring
"""
from fastapi import FastAPI, HTTPException
import asyncio
import aioredis
import asyncpg
from typing import Dict

class HealthChecker:
    """Check health of all dependencies"""
    
    def __init__(self):
        self.redis_client = None
        self.db_pool = None
    
    async def check_redis(self) -> bool:
        """Check Redis connection"""
        try:
            if not self.redis_client:
                self.redis_client = await aioredis.from_url('redis://localhost')
            
            await self.redis_client.ping()
            return True
        except:
            return False
    
    async def check_database(self) -> bool:
        """Check PostgreSQL connection"""
        try:
            if not self.db_pool:
                self.db_pool = await asyncpg.create_pool(
                    'postgresql://galani:password@localhost/galani'
                )
            
            async with self.db_pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
            return True
        except:
            return False
    
    async def check_vault(self) -> bool:
        """Check Vault connection"""
        try:
            from security.secrets.secrets_manager import get_secrets_manager
            secrets = get_secrets_manager()
            return secrets.client.is_authenticated()
        except:
            return False
    
    async def get_health_status(self) -> Dict:
        """Get complete health status"""
        redis_ok = await self.check_redis()
        db_ok = await self.check_database()
        vault_ok = await self.check_vault()
        
        all_healthy = redis_ok and db_ok and vault_ok
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": {
                "redis": "ok" if redis_ok else "failed",
                "database": "ok" if db_ok else "failed",
                "vault": "ok" if vault_ok else "failed"
            }
        }

health_checker = HealthChecker()

def add_health_endpoints(app: FastAPI):
    """Add health check endpoints to FastAPI app"""
    
    @app.get("/health/live")
    async def liveness():
        """
        Kubernetes liveness probe
        Returns 200 if service is running
        """
        return {"status": "alive"}
    
    @app.get("/health/ready")
    async def readiness():
        """
        Kubernetes readiness probe
        Returns 200 only if all dependencies are healthy
        """
        health = await health_checker.get_health_status()
        
        if health["status"] != "healthy":
            raise HTTPException(status_code=503, detail=health)
        
        return health
    
    @app.get("/health/detailed")
    async def detailed_health():
        """
        Detailed health check for debugging
        """
        return await health_checker.get_health_status()
