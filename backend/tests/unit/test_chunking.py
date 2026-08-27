import pytest
from src.services.chunking_service import ChunkingService

def test_text_chunking():
    service = ChunkingService()
    sample_text = ("This is a test paragraph for document chunking. " * 50).encode("utf-8")
    chunks, pages = service.extract_and_chunk_text(sample_text)
    assert len(chunks) >= 1
    assert pages == 1
    assert "content" in chunks[0]
    assert "chunk_index" in chunks[0]
    assert chunks[0]["page_number"] == 1
