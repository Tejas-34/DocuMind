# WebSocket Protocol Specification: Real-Time Chat & RAG Streaming

**Feature**: [spec.md](../spec.md) | **Date**: 2026-08-27

---

## 1. Connection Endpoint & Handshake

### URL
`ws://<host>:<port>/api/v1/ws/chat/{session_id}?token=<JWT_ACCESS_TOKEN>`

### Connection Lifecycle & Security Gate:
1. Client establishes WebSocket connection passing JWT token in `token` query param.
2. Server validates JWT HMAC-SHA256 signature and extracts `user_id`.
3. Server queries `chat_sessions` to verify that `id == session_id AND user_id == jwt_user_id`.
4. If authentication fails or tenant mismatch occurs, the server immediately closes the connection with code `4401` (`Unauthorized`) or `4403` (`Forbidden`).
5. Upon successful handshake, server sends an `authenticated` message frame (`connected`).

---

## 2. Message Frames (JSON)

### A. Client-to-Server Frames

#### 1. Submit Question (`query`)
```json
{
  "type": "query",
  "client_msg_id": "opt-1724778100-abc",
  "text": "What does the contract say about termination?"
}
```

#### 2. Clear Context (`clear_context`)
Resets active memory context for the session without deleting historical message records:
```json
{
  "type": "clear_context"
}
```

#### 3. Cancel Active Stream (`cancel`)
```json
{
  "type": "cancel"
}
```

#### 4. Heartbeat / Ping (`ping`)
```json
{
  "type": "ping"
}
```

---

### B. Server-to-Client Frames

#### 1. Authenticated Confirmation (`connected`)
Sent immediately after handshake:
```json
{
  "type": "connected",
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
}
```

#### 2. Query Status Notification (`status`)
Sent during query retrieval & processing:
```json
{
  "type": "status",
  "step": "searching_documents",
  "message": "Searching your uploaded documents..."
}
```

#### 3. Real-Time Token Chunk (`token`)
Sent continuously as tokens stream from Gemini async client:
```json
{
  "type": "token",
  "content": "According "
}
```

#### 4. Stream Completed & Attribution (`done`)
Sent when response generation concludes. Includes message ID, client message correlation ID, and grounded source citations:
```json
{
  "type": "done",
  "client_msg_id": "opt-1724778100-abc",
  "message_id": "e3b0c442-98fc-1c14-9af0-2d8544a49c95",
  "role": "assistant",
  "content": "According to Section 9.2 of the contract, either party may terminate the agreement with 30 days written notice.",
  "citations": [
    {
      "document_id": "8f03c025-a13f-4e08-8f5b-11758ce60172",
      "document_name": "Consulting_Agreement_2026.pdf",
      "page_number": 4,
      "snippet": "Section 9.2: The contract may be terminated by either party with 30 days written notice..."
    }
  ]
}
```

#### 5. Context Cleared Confirmation (`context_cleared`)
```json
{
  "type": "context_cleared",
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "message": "Session context reset successfully."
}
```

#### 6. Error Frame (`error`)
Sent when an error occurs during processing:
```json
{
  "type": "error",
  "code": "NO_DOCUMENTS_FOUND",
  "message": "No processed documents found in your account. Please upload documents first."
}
```

#### 7. Heartbeat Response (`pong`)
```json
{
  "type": "pong"
}
```

---

## 3. Client Resilience & Auto-Reconnect Lifecycle

```text
[Connected] ──(Network Drop)──> [Reconnecting: Backoff 1s, 2s, 4s, 8s]
      │                                    │
      │                                (Handshake)
      ▼                                    ▼
[Send Query] <────────────────── [Re-authenticate & Restore Session]
```

1. When a WebSocket disconnect occurs unexpectedly, `useChatWebSocket` enters reconnect mode with exponential backoff (1s, 2s, 4s, 8s, up to 30s with random jitter).
2. Upon re-establishing the socket connection, the client sends authentication and validates the session.
3. If a response stream was interrupted mid-flight, the client renders an inline retry button allowing the user to seamlessly re-dispatch the pending query.
