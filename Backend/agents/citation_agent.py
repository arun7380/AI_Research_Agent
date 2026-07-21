from typing import List, Dict, Any


class CitationAgent:
    """
    Extracts, validates, and tags source citations from document chunks and web results.
    """

    def process(self, doc_chunks: List[Dict[str, Any]], web_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        citations = []
        sources = []

        # Process document citations
        for idx, chunk in enumerate(doc_chunks, start=1):
            fname = chunk.get("filename", "Uploaded Document")
            page = chunk.get("page", 1)
            citation_str = f"[{idx}] Document: {fname} (Page {page})"
            citations.append(citation_str)
            sources.append({
                "type": "document",
                "filename": fname,
                "page": page,
                "snippet": chunk.get("text", "")[:150]
            })

        # Process web citations
        start_idx = len(citations) + 1
        for idx, item in enumerate(web_results, start=start_idx):
            title = item.get("title", "Web Source")
            url = item.get("url", "#")
            citation_str = f"[{idx}] Web: {title} - {url}"
            citations.append(citation_str)
            sources.append({
                "type": "web",
                "title": title,
                "url": url,
                "snippet": item.get("snippet", "")[:150]
            })

        return {
            "citations": citations,
            "sources": sources
        }
