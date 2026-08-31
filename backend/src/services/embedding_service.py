import os
import asyncio
import logging
from typing import List, Any, Optional
from src.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _model: Optional[Any] = None

    @classmethod
    def get_model(cls) -> Any:
        if cls._model is None:
            try:
                from fastembed import TextEmbedding

                cache_dir = os.environ.get("FASTEMBED_CACHE_PATH", settings.FASTEMBED_CACHE_PATH)
                kwargs = {"model_name": settings.EMBEDDING_MODEL}
                if cache_dir and os.path.exists(cache_dir):
                    kwargs["cache_dir"] = cache_dir

                cls._model = TextEmbedding(**kwargs)

                logger.info(
                    f"Loaded FastEmbed model: {settings.EMBEDDING_MODEL} (cache: {cache_dir})"
                )

            except Exception as e:
                logger.exception(
                    f"Failed to load embedding model: {e}"
                )
                raise RuntimeError(
                    f"Semantic embedding model '{settings.EMBEDDING_MODEL}' could not be loaded: {e}"
                ) from e

        return cls._model

    async def embed_query(self, text: str) -> List[float]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_embed_query, text)

    def _sync_embed_query(self, text: str) -> List[float]:
        try:
            model = self.get_model()
            if model is not None:
                embeddings = list(model.embed([text]))
                if embeddings:
                    return embeddings[0].tolist()
        except Exception as e:
            logger.error(f"FastEmbed error encoding query: {e}")

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
        try:
            model = self.get_model()
            if model is not None:
                embeddings = [e.tolist() for e in model.embed(texts, batch_size=32)]
                return embeddings
        except Exception as e:
            logger.error(f"FastEmbed error encoding documents: {e}")
        return [self._sync_embed_query(t) for t in texts]
