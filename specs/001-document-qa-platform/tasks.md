# Implementation Tasks: Multi-Tenant Document Q&A Platform

**Feature**: Multi-Tenant Document Q&A Platform
**Branch**: `001-document-qa-platform`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Environment Setup & Project Scaffolding

**Purpose**: Initialize backend and frontend project foundations, tooling, and environment configuration.

- [X] T001 Initialize backend repository structure, `.env.example`, `pyproject.toml`, and `requirements.txt` targeting Python 3.10+ in `backend/`
- [X] T002 [P] Initialize Vue 3 SPA project using Vite, TypeScript, Pinia, Vue Router 4, Tailwind CSS, and Lucide icons in `frontend/`
- [X] T003 [P] Configure backend linting/formatting (`ruff`/`black`) in `backend/pyproject.toml` and frontend linting (`eslint`/`prettier`) in `frontend/.eslintrc.cjs`

---

## Phase 2: Foundational Infrastructure & Database Schema

**Purpose**: Core data layer, async SQLAlchemy 2.0 setup, Alembic migrations with pgvector, base models, and security infrastructure.

**⚠️ CRITICAL**: Must complete before any user story can be implemented.

- [X] T004 Setup async SQLAlchemy 2.0 database engine, `async_sessionmaker`, and declarative `Base` in `backend/src/core/database.py`
- [X] T005 [P] Implement Pydantic Settings for environment variables (`DATABASE_URL`, `JWT_SECRET`, `GEMINI_API_KEY`, `EMBEDDING_MODEL`) in `backend/src/core/config.py`
- [X] T006 [P] Configure Alembic with asyncpg and pgvector extension registration in `backend/alembic/env.py` and `backend/alembic.ini`
- [X] T007 Create SQLAlchemy models for `User`, `Document`, `Chunk` (with `Vector(384)` column), `ChatSession`, and `Message` with mandatory `user_id` foreign keys in `backend/src/models/`
- [X] T008 Generate and apply initial Alembic migration creating tables and HNSW cosine similarity index on `chunks.embedding` in `backend/alembic/versions/001_initial_schema.py`
- [X] T009 [P] Implement password hashing (Argon2id/bcrypt) and JWT encode/decode utilities in `backend/src/core/security.py`
- [X] T010 [P] Implement FastAPI global exception handlers and standard error response schemas in `backend/src/core/exceptions.py`
- [X] T011 Create main FastAPI application entry point with CORS middleware, lifespan event handlers, and API router mounting in `backend/src/main.py`

**Checkpoint**: Database initialized, pgvector ready, and foundational security/configuration complete.

---

## Phase 3: User Story 1 - User Authentication & Isolated Workspace (Priority: P1) 🎯 MVP

**Goal**: Enable users to securely register, log in, receive JWT tokens, and establish an isolated workspace where all private routes are protected.

**Independent Test**: Register User A and User B, log in, verify JWT authentication, and confirm navigation guards protect private routes.

### Implementation for User Story 1

- [X] T012 [P] [US1] Define Pydantic schemas for user registration, login, token response, and user profile in `backend/src/schemas/auth.py`
- [X] T013 [US1] Implement `AuthService` handling user registration, duplicate email check, and credential validation in `backend/src/services/auth_service.py`
- [X] T014 [US1] Implement FastAPI dependency `get_current_user` enforcing strict JWT token verification and tenant identity extraction in `backend/src/api/deps.py`
- [X] T015 [US1] Implement `/api/v1/auth/register`, `/api/v1/auth/login`, and `/api/v1/auth/me` endpoints in `backend/src/api/v1/auth.py`
- [X] T016 [P] [US1] Setup Axios API client with request interceptors attaching `Bearer` JWT token in `frontend/src/services/api.ts`
- [X] T017 [P] [US1] Implement Pinia `useAuthStore` managing login, registration, logout, and token persistence in `frontend/src/stores/auth.ts`
- [X] T018 [US1] Configure Vue Router with strict global navigation guards (`router.beforeEach`) redirecting unauthenticated users to `/login` in `frontend/src/router/index.ts`
- [X] T019 [P] [US1] Build responsive Login and Registration views with form validation in `frontend/src/views/LoginView.vue` and `frontend/src/views/RegisterView.vue`

**Checkpoint**: Authentication flow and private route protection functional.

---

## Phase 4: User Story 2 - Document Ingestion & Management Dashboard (Priority: P1)

**Goal**: Allow authenticated users to upload text-heavy documents (.pdf, .txt, .md), process them in the background via `FastAPI BackgroundTasks` (chunking & 384-d embeddings), and manage them in a dashboard grid.

**Independent Test**: Upload a PDF/TXT document via drag-and-drop, verify background status transitions (`uploading` → `processing` → `ready`), view document ID/date/status, and verify deletion purges chunks.

### Implementation for User Story 2

- [X] T020 [P] [US2] Define Pydantic schemas for document upload responses, metadata, and status in `backend/src/schemas/document.py`
- [X] T021 [P] [US2] Implement `ChunkingService` using `langchain-text-splitters` (`RecursiveCharacterTextSplitter` configured for ~800 tokens and 15% overlap) for PDF, TXT, and Markdown in `backend/src/services/chunking_service.py`
- [X] T022 [P] [US2] Implement `EmbeddingService` loading local `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) for in-process embedding generation in `backend/src/services/embedding_service.py`
- [X] T023 [US2] Implement `DocumentService` with `process_document_background` executing extraction, chunking, local embedding, and user-scoped chunk persistence in `backend/src/services/document_service.py`
- [X] T024 [US2] Implement `/api/v1/documents` endpoints (upload with `FastAPI BackgroundTasks`, list documents, get status, and delete document with cascading chunk purge) strictly filtered by `user_id == current_user.id` in `backend/src/api/v1/documents.py`
- [X] T025 [P] [US2] Implement document management API client methods in `frontend/src/services/documentService.ts`
- [X] T026 [P] [US2] Implement Pinia `useDocumentStore` managing file list, upload queue, status polling, and deletion in `frontend/src/stores/document.ts`
- [X] T027 [P] [US2] Build DragDropZone component with drag-over feedback, file type restrictions (.pdf, .txt, .md), and 25MB limit validation in `frontend/src/components/documents/DragDropZone.vue`
- [X] T028 [US2] Build DocumentGrid component explicitly displaying filename, upload date, document UUID (with copy button), status badge, and view/delete actions in `frontend/src/components/documents/DocumentGrid.vue`
- [X] T029 [US2] Assemble DocumentsView integrating DragDropZone and DocumentGrid in `frontend/src/views/DocumentsView.vue`

**Checkpoint**: Document ingestion, background chunking/embedding, and dashboard management complete with strict tenant isolation.

---

## Phase 5: User Story 3 - Document-Grounded Real-Time Chat & Streaming (Priority: P1)

**Goal**: Provide real-time Q&A over FastAPI WebSockets where questions are embedded locally, matched against user-scoped pgvector chunks, and streamed back using `google-genai` async client with smooth auto-scrolling and optimistic UI.

**Independent Test**: Ask a question in chat, verify user-scoped vector search, confirm token-by-token streaming, verify anti-hallucination fallback on unknown topics, and check smooth auto-scroll.

### Implementation for User Story 3

- [X] T030 [P] [US3] Define Pydantic schemas for chat sessions, messages, and citation payloads in `backend/src/schemas/chat.py`
- [X] T031 [US3] Implement `RAGService` with `search_similar_chunks` executing strict tenant-scoped query `WHERE c.user_id = :user_id ORDER BY c.embedding <=> :query_vector LIMIT 5` and assembling strict anti-hallucination prompts in `backend/src/services/rag_service.py`
- [X] T032 [US3] Implement `GeminiService` using modern `google-genai` SDK async client (`genai.Client().aio.models.generate_content_stream`) targeting `gemini-2.5-flash` in `backend/src/services/gemini_service.py`
- [X] T033 [US3] Implement FastAPI WebSocket endpoint `/api/v1/ws/chat/{session_id}` handling JWT query handshake, local query embedding, pgvector search, async token streaming, and message persistence in `backend/src/api/v1/websocket.py`
- [X] T034 [P] [US3] Implement `useAutoScroll` composable with bottom-anchor detection to smoothly scroll during token streaming while halting auto-scroll when user scrolls up (preventing layout shifts) in `frontend/src/composables/useAutoScroll.ts`
- [X] T035 [P] [US3] Implement Pinia `useChatStore` supporting optimistic user message rendering, streaming token assembly, and message history in `frontend/src/stores/chat.ts`
- [X] T036 [US3] Build MessageBubble component rendering Markdown, code highlighting, and optimistic pending status in `frontend/src/components/chat/MessageBubble.vue`
- [X] T037 [US3] Build ChatWindow component with message stream list, smooth auto-scrolling container, and chat input in `frontend/src/components/chat/ChatWindow.vue`
- [X] T038 [US3] Assemble ChatView integrating active chat session streaming in `frontend/src/views/ChatView.vue`

**Checkpoint**: Core RAG pipeline, WebSocket token streaming, optimistic rendering, and layout shift-free auto-scrolling fully operational.

---

## Phase 6: User Story 4 - Conversation Thread Lifecycle & History (Priority: P2)

**Goal**: Enable users to create, switch between, rename, and delete conversation threads, as well as clear the current context memory.

**Independent Test**: Create multiple chat threads, switch between them to verify isolated message history, rename a thread, and click "Clear Context" to reset conversational memory.

### Implementation for User Story 4

- [X] T039 [P] [US4] Implement `/api/v1/chat/sessions` REST endpoints (list sessions, create, rename, delete, get session with messages) strictly scoped by `user_id == current_user.id` in `backend/src/api/v1/chat.py`
- [X] T040 [P] [US4] Implement chat session API client methods in `frontend/src/services/chatService.ts`
- [X] T041 [US4] Build ChatSidebar component listing historical threads, thread switching, "New Chat" button, and inline rename/delete actions in `frontend/src/components/chat/ChatSidebar.vue`
- [X] T042 [US4] Implement "Clear Current Context" button and confirmation modal in `frontend/src/components/chat/ClearContextModal.vue`

**Checkpoint**: Multi-thread conversation history management and context clearing complete.

---

## Phase 7: User Story 5 - Source Reference & Citation Attribution (Priority: P2)

**Goal**: Deliver grounded citations with document name, page number, and source snippet drawer alongside assistant responses.

**Independent Test**: Submit a query answerable from an uploaded PDF and verify citation badges appear with correct document name and page number.

### Implementation for User Story 5

- [X] T043 [US5] Enhance `RAGService` to format structured citations with document ID, document name, page number, and snippet in `backend/src/services/rag_service.py`
- [X] T044 [US5] Build CitationPill component displaying clickable source badges and a slide-out source snippet drawer in `frontend/src/components/chat/CitationPill.vue`

**Checkpoint**: Grounded citations and verification drawer complete.

---

## Phase 8: Bonus Features & Client Resilience

**Purpose**: Implement resilient WebSocket client auto-reconnect, persistent theme toggling, and optimistic UI polish.

- [X] T045 [P] Implement `useTheme` composable managing persistent Dark/Light mode with `localStorage` and `document.documentElement` class toggle in `frontend/src/composables/useTheme.ts`
- [X] T046 [P] Build ThemeToggle button component with Lucide icons in `frontend/src/components/common/ThemeToggle.vue`
- [X] T047 Implement resilient `useChatWebSocket` composable with exponential backoff auto-reconnect (1s, 2s, 4s, 8s...), heartbeat ping/pong, and session context restoration in `frontend/src/composables/useChatWebSocket.ts`

**Checkpoint**: Resilient WebSocket auto-recovery and persistent dark/light theme complete.

---

## Phase 9: Submission Artifacts & Containerization

**Purpose**: Scaffolding docker compose, documenting prompt engineering in `PROMPTS.md`, and structuring `README.md`.

- [X] T048 Create `docker-compose.yml` orchestrating PostgreSQL (with pgvector), FastAPI backend, and Vue 3 frontend in `docker-compose.yml`
- [X] T049 [P] Create backend `Dockerfile` in `backend/Dockerfile` and frontend `Dockerfile` with Nginx in `frontend/Dockerfile`
- [X] T050 Draft comprehensive `PROMPTS.md` documenting LLM system prompt engineering, strict reference grounding instructions, and anti-hallucination templates in `PROMPTS.md`
- [X] T051 Draft comprehensive `README.md` detailing architecture, multi-tenant isolation model, environment variables, local setup instructions, Docker setup, and architectural trade-offs in `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies
```text
Phase 1: Setup
    │
    ▼
Phase 2: Foundational (BLOCKS all user stories)
    │
    ├───────────────────────┬───────────────────────┐
    ▼                       ▼                       ▼
Phase 3: US1 (Auth)    Phase 4: US2 (Docs)     Phase 5: US3 (Chat & RAG)
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            │
                            ▼
                    Phase 6: US4 (Threads)
                            │
                            ▼
                    Phase 7: US5 (Citations)
                            │
                            ▼
                    Phase 8: Bonus Features
                            │
                            ▼
                    Phase 9: Deliverables
```

### Parallel Opportunities

- **Phase 1**: Backend setup (T001), frontend setup (T002), and linting (T003) can execute in parallel.
- **Phase 2**: Config (T005), Alembic setup (T006), Security utilities (T009), and Exceptions (T010) can execute in parallel once database engine (T004) is ready.
- **Phase 3 (US1)**: Frontend store (T017) and Login/Register views (T019) can execute in parallel with backend auth service (T013).
- **Phase 4 (US2)**: Chunking service (T021) and Embedding service (T022) can execute in parallel; frontend DragDropZone (T027) can execute in parallel with backend document routes (T024).
- **Phase 5 (US3)**: Gemini service (T032), auto-scroll composable (T034), and MessageBubble component (T036) can execute in parallel.
- **Phase 8 (Bonus)**: `useTheme` (T045) and `ThemeToggle` (T046) can execute in parallel.
- **Phase 9 (Deliverables)**: Backend Dockerfile (T049), `PROMPTS.md` (T050), and `README.md` (T051) can execute in parallel.

---

## Implementation Strategy

### MVP Scope (Phases 1, 2, 3, 4, 5)
1. Complete Setup & Foundational database + pgvector schema.
2. Deliver User Authentication & Isolated Workspace (US1).
3. Deliver Document Ingestion & Background Embedding (US2).
4. Deliver Real-Time Document Q&A with WebSocket Streaming (US3).
5. **Validate MVP**: User registers, uploads PDF, asks question, and receives grounded real-time streaming answer.

### Incremental Enhancements (Phases 6, 7, 8, 9)
6. Add Conversation Thread Lifecycle & Context Clearing (US4).
7. Add Source Citations & Snippet Drawer (US5).
8. Add WebSocket Auto-Reconnect & Persistent Dark/Light Mode (Bonus).
9. Add Docker Compose orchestration, `PROMPTS.md`, and `README.md` (Deliverables).
