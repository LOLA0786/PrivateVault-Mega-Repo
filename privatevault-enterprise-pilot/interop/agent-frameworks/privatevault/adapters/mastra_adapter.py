from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.core.wrappers import wrap_tool

def build_mastra_tools(vault: PrivateVault, policy: Policy):
    """
    Mastra integration stub.

    Mastra appears to be Node/TS-first (no PyPI package named 'mastra').
    PrivateVault integration pattern remains identical:
      - wrap tool execution
      - enforce policy
      - log + hash chain
    """
    from privatevault.tools.demo_tools import add, echo, risky_shell

    return {
        "add": wrap_tool(vault, policy, "mastra", "add", add),
        "echo": wrap_tool(vault, policy, "mastra", "echo", echo),
        "shell": wrap_tool(vault, policy, "mastra", "shell", risky_shell),
    }
