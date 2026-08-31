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
        try:
            reader = PdfReader(BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Corrupted or invalid PDF file: {str(e)}") from e

        if reader.is_encrypted:
            try:
                decrypted = reader.decrypt("")
                if decrypted == 0:
                    raise ValueError("PDF is password-protected. Please remove password encryption and re-upload.")
            except Exception:
                raise ValueError("PDF is password-protected. Please remove password encryption and re-upload.")

        total_pages = len(reader.pages)
        if total_pages == 0:
            raise ValueError("PDF document contains no pages.")

        chunks: List[Dict[str, Any]] = []
        chunk_idx = 0

        for page_num, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception as e:
                page_text = ""

            page_text = page_text.strip()
            if not page_text:
                continue

            page_chunks = self.splitter.split_text(page_text)
            for text in page_chunks:
                text_clean = text.strip()
                if len(text_clean) > 10:  # filter out empty/trivial fragments
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": text_clean,
                        "page_number": page_num,
                        "token_count": len(text_clean.split())
                    })
                    chunk_idx += 1

        if not chunks:
            raise ValueError(
                "No readable text found in PDF. Scanned image-only PDFs require OCR or selectable text."
            )

        return chunks, total_pages

    def extract_and_chunk_text(self, file_bytes: bytes) -> tuple[List[Dict[str, Any]], int]:
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content = file_bytes.decode("latin-1")
            except Exception as e:
                raise ValueError(f"Unable to decode text file: {str(e)}") from e

        content = content.strip()
        if not content:
            raise ValueError("File is empty or contains only whitespace.")

        chunks: List[Dict[str, Any]] = []
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

        if not chunks:
            raise ValueError("Document contains insufficient text content (minimum 10 characters required).")

        return chunks, 1
