from typing import List, Dict, Any


class CitationAgent:
    """
    Extracts, validates, and tags source citations from document chunks and web results.
    Enforces citation limits (< 10 for research/reports, < 5 for slides).
    """

    def process(
        self,
        doc_chunks: List[Dict[str, Any]],
        web_results: List[Dict[str, Any]],
        max_citations: int = 9
    ) -> Dict[str, Any]:
        citations = []
        sources = []

        # Process document citations
        for idx, chunk in enumerate(doc_chunks, start=1):
            if len(citations) >= max_citations:
                break
            fname = chunk.get("filename", "Uploaded Document")
            page = chunk.get("page", 1)
            citation_str = f"[{len(citations) + 1}] Document: {fname} (Page {page})"
            citations.append(citation_str)
            sources.append({
                "type": "document",
                "filename": fname,
                "page": page,
                "snippet": chunk.get("text", "")[:150]
            })

        # Process web citations
        for item in web_results:
            if len(citations) >= max_citations:
                break
            title = item.get("title", "Web Source")
            url = item.get("url", "#")
            idx = len(citations) + 1
            citation_str = f"[{idx}] Web: [{title}]({url})"
            citations.append(citation_str)
            sources.append({
                "type": "web",
                "title": title,
                "url": url,
                "snippet": item.get("snippet", "")[:150]
            })

        return {
            "citations": citations[:max_citations],
            "sources": sources[:max_citations]
        }

