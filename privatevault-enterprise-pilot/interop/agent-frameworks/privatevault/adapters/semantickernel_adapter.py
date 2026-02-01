from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.core.wrappers import wrap_tool

def build_semantic_kernel_functions(vault: PrivateVault, policy: Policy):
    """
    Semantic Kernel: register python callables as native functions.
    We'll return wrapped callables; integration into Kernel is optional.
    """
    from privatevault.tools.demo_tools import add, echo, risky_shell

    return {
        "add": wrap_tool(vault, policy, "semantic_kernel", "add", add),
        "echo": wrap_tool(vault, policy, "semantic_kernel", "echo", echo),
        "shell": wrap_tool(vault, policy, "semantic_kernel", "shell", risky_shell),
    }
