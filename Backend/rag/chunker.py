from typing import List, Dict, Any


class TextChunker:
    """
    Splits document text into overlapping chunks with metadata.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        text: str,
        document_id: str,
        filename: str,
        pages: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Splits text into chunks preserving page information and metadata.
        """
        chunks = []

        if pages and len(pages) > 0:
            chunk_idx = 0
            for page_info in pages:
                page_num = page_info.get("page", 1)
                page_text = page_info.get("text", "")
                page_chunks = self._split_text(page_text)

                for p_chunk in page_chunks:
                    chunks.append({
                        "chunk_id": f"{document_id}_{chunk_idx}",
                        "document_id": document_id,
                        "filename": filename,
                        "page": page_num,
                        "chunk_index": chunk_idx,
                        "text": p_chunk,
                    })
                    chunk_idx += 1
        else:
            raw_chunks = self._split_text(text)
            for idx, c_text in enumerate(raw_chunks):
                chunks.append({
                    "chunk_id": f"{document_id}_{idx}",
                    "document_id": document_id,
                    "filename": filename,
                    "page": 1,
                    "chunk_index": idx,
                    "text": c_text,
                })

        return chunks

    def _split_text(self, text: str) -> List[str]:
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size

            if end < text_len:
                # Attempt to break on natural boundaries
                last_space = text.rfind(" ", start, end)
                last_newline = text.rfind("\n", start, end)
                break_point = max(last_space, last_newline)

                if break_point > start + (self.chunk_size // 2):
                    end = break_point

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(chunk_text)

            start = end - self.chunk_overlap
            if start >= text_len or (end == text_len):
                break

        return chunks
