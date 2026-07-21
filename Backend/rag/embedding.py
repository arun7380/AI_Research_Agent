import logging
from typing import List
import numpy as np

from config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Embedding service supporting SentenceTransformers and OpenAI models with graceful fallback.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None
        self._dimension = 384  # Default for bge-small-en-v1.5

    def _load_model(self):
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer
            model_inst = SentenceTransformer(self.model_name)
            self._model = model_inst
            if hasattr(model_inst, "get_embedding_dimension"):
                self._dimension = model_inst.get_embedding_dimension()
            else:
                self._dimension = model_inst.get_sentence_embedding_dimension()
        except Exception as e:
            logger.warning(f"Failed to load SentenceTransformer ({e}). Using lightweight fallback encoder.")
            self._model = "fallback"

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of text strings into numpy float32 array matrix.
        """
        self._load_model()

        if not texts:
            return np.empty((0, self._dimension), dtype=np.float32)

        if self._model == "fallback":
            return self._fallback_embed(texts)

        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.error(f"Embedding error: {e}. Falling back to hash embeddings.")
            return self._fallback_embed(texts)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string into 1D numpy float32 vector.
        """
        embeddings = self.embed_texts([query])
        return embeddings[0]

    def _fallback_embed(self, texts: List[str]) -> np.ndarray:
        """
        Deterministic lightweight hash embedding fallback when transformer models are not downloaded yet.
        """
        vectors = []
        for text in texts:
            vec = np.zeros(self._dimension, dtype=np.float32)
            for i, word in enumerate(text.split()):
                h = hash(word)
                idx = abs(h) % self._dimension
                vec[idx] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            vectors.append(vec)
        return np.array(vectors, dtype=np.float32)

    @property
    def dimension(self) -> int:
        return self._dimension
