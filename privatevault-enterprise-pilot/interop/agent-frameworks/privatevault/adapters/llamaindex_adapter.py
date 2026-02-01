from typing import List
from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy

def build_llamaindex_query_engine(vault: PrivateVault, policy: Policy):
    """
    Build a minimal LlamaIndex query engine with PrivateVault logging on retrieval.
    We don't use policy gating here yet (policy can be used to block certain queries later).
    """
    from llama_index.core import VectorStoreIndex, Document
    from llama_index.core.settings import Settings
    from llama_index.core.embeddings import MockEmbedding
    from llama_index.core.llms import MockLLM

    # fully offline deterministic
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding(embed_dim=16)

    docs: List[Document] = [
        Document(text="KoshaTrack is an orbital propagator system with VV evidence packs."),
        Document(text="PrivateVault is an agent control plane for intent verification and audit."),
    ]

    index = VectorStoreIndex.from_documents(docs)
    qe = index.as_query_engine(similarity_top_k=2)

    # Wrap qe.query
    original_query = qe.query

    def pv_query(q: str):
        vault.record("llamaindex", "retrieval_query", {"query": q})
        resp = original_query(q)

        # response metadata logging (safe + concise)
        vault.record("llamaindex", "retrieval_result", {
            "query": q,
            "response_preview": str(resp)[:300],
        })
        return resp

    qe.query = pv_query
    return qe
