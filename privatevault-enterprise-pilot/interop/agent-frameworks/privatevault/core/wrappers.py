from typing import Any, Callable, Dict
from .vault import PrivateVault
from .policy import Policy

def wrap_tool(vault: PrivateVault, policy: Policy, framework: str, tool_name: str, fn: Callable[..., Any]) -> Callable[..., Any]:
    def wrapped(**kwargs):
        vault.record(framework, "tool_call_attempt", {"tool": tool_name, "args": kwargs})
        ok, reason = policy.allow_tool(tool_name, kwargs)
        vault.record(framework, "tool_policy", {"tool": tool_name, "allowed": ok, "reason": reason})
        if not ok:
            raise RuntimeError(f"PrivateVault blocked tool '{tool_name}': {reason}")

        out = fn(**kwargs)
        vault.record(framework, "tool_result", {"tool": tool_name, "result": str(out)[:500]})
        return out
    return wrapped
