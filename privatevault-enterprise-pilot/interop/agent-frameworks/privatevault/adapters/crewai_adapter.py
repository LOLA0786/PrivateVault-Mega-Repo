from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.core.wrappers import wrap_tool

def build_crewai_tools(vault: PrivateVault, policy: Policy):
    """
    CrewAI tools are usually passed as callables.
    We provide wrapped callables compatible with CrewAI tool usage.
    """
    from privatevault.tools.demo_tools import add, echo, risky_shell

    return {
        "add": wrap_tool(vault, policy, "crewai", "add", add),
        "echo": wrap_tool(vault, policy, "crewai", "echo", echo),
        "shell": wrap_tool(vault, policy, "crewai", "shell", risky_shell),
    }
