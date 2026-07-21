from typing import List, Dict, Any

class Reranker:
    """
    Reranks search results based on relevance and token overlap.
    """

    @staticmethod
    def rerank(query: str, results: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        if not results:
            return []

        query_terms = set(query.lower().split())

        for item in results:
            text = item.get("text", "").lower()
            text_terms = set(text.split())
            overlap = len(query_terms.intersection(text_terms)) / max(1, len(query_terms))
            # Combine vector similarity score with keyword overlap score
            item["final_score"] = item.get("score", 0.0) * 0.7 + overlap * 0.3

        reranked = sorted(results, key=lambda x: x["final_score"], reverse=True)
        return reranked[:top_k]
