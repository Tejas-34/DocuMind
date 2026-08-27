# Technical Research & Architecture Decisions: Multi-Tenant Document Q&A Platform

**Feature**: [spec.md](./spec.md) | **Date**: 2026-08-27

---

## 1. Unified Relational & Vector Storage (PostgreSQL + pgvector)

### Decision
Use a single PostgreSQL instance with the `pgvector` extension, managed via `SQLAlchemy 2.0` (async) and `asyncpg`, with schema migrations automated through `Alembic`.

### Rationale
- **Zero Synchronization Lag**: Co-locating relational metadata (`users`, `documents`, `chat_sessions`, `messages`) and vector chunks in the same database avoids dual-write consistency problems and distributed failure modes.
- **Strict Multi-Tenant Scoping**: Allows combining relational `user_id` filtering with vector similarity search in a single atomic SQL statement:
  ```sql
  SELECT id, document_id, content, page_number, 
         (embedding <=> :query_vector) AS distance
  FROM chunks
  WHERE user_id = :user_id
  ORDER BY distance ASC
  LIMIT :top_k;
  ```
- **HNSW Indexing**: `pgvector` supports HNSW cosine distance indexing (`vector_cosine_ops`), providing sub-10ms retrieval latency for millions of tenant-isolated vectors.

### Alternatives Considered
- **Dedicated Vector DB (Pinecone, Qdrant, Milvus)**: Rejected due to complex cross-database metadata synchronization, separate authentication boundaries, and increased operational overhead.

---

## 2. Local Embedding Generation (`sentence-transformers` / `all-MiniLM-L6-v2`)

### Decision
Generate 384-dimensional text embeddings in-process using `sentence-transformers` (`all-MiniLM-L6-v2`) running on CPU/MPS/CUDA.

### Rationale
- **Zero Network Bottleneck**: Eliminates external API roundtrips during document ingestion and real-time chat queries.
- **Deterministic & High-Throughput**: `all-MiniLM-L6-v2` produces dense 384-dimensional vectors with minimal latency (<15ms per chunk on modern CPU) and low memory footprint (~120MB model weight).
- **Storage & Indexing Efficiency**: 384 dimensions consume substantially less RAM and storage in `pgvector` compared to 1536-d or 3072-d models, accelerating cosine distance calculations.

---

## 3. Asynchronous LLM Generation (`google-genai` Modern SDK)

### Decision
Use the official modern `google-genai` Python SDK targeting `gemini-2.5-flash` with its async client:
```python
from google import genai
from google.genai import types

client = genai.Client()
response_stream = await client.aio.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.0,
        system_instruction=STRICT_REFERENCE_SYSTEM_PROMPT
    )
)
```

### Rationale
- **Asynchronous Token Streaming**: Non-blocking `aio` client seamlessly yields chunks to the FastAPI WebSocket loop without holding Python GIL or blocking concurrent tenants.
- **Ultra-Low Latency**: Gemini Flash delivers rapid time-to-first-token (TTFT < 400ms) with strict grounding instruction following.

---

## 4. Ingestion, Extraction & Chunking Strategy

### Decision
- **File Extraction**: `pypdf` for PDF text and page boundary extraction; native UTF-8 streaming for plain text (`.txt`).
- **Text Chunking**: `langchain-text-splitters` with `RecursiveCharacterTextSplitter` configured for:
  - Chunk Size: ~800 tokens (~3200 characters)
  - Chunk Overlap: 15% (~120 tokens / 480 characters)
  - Separators: `["\n\n", "\n", ". ", " ", ""]` to preserve semantic sentence and paragraph boundaries.
- **Metadata Tagging**: Each chunk stores `user_id`, `document_id`, `chunk_index`, and `page_number` for citation attribution.

---

## 5. Real-Time Chat & Resilient WebSocket Infrastructure

### Decision
Implement chat interactions using FastAPI native WebSockets (`/api/v1/ws/chat/{session_id}?token=...`) coupled with a resilient client-side composable (`useChatWebSocket`).

### Robust Client Protocol Features:
- **Automatic Reconnection**: Exponential backoff with jitter (1s, 2s, 4s, 8s, max 30s) upon unexpected disconnection.
- **State & Context Restoration**: Client auto-resumes active session subscription and fetches missing messages upon reconnect.
- **Heartbeat / Keepalive**: Client transmits periodic ping frames every 25s; server responds with pong.
- **Optimistic UI Dispatch**: User messages are immediately rendered into the chat view with a temporary status (`pending`), transitioning to `sent` on WebSocket acknowledgement.

---

## 6. Frontend Architecture & Detailed UI Engineering (Vue 3 + Pinia + Tailwind CSS)

### Decision
Build a responsive Single-Page Application (SPA) using Vue 3 Composition API (`<script setup>`), Pinia state stores, and Tailwind CSS.

### Key Frontend Implementations:

#### A. Strict Vue Router Navigation Guards
- Global navigation guard (`router.beforeEach`) verifies authentication state via `useAuthStore`.
- Protected routes (`/dashboard`, `/documents`, `/chat`, `/chat/:sessionId`) require valid JWT. Unauthenticated accesses are redirected to `/login` with a `redirect` query parameter.
- Auth tokens are held in Pinia state with secure `localStorage` persistence and attached via Axios request interceptors.

#### B. Document Management View (`/documents`)
- **Drag-and-Drop Dropzone**: Native HTML5 drag-and-drop zone with visual hover feedback, file type validation (`.pdf`, `.txt`), size checks (max 25MB), and multi-file queueing.
- **Document List & Grid View**: Toggleable table/grid explicitly displaying:
  - Document Title & Original Filename
  - Upload Date (relative and absolute timestamps)
  - Document UUID
  - File Size & MIME badge
  - Processing Status (`uploading`, `processing`, `ready`, `failed`)
  - Action buttons: `Delete` (with confirmation modal) and `View Details / Metadata`.

#### C. Chat Interface View (`/chat`)
- **Sidebar**:
  - List of historical conversation threads ordered by last activity.
  - Active thread highlighting and inline thread rename / delete actions.
  - "New Chat" primary button.
  - "Clear Current Context" action button to reset conversational context while preserving thread structure.
- **Chat Window & Layout Shift Prevention**:
  - Auto-scrolling engine utilizing `ResizeObserver` and scroll anchor detection: Auto-scrolls down smoothly during token streaming **only** if the user is already pinned to the bottom. If the user scrolls up to review earlier citations, auto-scroll pauses to prevent disruptive layout shifts.
  - Optimistic message bubbles rendered instantly upon send.
  - Real-time token streaming with typing indicator and Markdown syntax rendering.
  - Grounding citation pills displaying document title, page number, and source snippet drawer.

#### D. Persistent Dark / Light Theme
- `useTheme` composable with system preference detection (`prefers-color-scheme`) and `localStorage` persistence.
- Toggles the `dark` class on `document.documentElement` for seamless Tailwind `dark:` variant styling across all views, sidebars, modals, and code snippets.

---

## 7. Strict Data Isolation & Security Architecture

1. **JWT Verification**: Every REST request and WebSocket connection validates the HMAC-SHA256 JWT, resolving `current_user: User`.
2. **Mandatory Foreign Key**: `user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE` on all operational entities (`documents`, `chunks`, `chat_sessions`, `messages`).
3. **Repository-Level Invariant**: Every database query method requires `user_id` as a mandatory parameter and enforces `WHERE user_id = :user_id`.
4. **Anti-Hallucination Prompting**: System prompt strictly commands the LLM to only answer from provided context and reply with a specific fallback if not present.