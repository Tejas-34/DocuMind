from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

class DocumentBase(BaseModel):
    filename: str
    file_size: int
    mime_type: str

class DocumentResponse(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    error_message: Optional[str] = None
    total_pages: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChunkResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    token_count: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
