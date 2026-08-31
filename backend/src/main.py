import sys
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure backend directory is in sys.path
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.core.config import settings
from src.core.database import engine, Base
from src.core.exceptions import DocuMindException, documind_exception_handler, global_exception_handler
from src.api.v1 import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("documind")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DocuMind backend...")
    # Verify DB connectivity & extension
    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schema initialized and vector extension verified.")
        except Exception as e:
            logger.warning(f"Database auto-init note (run migrations if db is not ready): {e}")

    # Pre-warm Embedding Model in background executor so the first user query has zero cold-start delay
    try:
        import asyncio
        from src.services.embedding_service import EmbeddingService
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, EmbeddingService.get_model)
        logger.info("Semantic embedding model pre-warmed successfully.")
    except Exception as e:
        logger.warning(f"Embedding model pre-warm note: {e}")

    yield
    logger.info("Shutting down DocuMind backend...")
    await engine.dispose()

app = FastAPI(
    title="DocuMind API",
    description="Secure, Multi-Tenant Document Q&A Web Application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(DocuMindException, documind_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
