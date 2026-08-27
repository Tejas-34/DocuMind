from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class Citation(BaseModel):
    document_id: uuid.UUID
    document_name: str
    page_number: Optional[int] = None
    snippet: Optional[str] = None

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: uuid.UUID
    user_id: uuid.UUID
    session_id: uuid.UUID
    citations: Optional[List[Citation]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatSessionBase(BaseModel):
    title: str = "New Conversation"

class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ChatSessionUpdate(BaseModel):
    title: str

class ChatSessionResponse(ChatSessionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatSessionDetailResponse(ChatSessionResponse):
    messages: List[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)
