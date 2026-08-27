# Implementation Plan: Multi-Tenant Document Q&A Platform

**Branch**: `001-document-qa-platform` | **Date**: 2026-08-27 | **Spec**: [spec.md](./spec.md)

---

## Summary

Build a secure, multi-tenant Document Q&A web application where users can register, upload text-heavy files (PDFs and plain text), and query their documents via an AI assistant that provides strictly grounded, real-time streamed responses with citations. 

The architecture pairs an asynchronous FastAPI backend (with PostgreSQL + `pgvector` for unified relational and vector storage, local `all-MiniLM-L6-v2` 384-d embeddings, and `google-genai` modern async LLM streaming) with a Vue 3 SPA frontend (featuring Vue Router navigation guards, drag-and-drop file ingestion, a document grid with UUID/date/status/actions, a chat sidebar with thread switching & context clearing, smooth auto-scrolling without layout shifts, optimistic UI updates, persistent dark/light theme, and an auto-reconnecting WebSocket client). Absolute tenant data isolation is enforced at the database query layer.

---

## Technical Context

**Language/Version**:
- Backend: Python 3.11+ (fully asynchronous `async`/`await`)
- Frontend: TypeScript / JavaScript (Node.js 20+, Vue.js 3 Composition API with `<script setup>`)

**Primary Dependencies**:
- Backend: `FastAPI`, `uvicorn`, `SQLAlchemy` (2.0 async), `asyncpg`, `alembic`, `pgvector`, `pydantic-settings`, `pypdf`, `langchain-text-splitters`, `sentence-transformers` (`all-MiniLM-L6-v2`), `google-genai`, `python-jose` / `passlib` (Argon2id/bcrypt)
- Frontend: `Vue 3`, `Vite`, `Vue Router 4`, `Pinia`, `Axios`, `Tailwind CSS`, `Lucide Vue Next` (icons)

**Storage**:
- PostgreSQL 16+ with `pgvector` extension for unified relational data and 384-dimensional dense vector embeddings.

**Testing**:
- Backend: `pytest`, `pytest-asyncio`, `httpx` (AsyncClient for REST & WebSocket testing)
- Frontend: `vitest`, `@vue/test-utils`

**Target Platform**:
- Web application (modern desktop and mobile responsive browsers), containerized backend & frontend.

**Project Type**:
- Full-Stack Web Application (Decoupled Async Backend + Vue 3 SPA Frontend).

**Performance Goals**:
- Time-to-First-Token (TTFT) < 2 seconds over WebSocket.
- Document ingestion & indexing < 30 seconds for standard PDFs under 10 MB.
- Sub-10ms vector cosine similarity retrieval per user query.

**Constraints & UI Requirements**:
- Strict multi-tenant data isolation: Every single database query must enforce `user_id == authenticated_jwt_user_id`.
- Protected frontend routes: Vue Router navigation guards redirect unauthenticated users to `/login`.
- Document Management UI: Drag-and-drop dropzone, list/grid displaying document name, upload date, document UUID, status, and view/delete actions.
- Chat UI & Streaming: Sidebar with historical sessions, thread switcher, "Clear Context" button, smooth auto-scroll with layout shift prevention, and optimistic user message rendering.
- Robust UX: Persistent Dark/Light theme toggle, auto-reconnecting WebSocket client with backoff and session re-subscription.

**Scale/Scope**:
- File size limit: 25 MB per document.
- Vector dimension: 384 (`all-MiniLM-L6-v2`).
- Chunk size: ~800 tokens with 15% overlap.

---

## Constitution Check

*GATE: All core architectural and governance principles verified.*

| Principle / Gate | Status | Evaluation |
| :--- | :--- | :--- |
| **Strict Data Isolation** | ✅ PASS | Every table (`users`, `documents`, `chunks`, `chat_sessions`, `messages`) contains `user_id` FK with cascading deletes. All SQL & vector queries require `user_id` parameter. |
| **Non-Blocking Architecture** | ✅ PASS | FastAPI async route handlers, `asyncpg` connection pool, and `google-genai` async generator (`aio.models.generate_content_stream`) prevent event-loop stalls. |
| **No Dual-Store Split Brain** | ✅ PASS | Relational data and vector embeddings reside in the single PostgreSQL + `pgvector` instance. |
| **Verifiable Attribution** | ✅ PASS | Every extracted chunk tracks source document metadata and page numbers, embedded in WebSocket response frames. |
| **Testability & Security Gates** | ✅ PASS | Automated integration tests verify that cross-tenant access attempts return 404/403 with zero metadata leakage. |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-document-qa-platform/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & architectural decisions
├── data-model.md        # Database schema, entities & pgvector indexing
├── quickstart.md        # Verification and quickstart guide
├── checklists/
│   └── requirements.md  # Spec quality checklist
├── contracts/
│   ├── openapi.yaml     # REST API specification
│   └── websocket-protocol.md # Real-time chat & token streaming protocol
└── tasks.md             # Implementation tasks (/speckit-tasks output)
```

### Source Code Structure (Repository Layout)

```text
backend/
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
├── alembic.ini
├── pyproject.toml
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI entry point & lifespan
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Pydantic Settings & env loading
│   │   ├── database.py             # Async SQLAlchemy engine & sessionmaker
│   │   └── security.py             # Password hashing & JWT generation/verification
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                 # User model
│   │   ├── document.py             # Document & Chunk models (with Vector column)
│   │   └── chat.py                 # ChatSession & Message models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Auth request/response schemas
│   │   ├── document.py             # Document & Chunk schemas
│   │   └── chat.py                 # Chat session & message schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Registration & login logic
│   │   ├── document_service.py     # File storage & extraction
│   │   ├── embedding_service.py    # Local sentence-transformers wrapper
│   │   ├── chunking_service.py     # RecursiveCharacterTextSplitter wrapper
│   │   ├── rag_service.py          # Tenant-scoped vector search & prompt assembly
│   │   └── gemini_service.py       # Google GenAI modern async client wrapper
│   └── api/
│       ├── __init__.py
│       ├── deps.py                 # JWT auth dependency (get_current_user)
│       └── v1/
│           ├── __init__.py
│           ├── auth.py             # /auth routes
│           ├── documents.py        # /documents routes
│           ├── chat.py             # /chat/sessions REST routes
│           └── websocket.py        # /ws/chat/{session_id} WebSocket route
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_chunking.py
    │   └── test_security.py
    └── integration/
        ├── test_auth_api.py
        ├── test_document_isolation.py
        └── test_chat_websocket.py

frontend/
├── package.json
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   │   └── index.ts                # Vue router with strict Navigation Guards
│   ├── stores/
│   │   ├── auth.ts                 # Auth state, login/logout, JWT storage
│   │   ├── document.ts             # Uploads, processing states, file list/grid
│   │   └── chat.ts                 # Chat threads, messages, optimistic updates
│   ├── composables/
│   │   ├── useTheme.ts             # Persistent Dark/Light theme state
│   │   ├── useChatWebSocket.ts     # Auto-reconnecting WebSocket client with backoff
│   │   └── useAutoScroll.ts        # Smooth scroll anchor & layout shift prevention
│   ├── services/
│   │   ├── api.ts                  # Axios client with JWT interceptors
│   │   ├── authService.ts
│   │   ├── documentService.ts
│   │   └── chatService.ts
│   ├── components/
│   │   ├── common/
│   │   │   ├── ThemeToggle.vue
│   │   │   ├── Modal.vue
│   │   │   └── StatusBadge.vue
│   │   ├── layout/
│   │   │   ├── AppNavbar.vue
│   │   │   └── AppSidebar.vue
│   │   ├── documents/
│   │   │   ├── DragDropZone.vue    # Drag-and-drop file ingestion zone
│   │   │   ├── DocumentGrid.vue    # List/grid showing ID, date, status, actions
│   │   │   └── DeleteDocModal.vue
│   │   └── chat/
│   │       ├── ChatSidebar.vue     # Historical sessions, switcher, Clear Context
│   │       ├── ChatWindow.vue      # Message stream container with smooth autoscroll
│   │       ├── MessageBubble.vue   # Optimistic rendering, Markdown, status pills
│   │       ├── CitationPill.vue    # Source attribution pills & snippet drawer
│   │       └── ClearContextModal.vue
│   └── views/
│       ├── LoginView.vue
│       ├── RegisterView.vue
│       ├── DocumentsView.vue       # /documents view with drag-drop & grid
│       └── ChatView.vue            # /chat view with sidebar & streaming window
└── tests/
    └── unit/
        ├── useAuthStore.spec.ts
        ├── useTheme.spec.ts
        └── useChatWebSocket.spec.ts
```

**Structure Decision**: Clean decoupled client-server architecture. Backend encapsulates domain logic in dedicated async services with strict tenant scoping in repositories. Frontend organizes UI flows with Vue 3 Composition API, centralized Pinia stores, specialized UI composables (`useTheme`, `useAutoScroll`, `useChatWebSocket`), and modular components for documents and chat streaming.

---

## Complexity Tracking

| Complexity / Feature | Why Needed | Simpler Alternative Rejected Because |
| :--- | :--- | :--- |
| **Local Sentence Transformers Embedding Model** | In-process embedding generation avoids external API network latency and eliminates cloud per-query embedding costs. | Cloud embedding APIs introduce ~100-300ms latency overhead per query and per chunk during ingestion. |
| **Native WebSocket with Auto-Reconnect & Re-subscription** | Guarantees resilient real-time token streaming with automatic connection recovery and session state restoration during network fluctuations. | Basic polling or non-resilient WebSockets cause message dropouts and degraded user experience on brief connection drops. |
| **Smart Scroll Anchor Detection (`useAutoScroll`)** | Prevents disruptive UI layout shifts when users scroll up to read previous messages or inspect citations while new tokens stream in. | Simple `scrollTop = scrollHeight` on every token violently jumps the view and interrupts reading. |
