from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.core.wrappers import wrap_tool

def build_langchain_tools(vault: PrivateVault, policy: Policy):
    from langchain_core.tools import tool
    from privatevault.tools.demo_tools import add, echo, risky_shell

    @tool
    def pv_add(a: int, b: int) -> int:
        """Add two integers (PrivateVault wrapped)."""
        return wrap_tool(vault, policy, "langchain", "add", add)(a=a, b=b)

    @tool
    def pv_echo(x: str) -> str:
        """Echo input string back (PrivateVault wrapped)."""
        return wrap_tool(vault, policy, "langchain", "echo", echo)(x=x)

    @tool
    def pv_shell(cmd: str) -> str:
        """Simulated shell tool (should be blocked by PrivateVault policy)."""
        return wrap_tool(vault, policy, "langchain", "shell", risky_shell)(cmd=cmd)

    return [pv_add, pv_echo, pv_shell]
