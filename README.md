# DocuMind: Multi-Tenant AI Document Assistant

DocuMind is an enterprise-grade, privacy-first, multi-tenant Document Q&A web application. It enables users to securely create an account, upload documents (`.pdf`, `.txt`, `.md`), and query their private knowledge base via real-time WebSocket token streaming with strict document grounding and verifiable citations.

## Setup & How to Run the Application

### Option A: Running with Docker Compose
1. Prerequisites - ``` Docker```

2. Clone the repository:
   ```bash
   git clone https://github.com/Tejas-34/DocuMind.git
   cd DocuMind
   ```

3. Create your `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and insert your GEMINI_API_KEY
   ```

4. Build and launch all services:
   ```bash
   docker compose up --build
   ```

5. Access the services:
   - Frontend UI: [http://localhost](http://localhost) (or [http://localhost:5173](http://localhost:5173))
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)


### Option B: Running Locally for Development

1. Prerequisites
   ```
   - Python 3.10+
   - Node.js 18+ & npm
   - PostgreSQL 16+ with `pgvector` extension
   ```

2. Database Setup
   ```sql
   CREATE DATABASE documind;
   \c documind;
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. Backend Setup
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

4. Frontend Setup
   ```bash
   cd frontend

   # Install Node dependencies
   npm install

   # Start Vite development server
   npm run dev
   ```
Open [http://localhost:5173](http://localhost:5173) in your browser.

## Environment Variables

The required environment variables are documented in the `.env.example` file located in the project root.

[`.env.example`](./.env.example)


## Technology Choices
### Frontend : Vue 3 + TypeScript
I chose Vue because it is simple to work with and makes it easy to build a reactive UI. I used TypeScript to make the code safer and easier to maintain.
### Backend: FastAPI 
I chose FastAPI because it works well with Python and supports asynchronous APIs. It also has good support for WebSockets, which I use for streaming chat responses.
### Database: PostgreSQL 16 + pgvector
I chose PostgreSQL because I need a database for users, documents, chats, and messages. I use pgvector in the same database to store and search document embeddings, so I don't need a separate vector database.
### Embeddings: FastEmbed + BAAI/bge-small-en-v1.5
FastEmbed to generate embeddings locally. I chose BGE because it gives semantic embeddings that work well for finding relevant document chunks without using an external embedding API.
### Chunks : PyPDF + LangChain Text Splitters
Used PyPDF to extract text from uploaded PDFs. Then I split the text into smaller chunks using the Recursive Character Text Splitter so that I can search smaller and more relevant parts of the documents.
### LLM: Google Gemini + google-genai
**Model:** `gemini-3.5-flash`

Gemini to generate the final answer from the document chunks retrieved by the RAG system. I keep the temperature at 0 so the answers are more consistent. The response is streamed back to the frontend.
### State Management: Pinia

Used Pinia to manage the state shared across different parts of the frontend, mainly authentication, documents, and chat.
### Styling and Icons: Tailwind CSS + Lucide Icons
I chose Tailwind because it makes styling the UI quick and simple. Lucide provides the icons used in the application.
### Authentication and Security: JWT + Password Hashing
**Technologies:** - JWT with HS256 

JWT for user authentication and password hashing for storing passwords securely. I also use `user_id` when accessing documents, chunks, and chats so that one user cannot access another user's data.


# RAG Flow
The basic flow of the project is:
1.  User uploads a document.
2.  The backend extracts the text using PyPDF.
3.  The text is split into chunks using Recursive Character Text Splitter.
4.  Each chunk is converted into a 384-dimensional embedding using
    FastEmbed.
5.  The chunks and embeddings are stored in PostgreSQL with pgvector.
6.  When the user asks a question, the question is also converted into
    an embedding.
7.  pgvector searches the user's document chunks using cosine
    similarity.
8.  The top 5 relevant chunks are selected.
9.  These chunks are added to the prompt.
10. Gemini generates the answer using only the retrieved document
    context.
11. The answer is streamed back to the frontend through WebSocket.


## Development Prompts

The major prompts used during the development of DocuMind are documented here:

- [PROMPTS.md](PROMPTS.md) — Major prompts and the spec-driven development workflow used for the project.


## Assumptions & Known Limitations

### 1. Document Ingestion & File Parsing
- **No OCR Support**: The system can only extract text from PDFs that contain selectable text. Scanned documents, photocopies, images, and PDFs without a text layer cannot be read and will cause an ingestion error.
- **File Format Constraints**: Ingestion is limited to `.pdf`, `.txt`, and `.md` files.
- **In-Memory File Buffering**: Uploaded files are buffered in memory during upload and passed directly to background tasks. Very large files under high concurrent load can cause memory spikes. **File Limit 25MB Max.**

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





## API Endpoints

The backend provides REST APIs for authentication, document management, and chat sessions.  
It also uses a WebSocket for real-time AI response streaming.

### Health Check

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/health` | Check if the API is running | Public |

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Create a new user account | Public |
| POST | `/api/v1/auth/login` | Login and get JWT token | Public |
| GET | `/api/v1/auth/me` | Get current user information | JWT |

### Documents

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/documents` | Upload a document and start processing | JWT |
| GET | `/api/v1/documents` | Get all documents of the current user | JWT |
| GET | `/api/v1/documents/{document_id}` | Get details of a document | JWT |
| DELETE | `/api/v1/documents/{document_id}` | Delete a document and its chunks | JWT |

Supported document types:

- PDF
- TXT
- Markdown

Maximum file size: **25 MB**

When a document is uploaded, it is first marked as `processing`. The backend then extracts the text, creates chunks, generates embeddings, and changes the status to `ready`.

### Chat Sessions

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/chat/sessions` | Create a new chat session | JWT |
| GET | `/api/v1/chat/sessions` | List user's chat sessions | JWT |
| GET | `/api/v1/chat/sessions/{session_id}` | Get session and message history | JWT |
| PATCH | `/api/v1/chat/sessions/{session_id}` | Rename a chat session | JWT |
| DELETE | `/api/v1/chat/sessions/{session_id}` | Delete a chat session and messages | JWT |

### Chat WebSocket

The chat uses WebSocket for real-time communication and streaming AI responses.

```text
WS /api/v1/ws/chat/{session_id}?token={JWT_ACCESS_TOKEN}