# Implementation Plan: Asynchronous Background Streaming & Resilient Reconnection

**Branch**: `003-async-streaming-resilience` | **Date**: 2026-08-28 | **Spec**: [specs/003-async-streaming-resilience/spec.md](spec.md)

**Input**: Feature specification from `specs/003-async-streaming-resilience/spec.md` (Asynchronous Decoupling, Pub/Sub WebSocket Connection Manager, Offline State Detection, Optimistic UI & Reconnection, Performant Token Rendering).

---

## Summary

Decouple message ingestion from the LLM generation task in FastAPI by creating an in-memory `SessionBroadcastManager` powered by `asyncio.create_task` and PostgreSQL persistence. Convert the WebSocket handler into a pure pub/sub consumer that delivers live tokens, supports mid-stream reconnection with catch-up buffering, tracks browser offline state with `navigator.onLine`, and batches rapid UI token frames using `requestAnimationFrame`.

---

## Technical Context

**Language/Version**: Python 3.11+, TypeScript 5.x, Vue 3.5  
**Primary Dependencies**: FastAPI, SQLAlchemy Async, asyncpg, google-genai, Pinia 2.2, Lucide Vue Next  
**Storage**: PostgreSQL (pgvector + messages table) + In-Memory `asyncio.Queue` Session Pub/Sub  
**Testing**: Pytest (backend asynchronous execution tests), Vite / Vue-TSC (frontend build check)  
**Target Platform**: Modern Web Browsers (WebSocket, `navigator.onLine`, `requestAnimationFrame`)  
**Project Type**: Multi-tenant full-stack RAG Web Application  
**Performance Goals**: <50ms catch-up resumption, 60fps streaming render without layout thrashing  
**Constraints**: Zero data loss when client disconnects; seamless multi-client sync for same session  

---

## Constitution Check

- **Principle I: Modularity & Independence**: PASS. `generation_manager.py` cleanly encapsulates task lifecycle and pub/sub subscription.
- **Principle II: Zero Data Loss / Contract Invariant**: PASS. All messages and citations are durably committed to PostgreSQL.
- **Principle III: Observability & Resilience**: PASS. Clear status transitions and reconnection lifecycle logging.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-async-streaming-resilience/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/
    └── websocket-pubsub-protocol.md
```

### Source Code

```text
backend/
├── src/
│   ├── api/v1/
│   │   ├── chat.py                       # Add /chat/sessions/{id}/sync endpoint
│   │   └── websocket.py                  # Refactor to Pub/Sub consumer
│   └── services/
│       └── generation_manager.py         # NEW: In-memory SessionBroadcastManager & background task worker

frontend/
├── src/
│   ├── composables/
│   │   ├── useAutoScroll.ts              # Refactor with user-scroll detection & rAF
│   │   ├── useChatWebSocket.ts           # Add exponential backoff & catch-up handler
│   │   └── useNetworkStatus.ts           # NEW: navigator.onLine & online/offline events
│   ├── components/chat/
│   │   ├── ChatWindow.vue                # Batch token updates via requestAnimationFrame
│   │   └── MessageBubble.vue             # Display optimistic pending state
│   └── views/
│       └── ChatView.vue                  # Floating offline status banner
```

---

## Complexity Tracking

*No constitution violations or unjustified complexities identified.*
