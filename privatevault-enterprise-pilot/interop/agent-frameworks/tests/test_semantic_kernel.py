import pytest
from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.adapters.semantickernel_adapter import build_semantic_kernel_functions

def test_semantic_kernel_privatevault_blocks_shell():
    vault = PrivateVault()
    policy = Policy()
    fns = build_semantic_kernel_functions(vault, policy)
    with pytest.raises(RuntimeError):
        fns["shell"](cmd="rm -rf /")

def test_semantic_kernel_privatevault_allows_add():
    vault = PrivateVault()
    policy = Policy()
    fns = build_semantic_kernel_functions(vault, policy)
    assert fns["add"](a=4, b=6) == 10
