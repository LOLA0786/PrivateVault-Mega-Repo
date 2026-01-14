"""Tool Authorization & Action Signing"""
import jwt
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolAuthorization:
    def __init__(self, secret_key: str = "demo-secret-key-change-me"):
        self.secret_key = secret_key
        self.policies = self._load_default_policies()
        self.violation_count = 0
    
    def _load_default_policies(self) -> Dict:
        return {
            "admin": {
                "allowed_tools": ["file_system_read", "file_system_write", 
                                 "database_query", "shell_execute"],
                "default": "allow"
            },
            "analyst": {
                "allowed_tools": ["file_system_read", "database_query", 
                                 "report_generation"],
                "default": "deny"
            },
            "viewer": {
                "allowed_tools": ["file_system_read", "report_view"],
                "default": "deny"
            }
        }
    
    def generate_action_signature(self, user_id: str, role: str, 
                                   tool_name: str, parameters: Dict) -> str:
        payload = {
            "user_id": user_id,
            "role": role,
            "tool": tool_name,
            "params_hash": hashlib.sha256(
                json.dumps(parameters, sort_keys=True).encode()
            ).hexdigest(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        logger.info(f"🔐 Signed action: {user_id} -> {tool_name}")
        return token
    
    def verify_action_signature(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            logger.info(f"✅ Signature verified")
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Signature expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid signature")
    
    def is_tool_authorized(self, user_role: str, tool_name: str) -> bool:
        if user_role not in self.policies:
            return False
        
        policy = self.policies[user_role]
        allowed = tool_name in policy["allowed_tools"]
        
        if not allowed:
            self.violation_count += 1
            logger.warning(f"🚫 UNAUTHORIZED: {user_role} -> {tool_name}")
        
        return allowed
    
    def execute_tool_with_auth(self, user_id: str, role: str, 
                                tool_name: str, parameters: Dict) -> Dict:
        result = {
            "authorized": False,
            "executed": False,
            "signature": None,
            "result": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if not self.is_tool_authorized(role, tool_name):
            result["error"] = f"Role '{role}' not authorized for '{tool_name}'"
            return result
        
        result["authorized"] = True
        
        signature = self.generate_action_signature(user_id, role, tool_name, parameters)
        result["signature"] = signature
        
        try:
            self.verify_action_signature(signature)
            result["executed"] = True
            result["result"] = {"status": "success", "message": f"{tool_name} executed"}
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_violation_count(self) -> int:
        return self.violation_count

if __name__ == "__main__":
    auth = ToolAuthorization()
    
    print("\n" + "="*50)
    print("TEST 1: Admin - Authorized")
    print("="*50)
    result = auth.execute_tool_with_auth("admin_001", "admin", "database_query", {})
    print(json.dumps({k: v for k, v in result.items() if k != 'signature'}, indent=2))
    
    print("\n" + "="*50)
    print("TEST 2: Analyst - Unauthorized")
    print("="*50)
    result = auth.execute_tool_with_auth("analyst_002", "analyst", "shell_execute", {})
    print(json.dumps({k: v for k, v in result.items() if k != 'signature'}, indent=2))
    
    print(f"\nViolations: {auth.get_violation_count()}")
