from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.core.wrappers import wrap_tool

def build_autogen_functions(vault: PrivateVault, policy: Policy):
    """
    AutoGen registers plain python callables as tools/functions.
    We return wrapped functions that enforce PrivateVault policy + logging.
    """
    from privatevault.tools.demo_tools import add, echo, risky_shell

    return {
        "add": wrap_tool(vault, policy, "autogen", "add", add),
        "echo": wrap_tool(vault, policy, "autogen", "echo", echo),
        "shell": wrap_tool(vault, policy, "autogen", "shell", risky_shell),
    }
