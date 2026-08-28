import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Any, Tuple
from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.models.chat import ChatSession, Message
from src.services.rag_service import RAGService
from src.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class ActiveGenerationState:
    def __init__(self, session_id: uuid.UUID, user_id: uuid.UUID, query_text: str, client_msg_id: Optional[str]):
        self.session_id = session_id
        self.user_id = user_id
        self.query_text = query_text
        self.client_msg_id = client_msg_id
        self.status_step = "initializing"
        self.status_message = "Starting generation..."
        self.accumulated_tokens: List[str] = []
        self.citations: List[Dict[str, Any]] = []
        self.message_id: Optional[str] = None
        self.subscribers: Set[asyncio.Queue] = set()
        self.background_task: Optional[asyncio.Task] = None
        self.is_done = False
        self.started_at = datetime.now(timezone.utc)

    def get_accumulated_text(self) -> str:
        return "".join(self.accumulated_tokens)


class SessionBroadcastManager:
    def __init__(self):
        self._active_generations: Dict[uuid.UUID, ActiveGenerationState] = {}
        self._session_subscribers: Dict[uuid.UUID, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def get_state(self, session_id: uuid.UUID) -> Optional[ActiveGenerationState]:
        async with self._lock:
            return self._active_generations.get(session_id)

    async def subscribe(self, session_id: uuid.UUID) -> Tuple[asyncio.Queue, Optional[ActiveGenerationState]]:
        queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        async with self._lock:
            if session_id not in self._session_subscribers:
                self._session_subscribers[session_id] = set()
            self._session_subscribers[session_id].add(queue)

            active_gen = self._active_generations.get(session_id)
            if active_gen and not active_gen.is_done:
                active_gen.subscribers.add(queue)

        return queue, active_gen

    async def unsubscribe(self, session_id: uuid.UUID, queue: asyncio.Queue):
        async with self._lock:
            if session_id in self._session_subscribers:
                self._session_subscribers[session_id].discard(queue)
                if not self._session_subscribers[session_id]:
                    del self._session_subscribers[session_id]

            active_gen = self._active_generations.get(session_id)
            if active_gen:
                active_gen.subscribers.discard(queue)

    async def broadcast(self, session_id: uuid.UUID, frame_data: Dict[str, Any]):
        async with self._lock:
            subscribers = list(self._session_subscribers.get(session_id, []))

        for queue in subscribers:
            try:
                queue.put_nowait(frame_data)
            except asyncio.QueueFull:
                logger.warning(f"Subscriber queue full for session {session_id}, dropping frame {frame_data.get('type')}")
            except Exception as e:
                logger.error(f"Error pushing to subscriber queue in session {session_id}: {e}")

    async def start_generation(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        query_text: str,
        client_msg_id: Optional[str] = None,
        context_cleared: bool = False
    ) -> ActiveGenerationState:
        async with self._lock:
            # If an existing generation is running, cancel it first
            existing = self._active_generations.get(session_id)
            if existing and existing.background_task and not existing.is_done:
                existing.background_task.cancel()

            state = ActiveGenerationState(
                session_id=session_id,
                user_id=user_id,
                query_text=query_text,
                client_msg_id=client_msg_id
            )
            # Attach existing session subscribers
            if session_id in self._session_subscribers:
                state.subscribers.update(self._session_subscribers[session_id])

            self._active_generations[session_id] = state

        # Launch decoupled background task
        task = asyncio.create_task(
            self._run_generation_task(state, context_cleared)
        )
        state.background_task = task
        return state

    async def cancel_generation(self, session_id: uuid.UUID):
        async with self._lock:
            state = self._active_generations.get(session_id)
            if state and state.background_task and not state.is_done:
                state.background_task.cancel()
                state.status_step = "cancelled"
                state.status_message = "Stream cancelled."
                state.is_done = True

        await self.broadcast(session_id, {
            "type": "status",
            "step": "cancelled",
            "message": "Stream cancelled."
        })

    async def _run_generation_task(self, state: ActiveGenerationState, context_cleared: bool):
        session_id = state.session_id
        user_id = state.user_id
        query_text = state.query_text
        gemini_service = GeminiService()

        try:
            async with AsyncSessionLocal() as db:
                rag_service = RAGService(db)

                # 1. Persist user message to DB
                user_msg = Message(
                    user_id=user_id,
                    session_id=session_id,
                    role="user",
                    content=query_text
                )
                db.add(user_msg)
                await db.commit()

                # 2. Status: Searching documents
                state.status_step = "searching_documents"
                state.status_message = "Searching your uploaded documents..."
                await self.broadcast(session_id, {
                    "type": "status",
                    "step": "searching_documents",
                    "message": state.status_message
                })

                # 3. Load conversation context
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
                    history = [{"role": m.role, "content": m.content} for m in hist_msgs[:-1]]

                # 4. Tenant vector search
                chunks = await rag_service.search_similar_chunks(user_id=user_id, query=query_text, top_k=5)

                # 5. Build prompt & citations
                prompt, citations = rag_service.build_prompt_with_context(
                    query=query_text,
                    chunks=chunks,
                    conversation_history=history
                )
                state.citations = citations

                # 6. Status: Generating
                state.status_step = "generating"
                state.status_message = "Streaming answer from documents..."
                await self.broadcast(session_id, {
                    "type": "status",
                    "step": "generating",
                    "message": state.status_message
                })

                # 7. Stream LLM tokens
                async for token_chunk in gemini_service.stream_response(prompt=prompt):
                    state.accumulated_tokens.append(token_chunk)
                    await self.broadcast(session_id, {
                        "type": "token",
                        "content": token_chunk
                    })

                full_content = state.get_accumulated_text()

                # 8. Persist assistant message to DB
                asst_msg = Message(
                    user_id=user_id,
                    session_id=session_id,
                    role="assistant",
                    content=full_content,
                    citations=citations
                )
                db.add(asst_msg)

                # 9. Auto-title if new session
                session_stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
                s_res = await db.execute(session_stmt)
                s_obj = s_res.scalars().first()
                if s_obj and s_obj.title == "New Conversation":
                    s_obj.title = query_text[:40] + ("..." if len(query_text) > 40 else "")

                await db.commit()
                await db.refresh(asst_msg)

                state.message_id = str(asst_msg.id)
                state.is_done = True
                state.status_step = "completed"
                state.status_message = ""

                # 10. Emit done frame
                await self.broadcast(session_id, {
                    "type": "done",
                    "client_msg_id": state.client_msg_id,
                    "message_id": str(asst_msg.id),
                    "role": "assistant",
                    "content": full_content,
                    "citations": citations
                })

        except asyncio.CancelledError:
            logger.info(f"Generation task for session {session_id} was cancelled.")
            state.status_step = "cancelled"
            state.is_done = True
        except Exception as e:
            logger.exception(f"Error during background generation for session {session_id}: {e}")
            state.status_step = "error"
            state.status_message = f"Server error: {str(e)}"
            state.is_done = True
            await self.broadcast(session_id, {
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
        finally:
            # Retain in cache briefly for catch-up, then remove after 15 seconds
            await asyncio.sleep(15)
            async with self._lock:
                if self._active_generations.get(session_id) is state:
                    del self._active_generations[session_id]


# Global singleton instance
broadcast_manager = SessionBroadcastManager()
