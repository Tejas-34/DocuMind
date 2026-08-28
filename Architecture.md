# DocuMind: Complete Application Architecture & Design Blueprint

DocuMind is an enterprise-grade, multi-tenant Document Q&A system designed for strict data isolation, fast local vector retrieval, and low-latency token streaming.

---

## 🛠️ Technology Stack & Tools Used

| Layer | Tool / Technology | Version / Spec | Purpose & Implementation |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | **Vue 3** + **Vite** + **TypeScript** | Vue 3.5+, Vite 6+ | Reactive SPA with `<script setup>`, strict typing, and composables |
| **State Management** | **Pinia** | Pinia 2.3+ | Centralized reactive stores: `auth.ts`, `document.ts`, `chat.ts` |
| **Styling & Icons** | **Tailwind CSS** + **Lucide Icons** | Tailwind v4, Lucide Vue | Modern responsive dark/light UI, modal overlays, dropzones |
| **Reverse Proxy** | **Nginx** | Alpine | Serves static SPA bundle, proxies `/api/` to backend, handles HTTP → WebSocket upgrade headers |
| **Backend Framework** | **FastAPI** (Python 3.10+) | Uvicorn / Async ASGI | Async REST endpoints, background tasks, native WebSocket routes |
| **ORM & Database Driver** | **SQLAlchemy 2.0** + **asyncpg** | Async engine + Sessions | Fully asynchronous database queries, relational mapping, connection pooling |
| **Relational & Vector DB** | **PostgreSQL 16** + **pgvector** | `pgvector/pgvector:pg16` | Unified relational storage + HNSW cosine vector index (`vector(384)`) |
| **Local Embeddings** | **FastEmbed** | `BAAI/bge-small-en-v1.5` | 384-dimensional local ONNX embedding inference (zero external latency) |
| **Document Processing** | **PyPDF** + **LangChain Text Splitters** | `RecursiveCharacterTextSplitter` | PDF page extraction, ~800 tokens (3200 chars) chunks with 15% overlap |
| **LLM Inference** | **Google GenAI Async SDK** | `google-genai` (Gemini 2.5/3.6 Flash) | Low-temperature (0.0) streaming RAG answer generation with strict document grounding |
| **Authentication** | **PyJWT** + **Passlib** | HMAC-SHA256 (HS256) + bcrypt | Stateless bearer JWT token authentication & WebSocket query token handshake |
| **Containerization** | **Docker** & **Docker Compose** | Multi-container compose | Orchestration of `postgres`, `backend`, and `frontend` services |

---

## 🏛️ Diagram 1: System Component & Layered Architecture

This high-level architecture diagram illustrates the end-to-end topology, showing how traffic flows from the browser through Nginx, FastAPI, the local FastEmbed engine, the PostgreSQL/pgvector database, and the external Gemini LLM.

```mermaid
flowchart TB
    subgraph ClientTier ["🖥️ Client Tier (Browser)"]
        SPA["Vue 3 Single Page Application"]
        subgraph PiniaStores ["Pinia State Management"]
            AuthStore["useAuthStore<br/>(JWT Token & User State)"]
            DocStore["useDocumentStore<br/>(File List & Polling Loop)"]
            ChatStore["useChatStore<br/>(Sessions & Optimistic UI)"]
        end
        subgraph ClientComposables ["Composables"]
            WSComp["useChatWebSocket<br/>(Auto-Reconnect & Heartbeat)"]
            ScrollComp["useAutoScroll<br/>(Bottom Anchor Detection)"]
        end
        SPA --> PiniaStores
        SPA --> ClientComposables
    end

    subgraph GatewayTier ["🌐 Gateway Tier"]
        Nginx["Nginx Reverse Proxy (:80)<br/>- Serves Vue Static Files<br/>- Upgrades HTTP to WebSocket<br/>- Proxies /api to Backend"]
    end

    subgraph AppTier ["⚡ Backend Application Tier (FastAPI Async ASGI :8000)"]
        RouterAuth["/api/v1/auth<br/>(Register, Login, Me)"]
        RouterDoc["/api/v1/documents<br/>(Upload, List, Delete)"]
        RouterChat["/api/v1/chat/sessions<br/>(CRUD Session Management)"]
        WSHandler["/api/v1/ws/chat/{session_id}<br/>(WebSocket Full-Duplex Stream)"]
        
        SecurityDeps["Auth Middleware / Deps<br/>(JWT get_current_user)"]
        BGTask["FastAPI BackgroundTasks<br/>(Async Ingestion Pipeline)"]
        
        subgraph Services ["Core Business Services"]
            DocSvc["DocumentService<br/>(Orchestrates Ingestion)"]
            ChunkSvc["ChunkingService<br/>(PyPDF + RecursiveSplitter)"]
            EmbedSvc["EmbeddingService<br/>(FastEmbed ONNX 384-d)"]
            RAGSvc["RAGService<br/>(Strict Tenant Cosine Query)"]
            GeminiSvc["GeminiService<br/>(google.genai Async Stream)"]
        end
    end

    subgraph DataTier ["🗄️ Unified Storage Tier (PostgreSQL 16 + pgvector :5432)"]
        T_Users[("users<br/>(id, email, password)")]
        T_Docs[("documents<br/>(id, user_id, status, total_pages)")]
        T_Chunks[("chunks<br/>(id, user_id, doc_id, embedding, content)<br/>[HNSW Index: m=16, ef=64]")]
        T_Sessions[("chat_sessions<br/>(id, user_id, title)")]
        T_Messages[("messages<br/>(id, user_id, session_id, role, citations)")]
    end

    subgraph ExternalTier ["☁️ External Cloud AI"]
        GeminiAPI["Google Gemini AI Studio<br/>(gemini-2.5-flash / gemini-3.6-flash)"]
    end

    %% Network Connections
    SPA <-->|HTTP REST & WSS| Nginx
    Nginx -->|Proxy REST| RouterAuth & RouterDoc & RouterChat
    Nginx <-->|WebSocket Upgrade| WSHandler
    
    RouterAuth --> SecurityDeps
    RouterDoc --> SecurityDeps
    RouterChat --> SecurityDeps
    
    RouterDoc --> BGTask
    BGTask --> DocSvc
    DocSvc --> ChunkSvc --> EmbedSvc --> T_Chunks
    DocSvc --> T_Docs
    
    WSHandler --> SecurityDeps
    WSHandler --> RAGSvc
    RAGSvc --> EmbedSvc
    RAGSvc -->|pgvector <=> Cosine Search| T_Chunks
    RAGSvc --> GeminiSvc
    GeminiSvc <-->|Async Stream| GeminiAPI
    WSHandler --> T_Messages & T_Sessions
    RouterAuth --> T_Users
```

---

## 🔄 Diagram 2: Document Ingestion Pipeline & Short Polling Design

The application uses **HTTP Short Polling (3-second interval)** for document status tracking. Here is how document ingestion, async background chunking, embedding generation, and status updates work:

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Browser
    participant Store as useDocumentStore (Pinia)
    participant Nginx as Nginx Proxy
    participant DocAPI as FastAPI /api/v1/documents
    participant BG as FastAPI BackgroundTasks
    participant Chunker as ChunkingService (PyPDF + Splitter)
    participant FastEmbed as EmbeddingService (FastEmbed ONNX)
    participant DB as PostgreSQL (documents & chunks)

    %% Step 1: Upload
    User->>Store: Drop file (.pdf, .txt, .md)
    Store->>Nginx: POST /api/v1/documents (multipart/form-data + JWT)
    Nginx->>DocAPI: Proxy POST /api/v1/documents
    DocAPI->>DB: INSERT into documents (status="processing", user_id)
    DocAPI->>BG: Queue DocumentService.process_document_background()
    DocAPI-->>Store: HTTP 202 Accepted (doc metadata with status="processing")
    Store-->>User: Optimistically render file with "processing" badge

    %% Step 2: Ingestion & Embedding in Background
    critical Background Ingestion Task
        BG->>Chunker: extract_and_chunk_pdf(file_bytes)
        Chunker-->>BG: Return text chunks (~800 tok, 15% overlap) + page numbers
        BG->>FastEmbed: embed_documents(chunk_texts) (batch size 32)
        FastEmbed-->>BG: 384-dimensional vector embeddings
        BG->>DB: INSERT INTO chunks (user_id, document_id, embedding, content, page_number)
        BG->>DB: UPDATE documents SET status="ready", total_pages=N WHERE id=doc_id
    end

    %% Step 3: Frontend Short Polling
    Note over Store,DocAPI: Frontend detects pending status and triggers checkAndStartPolling()
    loop Every 3000ms Polling Interval
        Store->>DocAPI: GET /api/v1/documents
        DocAPI->>DB: SELECT * FROM documents WHERE user_id = :user_id
        DB-->>DocAPI: Return documents list
        DocAPI-->>Store: JSON array with current statuses
        alt Status is still 'processing'
            Store-->>User: Keep "processing" spinner active
        else Status transitioned to 'ready' or 'failed'
            Store-->>User: Update badge to "ready" (Green) / "failed" (Red)
            Note over Store: All documents resolved -> stopPolling() clears interval
        end
    end
```

### 🔍 How Document Polling Works in Code:
1. Located in `frontend/src/stores/document.ts`.
2. When `fetchDocuments()` or `uploadFile()` executes, `checkAndStartPolling()` checks `documents.value.some(d => d.status === 'uploading' || d.status === 'processing')`.
3. If pending files exist, `setInterval` triggers `documentService.listDocuments()` every **3000ms**.
4. Once all documents transition to `'ready'` or `'failed'`, `clearInterval` is called to halt background network requests.

---

## ⚡ Diagram 3: Real-Time RAG & WebSocket Streaming Architecture

The chat interface uses **Full-Duplex WebSockets (`/api/v1/ws/chat/{session_id}`)** for bidirectional streaming, tenant-scoped vector search, token generation, and ping/pong heartbeats.

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Browser
    participant WSComp as useChatWebSocket (Vue Composable)
    participant Nginx as Nginx Proxy
    participant WSAPI as FastAPI WebSocket (/ws/chat/{session_id})
    participant RAG as RAGService
    participant FastEmbed as EmbeddingService
    participant DB as PostgreSQL (pgvector HNSW)
    participant Gemini as Google Gemini API (Async Stream)

    %% 1. Handshake
    User->>WSComp: Open Chat Session
    WSComp->>Nginx: GET /api/v1/ws/chat/{session_id}?token={JWT} (Upgrade: websocket)
    Nginx->>WSAPI: Forward WS Handshake
    WSAPI->>WSAPI: decode_access_token(token) -> Validate user_id
    WSAPI->>DB: SELECT * FROM chat_sessions WHERE id=session_id AND user_id=user_id
    alt Token Invalid or Session Belongs to Another Tenant
        WSAPI-->>WSComp: Close Frame 4401 (Unauthorized) / 4403 (Forbidden)
    else Authorized
        WSAPI-->>WSComp: Accept Connection + {"type": "connected", "session_id": "..."}
        WSComp->>WSComp: startHeartbeat() (Send ping every 25s)
    end

    %% 2. Ping-Pong Heartbeat Loop
    Note over WSComp,WSAPI: Background Keep-Alive (every 25 seconds)
    WSComp->>WSAPI: {"type": "ping"}
    WSAPI-->>WSComp: {"type": "pong"}

    %% 3. Query & RAG Execution
    User->>WSComp: Submits query: "What are the project deliverables?"
    WSComp->>WSComp: Optimistic UI message rendered immediately
    WSComp->>WSAPI: {"type": "query", "text": "...", "client_msg_id": "opt-123"}
    
    WSAPI->>DB: INSERT INTO messages (role="user", content=query, session_id, user_id)
    WSAPI-->>WSComp: {"type": "status", "step": "searching_documents", "message": "Searching..."}

    WSAPI->>RAG: search_similar_chunks(user_id, query, top_k=5)
    RAG->>FastEmbed: embed_query(query) -> [384-d float vector]
    RAG->>DB: SELECT c.id, c.content, c.page_number, d.filename, (c.embedding <=> :query_vector) AS distance<br/>WHERE c.user_id = :user_id AND d.status = 'ready'<br/>ORDER BY distance LIMIT 5
    DB-->>RAG: Top 5 Relevant Chunks

    WSAPI->>RAG: build_prompt_with_context(query, chunks, history)
    WSAPI-->>WSComp: {"type": "status", "step": "generating", "message": "Streaming answer..."}

    %% 4. Streaming Token Generation
    WSAPI->>Gemini: aio.models.generate_content_stream(model="gemini-2.5-flash", prompt, temp=0.0)
    loop Asynchronous Token Stream
        Gemini-->>WSAPI: Token Chunk ("DocuMind", " delivers", "...")
        WSAPI-->>WSComp: {"type": "token", "content": "DocuMind"}
        WSComp-->>User: Append token to UI bubble (useAutoScroll anchors view)
    end

    %% 5. Persistence & Finalization
    WSAPI->>DB: INSERT INTO messages (role="assistant", content=full_content, citations=citations)
    WSAPI->>DB: UPDATE chat_sessions SET title = auto_generated_title WHERE id = session_id
    WSAPI-->>WSComp: {"type": "done", "client_msg_id": "opt-123", "message_id": "...", "citations": [...]}
    WSComp-->>User: Display clickable citation pills (Document name, page, snippet)
```

---

## ⚖️ Deep Dive: Interaction Designs & Protocols Compared

DocuMind uses three distinct communication patterns strategically chosen for specific operational requirements:

```mermaid
flowchart LR
    subgraph REST ["1. REST (HTTP JSON)"]
        direction TB
        R1["Auth: /auth/login, /auth/register"]
        R2["Session CRUD: /chat/sessions"]
        R3["Document Management: /documents"]
        RDesc["<b>Pattern:</b> Stateless Request-Response<br/><b>Best For:</b> CRUD operations, Auth, File Uploads"]
    end

    subgraph Polling ["2. Short Polling (HTTP GET 3s)"]
        direction TB
        P1["useDocumentStore.ts"]
        P2["Triggered by status='processing'"]
        P3["Stops when status='ready'|'failed'"]
        PDesc["<b>Pattern:</b> Periodic HTTP GET check<br/><b>Best For:</b> Ingestion pipeline status without maintaining stateful channels"]
    end

    subgraph WebSockets ["3. Full-Duplex WebSockets"]
        direction TB
        W1["Endpoint: /ws/chat/{session_id}"]
        W2["25s Heartbeat Ping/Pong"]
        W3["Auto-Reconnect Backoff (1s-30s)"]
        W4["Real-time Token Stream & Citations"]
        WDesc["<b>Pattern:</b> Bidirectional Persistent TCP<br/><b>Best For:</b> Low-latency LLM streaming, query cancellation, context clear"]
    end
```

### 1. WebSocket Protocol & Framing Specification
Implemented in `backend/src/api/v1/websocket.py` and `frontend/src/composables/useChatWebSocket.ts`:

| Direction | Frame Type | Payload Schema | Action / Purpose |
| :--- | :--- | :--- | :--- |
| **Client → Server** | `query` | `{"type": "query", "text": "...", "client_msg_id": "opt-123"}` | Submits user prompt to initiate vector search and streaming. |
| **Client → Server** | `ping` | `{"type": "ping"}` | Sent every 25s to keep WebSocket connections open through proxies. |
| **Client → Server** | `clear_context` | `{"type": "clear_context"}` | Resets short-term conversation context for the active session. |
| **Client → Server** | `cancel` | `{"type": "cancel"}` | Aborts ongoing LLM generation stream. |
| **Server → Client** | `connected` | `{"type": "connected", "session_id": "...", "user_id": "..."}` | Acknowledges successful JWT auth and session ownership. |
| **Server → Client** | `pong` | `{"type": "pong"}` | Heartbeat response. |
| **Server → Client** | `status` | `{"type": "status", "step": "searching_documents"\|"generating", "message": "..."}` | Provides real-time phase updates to the UI. |
| **Server → Client** | `token` | `{"type": "token", "content": "string"}` | Streamed individual word/subword token from Gemini. |
| **Server → Client** | `done` | `{"type": "done", "client_msg_id": "...", "content": "...", "citations": [...]}` | Signals completion, persists message ID, and delivers citation metadata. |
| **Server → Client** | `error` | `{"type": "error", "message": "..."}` | Delivers user-facing error details if generation or search fails. |

### 2. Auto-Reconnect & Resilience Strategy
- **Exponential Backoff**: If disconnected unexpectedly (`event.code !== 1000`), `useChatWebSocket.ts` calculates backoff:
  `Delay = min(1000 * 2^(attempt - 1), 30000) ms`
  *(Attempts reconnect after 1s, 2s, 4s, 8s, 16s, up to max 30s, capped at 5 attempts).*
- **Auto-scroll Protection**: `useAutoScroll.ts` monitors scroll offset: auto-scroll is maintained as long as the user is anchored to the bottom, but automatically suspends if the user scrolls up to review previous citation sources.

---

## 🔒 Multi-Tenant Data Isolation Invariant

Every database model incorporates strict row-level tenant foreign keys (`user_id UUID REFERENCES users(id) ON DELETE CASCADE`):

```sql
-- Enforced in RAGService.search_similar_chunks()
SELECT 
    c.id, 
    c.document_id, 
    d.filename, 
    c.page_number, 
    c.content,
    (c.embedding <=> :query_vector) AS distance
FROM chunks c
JOIN documents d ON d.id = c.document_id
WHERE c.user_id = :authenticated_user_id
  AND d.user_id = :authenticated_user_id
  AND d.status = 'ready'
ORDER BY distance ASC
LIMIT 5;
```

This guarantees that even with billions of embedded chunks in the shared `pgvector` HNSW index, **zero cross-tenant data leakage** is mathematically possible. Attempting to query an ID belonging to another user results in an immediate `404 Not Found`.
