import asyncio
import logging
from typing import List, Any
from src.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _model: Any = None

    @classmethod
    def get_model(cls) -> Any:
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception as e:
                logger.warning(f"SentenceTransformer not loaded directly: {e}. Fallback to deterministic encoder.")
        return cls._model

    async def embed_query(self, text: str) -> List[float]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_embed_query, text)

    def _sync_embed_query(self, text: str) -> List[float]:
        model = self.get_model()
        if model is not None:
            embedding = model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        # Deterministic lightweight hash embedding (384-dim) fallback
        import hashlib
        import math
        h = hashlib.sha256(text.encode()).digest()
        vec = [(float(b) / 255.0) - 0.5 for b in (h * 12)[:384]]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_embed_documents, texts)

    def _sync_embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        model = self.get_model()
        if model is not None:
            embeddings = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
            return embeddings.tolist()
        return [self._sync_embed_query(t) for t in texts]

