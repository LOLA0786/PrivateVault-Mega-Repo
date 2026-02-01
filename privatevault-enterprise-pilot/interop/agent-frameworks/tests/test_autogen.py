import pytest
from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.adapters.autogen_adapter import build_autogen_functions

def test_autogen_privatevault_blocks_shell():
    vault = PrivateVault()
    policy = Policy()
    tools = build_autogen_functions(vault, policy)
    with pytest.raises(RuntimeError):
        tools["shell"](cmd="rm -rf /")

def test_autogen_privatevault_allows_add():
    vault = PrivateVault()
    policy = Policy()
    tools = build_autogen_functions(vault, policy)
    assert tools["add"](a=7, b=8) == 15
