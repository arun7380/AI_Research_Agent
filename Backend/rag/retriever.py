from typing import List, Dict, Any

from rag.reranker import Reranker
from rag.vector_store import VectorStore


class DocumentRetriever:
    """
    High-level document retriever using VectorStore and Reranker.
    """

    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store or VectorStore()
        self.reranker = Reranker()

    def retrieve(self, query: str, top_k: int = 5, document_id: str = None) -> List[Dict[str, Any]]:
        raw_results = self.vector_store.search(query=query, top_k=top_k * 2, document_id=document_id)
        reranked = self.reranker.rerank(query=query, results=raw_results, top_k=top_k)
        return reranked
