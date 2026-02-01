from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy

def build_haystack_retriever(vault: PrivateVault, policy: Policy):
    """
    Minimal deterministic Haystack retrieval (offline).
    """
    from haystack import Document
    from haystack.document_stores.in_memory import InMemoryDocumentStore
    from haystack.components.retrievers.in_memory import InMemoryBM25Retriever

    store = InMemoryDocumentStore()
    docs = [
        Document(content="KoshaTrack generates VV evidence packs for orbit prediction."),
        Document(content="PrivateVault provides intent verification, replayability, audit, and tamper-proof logs."),
    ]
    store.write_documents(docs)

    retriever = InMemoryBM25Retriever(document_store=store)

    def pv_retrieve(query: str):
        vault.record("haystack", "retrieval_query", {"query": query})
        out = retriever.run(query=query)
        # log only ids + small preview
        vault.record("haystack", "retrieval_result", {
            "query": query,
            "top_docs_preview": [
                d.content[:80] for d in out.get("documents", [])[:3]
            ]
        })
        return out

    return pv_retrieve
