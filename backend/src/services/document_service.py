import uuid
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status

from src.models.document import Document, Chunk
from src.schemas.document import DocumentResponse
from src.services.chunking_service import ChunkingService
from src.services.embedding_service import EmbeddingService
from src.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()

    async def create_document(
        self,
        user_id: uuid.UUID,
        filename: str,
        file_size: int,
        mime_type: str
    ) -> Document:
        doc = Document(
            user_id=user_id,
            filename=filename,
            file_size=file_size,
            mime_type=mime_type,
            status="processing"
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def list_documents(self, user_id: uuid.UUID) -> List[Document]:
        stmt = (
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_document(self, user_id: uuid.UUID, document_id: uuid.UUID) -> Optional[Document]:
        stmt = (
            select(Document)
            .where(Document.user_id == user_id, Document.id == document_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def delete_document(self, user_id: uuid.UUID, document_id: uuid.UUID) -> bool:
        doc = await self.get_document(user_id, document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found."
            )
        
        await self.db.delete(doc)
        await self.db.commit()
        return True

    @classmethod
    async def process_document_background(
        cls,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        file_bytes: bytes,
        filename: str,
        mime_type: str
    ):
        async with AsyncSessionLocal() as session:
            try:
                chunking_service = ChunkingService()
                embedding_service = EmbeddingService()

                # 1. Extract and chunk text
                if mime_type == "application/pdf" or filename.lower().endswith(".pdf"):
                    raw_chunks, total_pages = chunking_service.extract_and_chunk_pdf(file_bytes)
                else:
                    raw_chunks, total_pages = chunking_service.extract_and_chunk_text(file_bytes)

                if not raw_chunks:
                    raise ValueError("No readable text content found in document. Scanned image-only PDFs require OCR.")

                # 2. Generate embeddings locally
                texts = [c["content"] for c in raw_chunks]
                embeddings = await embedding_service.embed_documents(texts)

                if not embeddings or len(embeddings) != len(raw_chunks):
                    raise RuntimeError("Embedding generation failed for one or more text chunks.")

                # 3. Persist chunks
                for i, c in enumerate(raw_chunks):
                    chunk = Chunk(
                        user_id=user_id,
                        document_id=document_id,
                        chunk_index=c["chunk_index"],
                        content=c["content"],
                        page_number=c["page_number"],
                        token_count=c["token_count"],
                        embedding=embeddings[i]
                    )
                    session.add(chunk)

                # 4. Update document status to ready
                stmt = select(Document).where(Document.id == document_id, Document.user_id == user_id)
                res = await session.execute(stmt)
                doc = res.scalars().first()
                if doc:
                    doc.status = "ready"
                    doc.total_pages = total_pages
                    doc.error_message = None
                    await session.commit()
                logger.info(f"Successfully processed document '{filename}' ({document_id}) with {len(raw_chunks)} chunks.")

            except Exception as e:
                error_reason = str(e).strip() or "Unknown document processing error"
                logger.exception(f"Failed to process document '{filename}' ({document_id}): {error_reason}")
                try:
                    stmt = select(Document).where(Document.id == document_id, Document.user_id == user_id)
                    res = await session.execute(stmt)
                    doc = res.scalars().first()
                    if doc:
                        doc.status = "failed"
                        doc.error_message = error_reason[:500]
                        await session.commit()
                except Exception as db_err:
                    logger.exception(f"Failed to record failed status for document {document_id}: {db_err}")
