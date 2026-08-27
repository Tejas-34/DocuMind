# DocuMind: Secure, Multi-Tenant Document Q&A Web Application

DocuMind is an enterprise-grade, privacy-first Document Question & Answering platform. Users can securely register, upload documents (PDF, TXT, MD), and interact with an AI assistant via full-duplex WebSockets for real-time streamed, strictly grounded answers with verifiable citations.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Frontend ["Vue 3 SPA (Vite + TypeScript + Tailwind)"]
        UI["Views: Auth, Documents, Chat"]
        Pinia["Pinia Stores: useAuth, useDoc, useChat"]
        Composables["useChatWebSocket (Auto-Reconnect) <br/> useAutoScroll (Anti-Layout Shift) <br/> useTheme (Dark/Light)"]
    end

    subgraph Backend ["FastAPI (Python 3.10+ Async)"]
        Router["FastAPI REST & WebSocket Routers"]
        Deps["Auth Middleware (JWT get_current_user)"]
        BG["FastAPI BackgroundTasks Ingestion"]
        Chunker["RecursiveCharacterTextSplitter (800 tok / 15% overlap)"]
        LocalEmbed["Local sentence-transformers (all-MiniLM-L6-v2, 384-d)"]
        RAG["RAG Service (Strict user_id pgvector Cosine Search)"]
        GeminiAsync["Google GenAI Async Client (gemini-2.5-flash)"]
    end

    subgraph Storage ["Unified PostgreSQL Instance"]
        PG[(PostgreSQL 16 + pgvector)]
        T1["users"]
        T2["documents (user_id FK)"]
        T3["chunks (user_id FK, HNSW Vector Index)"]
        T4["chat_sessions (user_id FK)"]
        T5["messages (user_id FK)"]
    end

    UI -->|REST API & JWT| Router
    UI <-->|WebSocket Stream /ws/chat| Router
    Router --> Deps
    Deps --> RAG
    Router --> BG
    BG --> Chunker --> LocalEmbed --> PG
    RAG --> LocalEmbed
    RAG -->|Cosine Distance <=> Scoped by user_id| PG
    RAG --> GeminiAsync
    GeminiAsync -->|Async Token Chunks| Router
```

---

## 🔒 Absolute Tenant Data Isolation Invariant

1. **Mandatory Foreign Key**: Every single operational table (`documents`, `chunks`, `chat_sessions`, `messages`) contains `user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE`.
2. **Repository & Query Layer Enforcement**: Every database query—specifically vector similarity retrieval—strictly enforces tenant scoping:
   ```sql
   SELECT c.id, c.document_id, d.filename, c.page_number, c.content,
          (c.embedding <=> :query_vector) AS distance
   FROM chunks c
   JOIN documents d ON d.id = c.document_id
   WHERE c.user_id = :authenticated_user_id
     AND d.status = 'ready'
   ORDER BY distance ASC
   LIMIT 5;
   ```
3. **Zero Cross-Tenant Leakage**: Attempting to query another tenant's document ID or session ID yields an immediate HTTP `404 Not Found`.

---

## ✨ Core Features & Detailed UI Implementation

- **Drag-and-Drop Ingestion**: Upload zone with dragover animation, supporting `.pdf`, `.txt`, and `.md` files up to 25MB.
- **Document Management Grid**: Displays **Filename**, **Upload Date**, **Document UUID** (with click-to-copy), **Status Badge** (`uploading`, `processing`, `ready`, `failed`), and **View/Delete actions**.
- **Real-Time WebSocket Streaming**: Non-blocking token streaming powered by the modern `google-genai` async client (`genai.Client().aio.models.generate_content_stream`).
- **Strict Grounding & Anti-Hallucination**: Explicit system prompt forces the assistant to only answer using uploaded document excerpts and provide a structured fallback when facts are absent.
- **Source Attribution & Citations**: Responses include clickable source badges displaying document name, page number, and source text snippets.
- **Layout Shift Prevention (`useAutoScroll`)**: Smart bottom-anchor detection automatically scrolls when new tokens arrive, but halts auto-scroll when the user scrolls up to inspect previous text.
- **Resilient Auto-Reconnect**: WebSocket client automatically reconnects with exponential backoff (1s, 2s, 4s, 8s...) and restores session context upon network recovery.
- **Optimistic UI Updates**: User queries appear immediately in the chat thread with a pending status.
- **Persistent Dark/Light Mode**: Synced with system preferences and persisted in `localStorage`.

---

## ⚙️ Environment Configuration

### Backend (`backend/.env`)
| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/documind` |
| `JWT_SECRET` | Secret key for signing HMAC-SHA256 JWT tokens | Minimum 32 characters |
| `JWT_ALGORITHM` | Algorithm used for JWT encoding | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Lifetime of access tokens in minutes | `1440` (24 hours) |
| `GEMINI_API_KEY` | Google Gemini API Key | Set from Google AI Studio |
| `GEMINI_MODEL` | Target Gemini model | `gemini-2.5-flash` |
| `EMBEDDING_MODEL` | Local sentence-transformers model | `sentence-transformers/all-MiniLM-L6-v2` |
| `MAX_FILE_SIZE_MB` | Maximum allowed document upload size | `25` |

---

## 🚀 Quickstart & Setup Guide

### Option 1: Running with Docker Compose (Recommended)

1. Ensure Docker & Docker Compose are running.
2. Provide your Gemini API Key:
   ```bash
   export GEMINI_API_KEY="your_actual_gemini_api_key"
   ```
3. Start all services:
   ```bash
   docker compose up --build
   ```
4. Access the application:
   - **Frontend UI**: [http://localhost](http://localhost)
   - **Backend REST Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 2: Running Locally for Development

#### 1. Database (PostgreSQL with pgvector)
Ensure PostgreSQL 16+ is running with pgvector:
```sql
CREATE DATABASE documind;
\c documind;
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 2. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start API server
uvicorn src.main:app --reload --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## ⚖️ Architectural Trade-Offs & Decisions

| Decision | Selected Approach | Alternative Rejected | Rationale |
| :--- | :--- | :--- | :--- |
| **Vector Storage** | Unified PostgreSQL + `pgvector` | Dedicated Vector DB (Pinecone/Milvus) | Eliminates distributed state synchronization, guarantees ACID transactions, and enables row-level tenant filtering in a single SQL query. |
| **Embeddings** | Local `all-MiniLM-L6-v2` (384-d) | Cloud Embedding APIs | Zero network round-trip overhead on ingestion & chat streaming; lower memory & storage footprint for HNSW indexes. |
| **Real-Time Transport** | FastAPI WebSockets | Server-Sent Events (SSE) + HTTP POST | Full-duplex communication allows bidirectional control (client cancellation, session heartbeats, streaming token acks) without HTTP reconnect overhead. |
| **Scroll Experience** | Smart Anchor Detection (`useAutoScroll`) | Aggressive auto-scroll | Prevents layout jumping and reading interruptions when users scroll up to read previous excerpts during streaming. |
