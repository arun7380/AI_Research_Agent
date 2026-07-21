import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

from config.settings import settings
from rag.embedding import EmbeddingService

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-backed vector database manager with JSON metadata persistence.
    """

    def __init__(self, index_path: str = None):
        self.index_path = Path(index_path or settings.FAISS_INDEX_PATH)
        self.metadata_path = self.index_path.with_suffix(".json")
        self.embedding_service = EmbeddingService()
        self.index = None
        self.chunks_metadata: List[Dict[str, Any]] = []

        self._ensure_storage_dir()
        self._load_or_create_index()

    def _ensure_storage_dir(self):
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_or_create_index(self):
        dim = self.embedding_service.dimension

        try:
            import faiss
            if self.index_path.exists() and self.metadata_path.exists():
                logger.info(f"Loading FAISS index from {self.index_path}")
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.chunks_metadata = json.load(f)
            else:
                logger.info("Creating new FAISS IndexFlatIP index")
                self.index = faiss.IndexFlatIP(dim)
                self.chunks_metadata = []
        except Exception as e:
            logger.warning(f"FAISS init warning: {e}. Operating in memory mode.")
            self.index = None
            self.chunks_metadata = []

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Embed and add document chunks to the vector store.
        """
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.embed_texts(texts)

        # Normalize vectors for cosine similarity via IndexFlatIP
        faiss_vectors = embeddings.copy()
        norms = np.linalg.norm(faiss_vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        faiss_vectors /= norms

        if self.index is not None:
            self.index.add(faiss_vectors)

        self.chunks_metadata.extend(chunks)
        self.save()

    def search(self, query: str, top_k: int = 5, document_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for top_k most relevant chunks for a given query string.
        Optionally filter by document_id.
        """
        if not self.chunks_metadata:
            return []

        query_vec = self.embedding_service.embed_query(query)
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec /= norm

        query_vec = np.expand_dims(query_vec, axis=0)

        results = []

        if self.index is not None and self.index.ntotal > 0:
            distances, indices = self.index.search(query_vec, min(top_k * 3, len(self.chunks_metadata)))

            for score, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.chunks_metadata):
                    continue

                chunk = self.chunks_metadata[idx].copy()
                chunk["score"] = float(score)

                if document_id and str(chunk.get("document_id")) != str(document_id):
                    continue

                results.append(chunk)
                if len(results) >= top_k:
                    break
        else:
            # InMemory fallback search
            for chunk in self.chunks_metadata:
                if document_id and str(chunk.get("document_id")) != str(document_id):
                    continue

                c_vec = self.embedding_service.embed_query(chunk["text"])
                c_norm = np.linalg.norm(c_vec)
                score = float(np.dot(query_vec[0], c_vec / (c_norm if c_norm > 0 else 1.0)))

                res = chunk.copy()
                res["score"] = score
                results.append(res)

            results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

        return results

    def save(self):
        """
        Persist FAISS index and metadata JSON to disk.
        """
        try:
            import faiss
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.chunks_metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist vector store: {e}")
