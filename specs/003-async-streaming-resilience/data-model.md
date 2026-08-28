# Phase 1: Data Model & Pub/Sub Architecture

**Feature**: Asynchronous Background Streaming & Resilient Reconnection (`003-async-streaming-resilience`)
**Date**: 2026-08-28

---

## 1. Backend In-Memory Pub/Sub State Model

```mermaid
classDiagram
    class SessionBroadcastManager {
        -Dict[UUID, ActiveGenerationState] active_generations
        +start_generation(session_id, user_id, query_text, client_msg_id)
        +subscribe(session_id) AsyncQueue
        +unsubscribe(session_id, queue)
        +broadcast(session_id, frame_data)
        +get_state(session_id) ActiveGenerationState
        +cancel_generation(session_id)
    }

    class ActiveGenerationState {
        +UUID session_id
        +UUID user_id
        +str query_text
        +str client_msg_id
        +str status
        +List[str] token_chunks
        +List[Dict] citations
        +Set[AsyncQueue] subscribers
        +Task background_task
        +datetime started_at
        +get_accumulated_text() str
    }

    SessionBroadcastManager "1" *-- "*" ActiveGenerationState : tracks
```

---

## 2. Session Sync REST Schema

```python
class SessionSyncResponse(BaseModel):
    session_id: uuid.UUID
    is_generating: bool
    status_step: Optional[str] = None # 'searching_documents', 'generating', 'idle'
    status_message: Optional[str] = None
    accumulated_content: Optional[str] = None
    latest_message_id: Optional[uuid.UUID] = None
    last_updated: datetime
```

---

## 3. Frontend Reactive Network State

```typescript
interface NetworkStatusState {
  isOnline: boolean
  isReconnecting: boolean
  offlineSince: Date | null
  reconnectAttempts: number
}
```
