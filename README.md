# DocuMind: Multi-Tenant AI Document Assistant

DocuMind is an enterprise-grade, privacy-first, multi-tenant Document Q&A web application. It enables users to securely create an account, upload documents (`.pdf`, `.txt`, `.md`), and query their private knowledge base via real-time WebSocket token streaming with strict document grounding and verifiable citations.

---

## 🏗️ Technology Choices & Architectural Rationale

| Layer / Component | Technology | Rationale & Trade-offs |
| :--- | :--- | :--- |
| **Frontend Framework** | **Vue 3 (Composition API) + Vite + TypeScript** | High reactivity, ultra-fast HMR, strict type safety, and clean separation of concerns using composables (`useChatWebSocket`, `useAutoScroll`, `useTheme`). |
| **State Management** | **Pinia** | Centralized, reactive state stores (`auth.ts`, `document.ts`, `chat.ts`) supporting optimistic UI updates and reactive session caching. |
| **Styling & Icons** | **Tailwind CSS + Lucide Icons** | Utility-first styling with responsive layouts, dark/light theme support, and lightweight icons. |
| **Backend API** | **FastAPI (Python 3.10+)** | High-performance asynchronous ASGI framework with native asyncpg database support, background tasks, and native WebSocket routes. |
| **Relational & Vector DB** | **PostgreSQL 16 + pgvector** | Unified operational and vector database. Eliminates distributed transactions and sync delays between separate relational and vector stores; guarantees strict ACID isolation and tenant-scoped HNSW cosine vector search in a single SQL query. |
| **Local Dense Embeddings** | **FastEmbed (`BAAI/bge-small-en-v1.5`)** | 384-dimensional dense semantic embeddings executed locally via ONNX runtime on CPU. Zero external embedding API latency, predictable inference performance, and low vector storage footprint. |
| **Document Processing** | **PyPDF + LangChain Text Splitters** | Document extraction and `RecursiveCharacterTextSplitter` splitting on paragraph and sentence boundaries (~800 tokens / 3200 characters with 15% overlap) to maintain semantic coherence across chunk borders. |
| **LLM Inference** | **Google Gemini (`gemini-3.5-flash`) via `google-genai`** | Low-temperature (`0.0`), strictly grounded, low-latency streaming generation with anti-hallucination prompts. |
| **Authentication & Security** | **JWT (HS256) + Passlib (Argon2 / bcrypt)** | Stateless authentication with cryptographic password hashing. Every database query, vector search, and WebSocket connection is strictly scoped by `user_id`. |
| **Containerization** | **Docker & Docker Compose** | Reproducible multi-container stack (`postgres`, `backend`, `frontend`) with Nginx reverse proxy. |

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory (or in `backend/.env`) based on the provided `.env.example`.

> **Important**: Never commit `.env` or sensitive API keys to version control.

```env
# Database (Local PostgreSQL or Docker service)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/documind

# Security & JWT Authentication
JWT_SECRET=your_super_secret_jwt_key_minimum_32_characters_long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI & Embeddings
GEMINI_API_KEY=your_actual_google_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSION=384

# Document Upload Limits & Storage
MAX_FILE_SIZE_MB=25
UPLOAD_DIR=./uploads
```

### Environment Variables Reference

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | Async PostgreSQL connection string with `asyncpg` driver | `postgresql+asyncpg://postgres:postgres@localhost:5432/documind` |
| `JWT_SECRET` | Secret key used to sign and verify HMAC-SHA256 JWT tokens | Min. 32 characters random string |
| `JWT_ALGORITHM` | Algorithm for JWT tokens | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Lifetime of access tokens | `1440` (24 hours) |
| `GEMINI_API_KEY` | Google Gemini API Key from Google AI Studio | Required for LLM generation |
| `GEMINI_MODEL` | Target Gemini model identifier | `gemini-3.5-flash` |
| `EMBEDDING_MODEL` | FastEmbed local ONNX embedding model | `BAAI/bge-small-en-v1.5` |
| `EMBEDDING_DIMENSION` | Embedding vector dimensionality | `384` |
| `MAX_FILE_SIZE_MB` | Maximum allowed file upload size in MB | `25` |
| `UPLOAD_DIR` | Local disk upload directory | `./uploads` |

---

## 🚀 Setup & How to Run the Application

### Option A: Running with Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/Tejas-34/DocuMind.git
   cd DocuMind
   ```

2. Create your `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and insert your GEMINI_API_KEY
   ```

3. Build and launch all services:
   ```bash
   docker compose up --build
   ```

4. Access the services:
   - **Frontend UI**: [http://localhost](http://localhost) (or [http://localhost:5173](http://localhost:5173))
   - **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### Option B: Running Locally for Development

#### 1. Prerequisites
- **Python 3.10+** (Python 3.10 - 3.14 supported)
- **Node.js 18+ & npm**
- **PostgreSQL 16+ with `pgvector` extension**

#### 2. Database Setup
```sql
CREATE DATABASE documind;
\c documind;
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 3. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create backend .env file
cp ../.env.example .env
# Edit .env and configure your DATABASE_URL and GEMINI_API_KEY

# Run database migrations
alembic upgrade head

# Start FastAPI development server
uvicorn src.main:app --reload --port 8000
```

#### 4. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Running Automated Tests

Run backend unit and integration test suites:
```bash
cd backend
source .venv/bin/activate
pytest -v
```

The test suite covers:
- User registration, password hashing, and JWT token authentication.
- Multi-tenant data protection and route authorization.
- Document text splitting and chunking logic.
- Citation filtering, explicit source extraction, and negative response handling.
- End-to-end WebSocket chat communication flow.

---

## 🔒 Multi-Tenancy & Data Isolation Guarantee

1. **Relational Isolation**: Every core entity (`documents`, `chunks`, `chat_sessions`, `messages`) contains a non-nullable `user_id` foreign key referencing the `users` table with cascading deletes.
2. **Vector Query Scoping**: Vector similarity search strictly binds the authenticated `user_id`:
   ```sql
   SELECT c.id, c.document_id, d.filename AS document_name, c.page_number, c.content,
          (c.embedding <=> :query_vector) AS distance
   FROM chunks c
   JOIN documents d ON d.id = c.document_id
   WHERE c.user_id = :authenticated_user_id
     AND d.user_id = :authenticated_user_id
     AND d.status = 'ready'
   ORDER BY distance ASC
   LIMIT 5;
   ```
3. **Session & Document Ownership**: REST and WebSocket endpoints verify ownership at the database level; requests for unowned resource IDs immediately return `404 Not Found`.

---

## ⚠️ Assumptions & Known Limitations

### 1. Document Ingestion & File Parsing
- **No OCR Support**: The system uses `pypdf` for native text extraction. Scanned PDFs, photocopies, images, or flattened vector drawings without embedded text layers cannot be extracted and will result in an ingestion error.
- **File Format Constraints**: Ingestion is limited to `.pdf`, `.txt`, and `.md` files. Rich formats such as `.docx`, `.pptx`, `.xlsx`, or `.csv` are not currently supported.
- **Complex Layouts & Tables**: Text chunking strips table borders, multi-column newspaper layouts, mathematical formulas, and inline charts, which may reduce context quality for complex structured documents.
- **In-Memory File Buffering**: Uploaded files are buffered in memory during upload and passed directly to background tasks. Very large files under high concurrent load can cause memory spikes.

### 2. Retrieval-Augmented Generation (RAG)
- **Dense-Only Retrieval (No Hybrid / BM25)**: Retrieval is based purely on dense vector cosine similarity via `pgvector`. It does not combine sparse lexical search (BM25 / Full-Text Search). Rare exact keywords, product serial numbers, or acronyms may be missed if their vector cosine distance is high.
- **No Cross-Encoder Re-ranker**: Top-5 retrieved chunks are ordered purely by bi-encoder cosine similarity. There is no second-stage re-ranking model (e.g., `bge-reranker`) to re-score relevance against the exact query nuance.
- **Static Top-$K$ Retrieval ($K = 5$)**: The retrieval depth is fixed at 5 chunks. Complex, multi-page synthesis questions may miss necessary context, while simple factual questions may receive extra noise.
- **Tenant-Wide Scope Without Document Filtering**: Vector search automatically runs across all ready documents in the user's account. Users cannot currently scope their query to a single selected document or folder.

### 3. Background Processing & Infrastructure
- **In-Process Background Tasks (`FastAPI BackgroundTasks`)**: Document chunking and embedding generation run in FastAPI's internal task runner rather than a distributed message queue (e.g., Celery/Redis). If the server restarts or crashes during processing, in-flight jobs are interrupted and documents remain stuck in `processing`.
- **CPU-Bound Embedding Load**: FastEmbed runs ONNX models on the backend CPU. High volumes of concurrent document uploads can consume significant CPU resources.
- **Binary Status Tracking**: Ingestion status transitions directly between `processing`, `ready`, and `failed` without granular percentage progress (e.g., "Chunking: 40%").

### 4. Conversational Memory & Context
- **Fixed History Truncation (Recent 4–6 Messages)**: Only the most recent messages are injected into prompt context. Long multi-turn conversations lose earlier discussion points.
- **No Query Rewriting / HyDE**: Conversational follow-ups containing ambiguous pronouns (e.g., *"What were his main achievements there?"*) are embedded directly into vector search without contextual co-reference resolution.

### 5. LLM & External AI Dependencies
- **External API Rate Limits**: Generation relies on Google Gemini API availability and rate limits (e.g., Free Tier daily request quotas).
- **Strict Anti-Hallucination Grounding**: The system prompt strictly enforces that missing facts must yield *"I cannot find this information in your uploaded documents."* While preventing hallucinations, it may occasionally reject answers that require cross-sentence inference across distant sections.

### 6. Security & Production Scaling
- **Stateless JWT Tokens**: Tokens are stateless with a 24-hour expiration. There is no distributed token blacklist (e.g., Redis-backed) for instantaneous token revocation before expiration.
- **No API Rate Limiting**: REST and WebSocket endpoints currently lack per-IP or per-user rate limiters.
- **Local Disk Storage**: Uploaded files and local SQLite/PostgreSQL instances require S3-compatible cloud object storage integration (e.g., AWS S3, MinIO) for multi-server horizontal scaling.
