from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.core.wrappers import wrap_tool

def build_langgraph_tools(vault: PrivateVault, policy: Policy):
    from privatevault.tools.demo_tools import add, echo, risky_shell

    return {
        "add": wrap_tool(vault, policy, "langgraph", "add", add),
        "echo": wrap_tool(vault, policy, "langgraph", "echo", echo),
        "shell": wrap_tool(vault, policy, "langgraph", "shell", risky_shell),
    }
