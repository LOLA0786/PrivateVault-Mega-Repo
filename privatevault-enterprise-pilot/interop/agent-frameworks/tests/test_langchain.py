import pytest
from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.adapters.langchain_adapter import build_langchain_tools

def test_langchain_privatevault_blocks_shell():
    vault = PrivateVault()
    policy = Policy()
    tools = build_langchain_tools(vault, policy)
    with pytest.raises(RuntimeError):
        tools[2].invoke({"cmd":"rm -rf /"})

def test_langchain_privatevault_allows_add():
    vault = PrivateVault()
    policy = Policy()
    tools = build_langchain_tools(vault, policy)
    out = tools[0].invoke({"a": 2, "b": 3})
    assert out == 5
