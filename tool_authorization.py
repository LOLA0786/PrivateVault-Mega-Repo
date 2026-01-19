"""
Tool Authorization & Action Signing
JWT-based identity binding for LLM tool calls
"""
import jwt
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolAuthorization:
    def __init__(self, secret_key: str = "your-secret-key-change-in-production"):
        self.secret_key = secret_key
        self.policies = self._load_default_policies()
        self.violation_count = 0
    
    def _load_default_policies(self) -> Dict:
        """Default role-based tool access policies"""
        return {
            "admin": {
                "allowed_tools": [
                    "file_system_read",
                    "file_system_write",
                    "database_query",
                    "database_write",
                    "external_api_call",
                    "shell_execute"
                ],
                "default": "allow"
            },
            "analyst": {
                "allowed_tools": [
                    "file_system_read",
                    "database_query",
                    "report_generation",
                    "external_api_call"
                ],
                "default": "deny"
            },
            "viewer": {
                "allowed_tools": [
                    "file_system_read",
                    "report_view"
                ],
                "default": "deny"
            },
            "guest": {
                "allowed_tools": [],
                "default": "deny"
            }
        }
    
    def generate_action_signature(self, user_id: str, role: str, 
                                   tool_name: str, parameters: Dict) -> str:
        """Generate JWT signature for tool execution"""
        payload = {
            "user_id": user_id,
            "role": role,
            "tool": tool_name,
            "params_hash": hashlib.sha256(
                json.dumps(parameters, sort_keys=True).encode()
            ).hexdigest(),
            "timestamp": datetime.utcnow().isoformat(),
            "exp": datetime.utcnow() + timedelta(minutes=5)  # 5 min expiry
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        logger.info(f"🔐 Generated signature for {user_id} -> {tool_name}")
        return token
    
    def verify_action_signature(self, token: str) -> Dict:
        """Verify JWT signature"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            logger.info(f"✅ Signature verified for user {payload['user_id']}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("❌ Signature expired")
            raise Exception("Action signature expired")
        except jwt.InvalidTokenError:
            logger.error("❌ Invalid signature")
            raise Exception("Invalid action signature")
    
    def is_tool_authorized(self, user_role: str, tool_name: str) -> bool:
        """Check if role is authorized to use tool"""
        if user_role not in self.policies:
            logger.warning(f"⚠️  Unknown role: {user_role}")
            return False
        
        policy = self.policies[user_role]
        allowed = tool_name in policy["allowed_tools"]
        
        if not allowed:
            self.violation_count += 1
            logger.warning(
                f"🚫 UNAUTHORIZED: {user_role} attempted to use {tool_name}"
            )
        
        return allowed
    
    def execute_tool_with_auth(self, user_id: str, role: str, 
                                tool_name: str, parameters: Dict) -> Dict:
        """Execute tool with authorization check and signing"""
        result = {
            "authorized": False,
            "executed": False,
            "signature": None,
            "result": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check authorization
        if not self.is_tool_authorized(role, tool_name):
            result["error"] = f"Role '{role}' not authorized for tool '{tool_name}'"
            return result
        
        result["authorized"] = True
        
        # Generate signature
        signature = self.generate_action_signature(user_id, role, tool_name, parameters)
        result["signature"] = signature
        
        # Simulate tool execution (replace with actual tool calls)
        tool_result = self._execute_tool(tool_name, parameters, signature)
        result["executed"] = True
        result["result"] = tool_result
        
        return result
    
    def _execute_tool(self, tool_name: str, parameters: Dict, signature: str) -> Any:
        """Simulate tool execution - replace with actual implementations"""
        logger.info(f"🔧 Executing tool: {tool_name}")
        
        # Verify signature before execution
        try:
            self.verify_action_signature(signature)
        except Exception as e:
            return {"error": str(e)}
        
        # Mock tool implementations
        if tool_name == "file_system_read":
            return {"status": "success", "data": "file contents here"}
        elif tool_name == "database_query":
            return {"status": "success", "rows": 42}
        elif tool_name == "shell_execute":
            return {"status": "success", "output": "command executed"}
        else:
            return {"status": "success", "message": f"{tool_name} executed"}
    
    def add_custom_policy(self, role: str, allowed_tools: List[str]):
        """Add or update role policy"""
        self.policies[role] = {
            "allowed_tools": allowed_tools,
            "default": "deny"
        }
        logger.info(f"📝 Policy updated for role: {role}")
    
    def get_violation_count(self) -> int:
        return self.violation_count


# ==================================================
# EXAMPLE USAGE
# ==================================================

if __name__ == "__main__":
    auth = ToolAuthorization()
    
    # Test 1: Admin authorized action
    print("\n" + "="*50)
    print("TEST 1: Admin - Authorized Tool")
    print("="*50)
    result = auth.execute_tool_with_auth(
        user_id="admin_001",
        role="admin",
        tool_name="database_write",
        parameters={"query": "UPDATE users SET status='active'"}
    )
    print(json.dumps(result, indent=2))
    
    # Test 2: Analyst unauthorized action
    print("\n" + "="*50)
    print("TEST 2: Analyst - Unauthorized Tool")
    print("="*50)
    result = auth.execute_tool_with_auth(
        user_id="analyst_002",
        role="analyst",
        tool_name="shell_execute",
        parameters={"command": "rm -rf /"}
    )
    print(json.dumps(result, indent=2))
    
    # Test 3: Viewer authorized action
    print("\n" + "="*50)
    print("TEST 3: Viewer - Authorized Tool")
    print("="*50)
    result = auth.execute_tool_with_auth(
        user_id="viewer_003",
        role="viewer",
        tool_name="file_system_read",
        parameters={"path": "/reports/summary.pdf"}
    )
    print(json.dumps(result, indent=2))
    
    # Stats
    print("\n" + "="*50)
    print("AUTHORIZATION STATS")
    print("="*50)
    print(f"Policy violations: {auth.get_violation_count()}")


# ============================================================
# Integration wrapper for multi_agent_workflow.py
# ============================================================
# ============================================================
# User -> Role mapping for integration workflows
# ============================================================
USER_ROLE_MAP = {
    "admin_001": "admin",
    "viewer_003": "viewer",
    "analyst_002": "analyst",
}


# ============================================================
# Robust integration wrapper (auto-adapts to method signatures)
# ============================================================
# ============================================================
# FINAL FIXED WRAPPER (correct parameter order)
# ============================================================
# ============================================================
# FINAL FINAL: correct execute signature (4 args after self)
# ============================================================


# ============================================================
# Integration wrapper for multi_agent_workflow.py (CLEAN)
# ============================================================
def authorize_tool_call(user_id: str, tool_name: str, params=None):
    params = params or {}
    ta = ToolAuthorization()

    # user -> role mapping
    role_map = {
        "admin_001": "admin",
        "viewer_003": "viewer",
        "analyst_002": "analyst",
    }
    role = role_map.get(user_id, "viewer")

    try:
        # optional: generate signature (for audit), not required for execution
        _ = ta.generate_action_signature(user_id, role, tool_name, params)

        res = ta.execute_tool_with_auth(user_id, role, tool_name, params)

        if res is None:
            return {"authorized": True, "executed": True, "result": {"status": "success"}, "error": None}

        # normalize into expected schema
        if isinstance(res, dict) and "authorized" in res:
            return res

        return {"authorized": True, "executed": True, "result": res, "error": None}

    except Exception as e:
        return {"authorized": False, "executed": False, "result": None, "error": str(e)}
