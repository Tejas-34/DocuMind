# DocuMind Asynchronous Ingestion Engine Workflow

This document provides a comprehensive, step-by-step breakdown of how DocuMind's asynchronous ingestion engine processes document uploads across the frontend, FastAPI backend, AsyncIO event loop, thread pool, and PostgreSQL database.

---

## ⚡ 1. Asynchronous Ingestion Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Vue 3 Browser)
    participant API as FastAPI REST Router (/documents)
    participant DB as PostgreSQL (documents table)
    participant EventLoop as Python AsyncIO Event Loop
    participant ThreadPool as ThreadPoolExecutor (Worker Thread)
    participant VectorDB as PostgreSQL (chunks table + pgvector)

    %% Step 1: Immediate Non-blocking upload
    User->>API: POST /api/v1/documents (multipart file)
    Note over API: 1. Validate MIME & size (25MB limit)<br/>2. Create doc row with status='processing'
    API->>DB: INSERT INTO documents (status='processing', user_id, ...)
    API->>EventLoop: background_tasks.add_task(process_document_background)
    API-->>User: ⚡ HTTP 202 Accepted (Returns immediately within ~30ms!)

    %% Step 2: Background processing starts after response
    Note over EventLoop: HTTP request is closed.<br/>Event Loop picks up the queued task.
    EventLoop->>EventLoop: DocumentService.process_document_background()
    EventLoop->>EventLoop: Open isolated AsyncSessionLocal()
    EventLoop->>EventLoop: PyPDF extract text + LangChain Recursive Splitter (~800 tok chunks)

    %% Step 3: CPU Offloading to ThreadPool
    Note over EventLoop,ThreadPool: CPU-heavy ONNX embedding inference offloaded to background thread
    EventLoop->>ThreadPool: loop.run_in_executor(None, _sync_embed_documents, texts)
    Note over ThreadPool: FastEmbed (BAAI/bge-small-en-v1.5)<br/>Generates 384-d vectors in batch of 32
    ThreadPool-->>EventLoop: Returns 384-d vector embeddings array

    %% Step 4: Batch Vector Storage & Status Transition
    EventLoop->>VectorDB: INSERT INTO chunks (user_id, document_id, embedding, content, page_num)
    EventLoop->>DB: UPDATE documents SET status='ready', total_pages=N WHERE id=doc_id
    Note over DB: State transitions from 'processing' to 'ready'

    %% Step 5: Frontend polling picks up the change
    loop Every 3 seconds (Short Polling)
        User->>API: GET /api/v1/documents
        API-->>User: Returns doc list with status='ready'
        Note over User: Pinia store sees all docs 'ready' -> stops polling interval
    end
```

---

## 📐 2. Architectural & Data Flow Diagram

```mermaid
flowchart TD
    subgraph Frontend ["🖥️ Vue 3 Frontend"]
        direction TB
        F_Upload["1. POST /api/v1/documents<br/>(Multipart File Upload)"]
        F_Opt["5. Instant HTTP 202 Accepted<br/>(Render 'Processing' Spinner)"]
        F_Poll["14. Smart Short Polling (Every 3s)<br/>GET /api/v1/documents"]
        F_Done["18. Status 'Ready' Received<br/>(Display Green Badge & stopPolling)"]
    end

    subgraph Backend ["⚡ FastAPI Application"]
        direction TB
        B_Val["2. Validate MIME & Size (25MB)"]
        B_Insert["3. INSERT doc (status='processing')"]
        B_BG["4. background_tasks.add_task()<br/>(Dispatch & Close Connection)"]
        B_PollRoute["15. Poll Router<br/>Reads DB Status"]
    end

    subgraph EventLoop ["🔄 AsyncIO Event Loop"]
        direction TB
        L_Task["6. Execute process_document_background()"]
        L_Session["7. Open Dedicated AsyncSessionLocal()"]
        L_Extract["8. PyPDF Text Extraction"]
        L_Chunk["9. LangChain Recursive Splitter<br/>(~800 tok, 15% overlap)"]
    end

    subgraph ThreadPool ["🧵 ThreadPoolExecutor (Worker Thread)"]
        direction TB
        T_Offload["10. loop.run_in_executor()"]
        T_ONNX["11. FastEmbed ONNX Model<br/>(BAAI/bge-small-en-v1.5, 384-d)"]
    end

    subgraph Database ["🗄️ PostgreSQL Database"]
        direction TB
        D_Doc[("documents table<br/>status: processing to ready")]
        D_Chunk[("chunks table<br/>pgvector HNSW index (384-d)")]
    end

    %% Ingestion Flow
    F_Upload --> B_Val
    B_Val --> B_Insert
    B_Insert --> D_Doc
    B_Insert --> B_BG
    B_BG --> F_Opt
    B_BG --> L_Task
    
    L_Task --> L_Session
    L_Session --> L_Extract
    L_Extract --> L_Chunk
    L_Chunk --> T_Offload
    T_Offload --> T_ONNX
    T_ONNX -->|12. Return Vector Embeddings| L_Task
    
    L_Task -->|13. INSERT chunks with embeddings| D_Chunk
    L_Task -->|13. UPDATE status='ready'| D_Doc
    
    %% Polling Flow
    F_Opt -.-> F_Poll
    F_Poll --> B_PollRoute
    B_PollRoute -->|Read Status| D_Doc
    D_Doc -->|Status 'ready'| B_PollRoute
    B_PollRoute --> F_Done
```

---

## 🔬 3. Deep Dive: 5 Critical Asynchronous Mechanisms

### 1. Immediate HTTP 202 Accepted & BackgroundTasks
When the user submits a file, the REST router in FastAPI does not process the document inline. Instead:
* It creates an initial row in the `documents` table marked as `status = "processing"`.
* It queues the ingestion job with `background_tasks.add_task(...)`.
* It returns an **HTTP 202 ACCEPTED** status code to the client in ~30ms, closing the client connection quickly.

```python
# backend/src/api/v1/documents.py (Lines 59-69)
background_tasks.add_task(
    DocumentService.process_document_background,
    document_id=doc.id,
    user_id=current_user.id,
    file_bytes=file_bytes,
    filename=filename,
    mime_type=mime_type
)

return doc  # Returns immediately to browser!
```

### 2. Isolated Database Session Lifecycle
Because the original HTTP request finishes and closes its request-scoped DB session, the background task cannot reuse the request's connection. It instantiates an independent session context:

```python
# backend/src/services/document_service.py (Lines 79-80)
@classmethod
async def process_document_background(cls, document_id, user_id, file_bytes, filename, mime_type):
    async with AsyncSessionLocal() as session:  # Fresh, dedicated async DB session
        ...
```

### 3. Non-Blocking CPU Offloading (`run_in_executor`)
Computing vector embeddings using ONNX/neural network models (`FastEmbed`) is a CPU-bound, synchronous operation. If executed directly inside an `async def` function on Python's main event loop, it would block the entire server—preventing FastAPI from serving other users or streaming WebSocket tokens.

The system solves this by offloading embedding inference to a separate worker thread using `loop.run_in_executor`:

```python
# backend/src/services/embedding_service.py (Lines 43-46)
async def embed_documents(self, texts: List[str]) -> List[List[float]]:
    loop = asyncio.get_running_loop()
    # Runs the synchronous ONNX batch inference in a background thread pool!
    return await loop.run_in_executor(None, self._sync_embed_documents, texts)
```
> **Why this matters:** The main asyncio event loop remains 100% free to handle WebSocket chats and API requests while the embedding calculation runs in parallel.

### 4. Background Parsing & Vector Index Ingestion
Inside the worker execution lifecycle:
1. **Extraction:** `PyPDF` extracts text per page (preserving page numbers for citations).
2. **Chunking:** Slices text into ~800 token fragments with a 15% overlap using a recursive strategy.
3. **Batch Vector Insert:** Embeddings and chunk metadata are inserted into the `chunks` table (indexed with pgvector HNSW).
4. **State Transition:** The document status is updated to `ready` (if successful) or `failed` (if an exception occurs).

### 5. Frontend State Synchronization (Smart Short Polling)
On the browser side, the frontend synchronizes the UI without needing heavy persistent connections for simple document uploads:
1. As soon as the upload returns with status `"processing"`, the UI displays a processing spinner.
2. `checkAndStartPolling()` initiates a 3-second interval timer (`setInterval(..., 3000)`).
3. Every 3 seconds, `documentService.listDocuments()` polls the server.
4. As soon as the background task completes and updates the database row to `"ready"`, the frontend receives `"ready"`, displays the green badge, and calls `stopPolling()` to terminate the timer.

---

## 🎯 4. Summary of Benefits

| Aspect | Synchronous Approach (Naive) | DocuMind Asynchronous Approach |
| :--- | :--- | :--- |
| **HTTP Response Time** | 5 – 20 seconds (user waits) | **< 30 milliseconds** |
| **Server Concurrency** | Blocks event loop during ONNX math | **Non-blocking** via `run_in_executor` thread pool |
| **User Experience** | Frozen UI / spinning page | **Instant optimistic update** + live status badge |
| **Failure Isolation** | Failed parsing crashes HTTP request | **Handled gracefully** in background with DB error status |
