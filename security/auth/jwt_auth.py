"""
JWT-based authentication for all API endpoints
"""

import os
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Get JWT secret from Vault (not hardcoded!)
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_THIS_IN_PRODUCTION")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

security = HTTPBearer()


class AuthManager:
    """Manage JWT tokens and authentication"""

    @staticmethod
    def create_token(user_id: str, agent_id: str, permissions: list) -> str:
        """
        Create JWT token

        Args:
            user_id: User identifier
            agent_id: Agent identifier
            permissions: List of permissions ['credit_check', 'fraud_detect']

        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "agent_id": agent_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verify JWT token

        Returns:
            Decoded token payload

        Raises:
            HTTPException if token invalid
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """
    FastAPI dependency to get current authenticated user

    Usage:
        @app.get("/protected")
        def protected_route(user: Dict = Depends(get_current_user)):
            return {"user_id": user['user_id']}
    """
    token = credentials.credentials
    return AuthManager.verify_token(token)


async def require_permission(permission: str):
    """
    FastAPI dependency to require specific permission

    Usage:
        @app.post("/credit/check")
        def credit_check(user: Dict = Depends(require_permission('credit_check'))):
            ...
    """

    async def permission_checker(
        credentials: HTTPAuthorizationCredentials = Security(security),
    ):
        user = AuthManager.verify_token(credentials.credentials)

        if permission not in user.get("permissions", []):
            raise HTTPException(
                status_code=403, detail=f"Missing required permission: {permission}"
            )

        return user

    return permission_checker
