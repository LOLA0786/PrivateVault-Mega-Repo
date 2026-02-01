"""
Health check endpoints for Kubernetes/monitoring
"""

from fastapi import FastAPI, HTTPException
from typing import Dict


class HealthChecker:
    """Check health of all dependencies"""

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
        vault_ok = await self.check_vault()

        return {
            "status": "healthy" if vault_ok else "degraded",
            "checks": {"vault": "ok" if vault_ok else "failed", "application": "ok"},
        }


health_checker = HealthChecker()


def add_health_endpoints(app: FastAPI):
    """Add health check endpoints to FastAPI app"""

    @app.get("/health/live")
    async def liveness():
        """Kubernetes liveness probe"""
        return {"status": "alive"}

    @app.get("/health/ready")
    async def readiness():
        """Kubernetes readiness probe"""
        health = await health_checker.get_health_status()

        if health["status"] != "healthy":
            raise HTTPException(status_code=503, detail=health)

        return health

    @app.get("/health/detailed")
    async def detailed_health():
        """Detailed health check"""
        return await health_checker.get_health_status()
