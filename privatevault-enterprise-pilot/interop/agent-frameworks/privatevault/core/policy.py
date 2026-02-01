from typing import Dict, Any

class Policy:
    BLOCKED_TOOLS = {"shell", "exec", "rm", "delete_all"}

    def allow_tool(self, tool_name: str, args: Dict[str, Any]) -> (bool, str):
        if tool_name in self.BLOCKED_TOOLS:
            return False, f"blocked tool: {tool_name}"
        return True, "allowed"
