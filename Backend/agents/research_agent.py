from typing import List, Dict, Any
from rag.retriever import DocumentRetriever


class ResearchAgent:
    """
    Searches uploaded document vector store for relevant context chunks.
    """

    def __init__(self, retriever: DocumentRetriever = None):
        self.retriever = retriever or DocumentRetriever()

    def search(self, sub_queries: List[str], document_id: str = None) -> List[Dict[str, Any]]:
        retrieved_chunks = []
        seen_chunk_ids = set()

        for query in sub_queries:
            chunks = self.retriever.retrieve(query=query, top_k=3, document_id=document_id)
            for c in chunks:
                c_id = c.get("chunk_id")
                if c_id not in seen_chunk_ids:
                    seen_chunk_ids.add(c_id)
                    retrieved_chunks.append(c)

        return retrieved_chunks
