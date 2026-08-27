import uuid
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.database import AsyncSessionLocal
from src.core.security import decode_access_token
from src.models.user import User
from src.models.chat import ChatSession, Message
from src.services.rag_service import RAGService
from src.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: uuid.UUID,
    token: Optional[str] = Query(None)
):
    # 1. Handshake & Token Validation
    if not token:
        await websocket.close(code=4401, reason="Missing authentication token")
        return

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        await websocket.close(code=4401, reason="Invalid authentication token")
        return

    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError:
        await websocket.close(code=4401, reason="Invalid user ID in token")
        return

    # 2. Verify Session Ownership
    async with AsyncSessionLocal() as session:
        stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        res = await session.execute(stmt)
        chat_session = res.scalars().first()
        if not chat_session:
            await websocket.close(code=4403, reason="Chat session not found or unauthorized")
            return

    await websocket.accept()
    await websocket.send_json({
        "type": "connected",
        "session_id": str(session_id),
        "user_id": str(user_id)
    })

    gemini_service = GeminiService()
    context_cleared = False

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                message_data = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})
                continue

            frame_type = message_data.get("type")

            # A. Heartbeat ping
            if frame_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            # B. Clear context
            if frame_type == "clear_context":
                context_cleared = True
                await websocket.send_json({
                    "type": "context_cleared",
                    "session_id": str(session_id),
                    "message": "Session context reset successfully."
                })
                continue

            # C. Cancel stream
            if frame_type == "cancel":
                await websocket.send_json({"type": "status", "step": "cancelled", "message": "Stream cancelled."})
                continue

            # D. Query processing
            if frame_type == "query":
                query_text = (message_data.get("text") or "").strip()
                client_msg_id = message_data.get("client_msg_id")

                if not query_text:
                    await websocket.send_json({"type": "error", "message": "Query cannot be empty"})
                    continue

                async with AsyncSessionLocal() as db:
                    rag_service = RAGService(db)

                    # Persist user message
                    user_msg = Message(
                        user_id=user_id,
                        session_id=session_id,
                        role="user",
                        content=query_text
                    )
                    db.add(user_msg)
                    await db.commit()

                    # Notify status
                    await websocket.send_json({
                        "type": "status",
                        "step": "searching_documents",
                        "message": "Searching your uploaded documents..."
                    })

                    # Load conversation history for context if not cleared
                    history: List[Dict[str, str]] = []
                    if not context_cleared:
                        hist_stmt = (
                            select(Message)
                            .where(Message.session_id == session_id, Message.user_id == user_id)
                            .order_by(Message.created_at.desc())
                            .limit(6)
                        )
                        hist_res = await db.execute(hist_stmt)
                        hist_msgs = list(reversed(hist_res.scalars().all()))
                        history = [{"role": m.role, "content": m.content} for m in hist_msgs[:-1]] # exclude the newly added msg

                    # Execute tenant-scoped vector search
                    chunks = await rag_service.search_similar_chunks(user_id=user_id, query=query_text, top_k=5)

                    # Build prompt and citations
                    prompt, citations = rag_service.build_prompt_with_context(
                        query=query_text,
                        chunks=chunks,
                        conversation_history=history
                    )

                    await websocket.send_json({
                        "type": "status",
                        "step": "generating",
                        "message": "Streaming answer from documents..."
                    })

                    # Stream LLM tokens asynchronously
                    accumulated_response = []
                    async for token_chunk in gemini_service.stream_response(prompt=prompt):
                        accumulated_response.append(token_chunk)
                        await websocket.send_json({
                            "type": "token",
                            "content": token_chunk
                        })

                    full_content = "".join(accumulated_response)

                    # Persist assistant message
                    asst_msg = Message(
                        user_id=user_id,
                        session_id=session_id,
                        role="assistant",
                        content=full_content,
                        citations=citations
                    )
                    db.add(asst_msg)
                    
                    # Update session timestamp & auto-title if first message
                    session_stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
                    s_res = await db.execute(session_stmt)
                    s_obj = s_res.scalars().first()
                    if s_obj and s_obj.title == "New Conversation":
                        # Auto-title based on first query
                        s_obj.title = query_text[:40] + ("..." if len(query_text) > 40 else "")

                    await db.commit()
                    await db.refresh(asst_msg)

                    # Emit done frame
                    await websocket.send_json({
                        "type": "done",
                        "client_msg_id": client_msg_id,
                        "message_id": str(asst_msg.id),
                        "role": "assistant",
                        "content": full_content,
                        "citations": citations
                    })

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for session {session_id}")
    except Exception as e:
        logger.exception(f"WebSocket error in session {session_id}: {e}")
        try:
            await websocket.send_json({"type": "error", "message": f"Server error: {str(e)}"})
        except Exception:
            pass
