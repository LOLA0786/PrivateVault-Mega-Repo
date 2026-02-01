from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.core.wrappers import wrap_tool

def build_google_adk_tools(vault: PrivateVault, policy: Policy):
    """
    Google ADK integration:
    - expose tools as callables compatible with ADK tool registration
    - enforce policy + logging via PrivateVault
    """
    from privatevault.tools.demo_tools import add, echo, risky_shell

    return {
        "add": wrap_tool(vault, policy, "google_adk", "add", add),
        "echo": wrap_tool(vault, policy, "google_adk", "echo", echo),
        "shell": wrap_tool(vault, policy, "google_adk", "shell", risky_shell),
    }
