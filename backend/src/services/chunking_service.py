from typing import List, Dict, Any
from io import BytesIO
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.core.config import settings

class ChunkingService:
    def __init__(self):
        # 800 tokens ~ 3200 chars, 15% overlap ~ 480 chars
        self.chunk_size = settings.CHUNK_SIZE * 4
        self.chunk_overlap = int(self.chunk_size * 0.15)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def extract_and_chunk_pdf(self, file_bytes: bytes) -> tuple[List[Dict[str, Any]], int]:
        reader = PdfReader(BytesIO(file_bytes))
        total_pages = len(reader.pages)
        chunks: List[Dict[str, Any]] = []
        chunk_idx = 0

        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            page_text = page_text.strip()
            if not page_text:
                continue

            page_chunks = self.splitter.split_text(page_text)
            for text in page_chunks:
                text_clean = text.strip()
                if len(text_clean) > 10: # filter out empty/trivial fragments
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": text_clean,
                        "page_number": page_num,
                        "token_count": len(text_clean.split())
                    })
                    chunk_idx += 1

        return chunks, total_pages

    def extract_and_chunk_text(self, file_bytes: bytes) -> tuple[List[Dict[str, Any]], int]:
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = file_bytes.decode("latin-1", errors="ignore")

        content = content.strip()
        chunks: List[Dict[str, Any]] = []
        if not content:
            return chunks, 1

        text_chunks = self.splitter.split_text(content)
        for idx, text in enumerate(text_chunks):
            text_clean = text.strip()
            if len(text_clean) > 10:
                chunks.append({
                    "chunk_index": idx,
                    "content": text_clean,
                    "page_number": 1,
                    "token_count": len(text_clean.split())
                })

        return chunks, 1
