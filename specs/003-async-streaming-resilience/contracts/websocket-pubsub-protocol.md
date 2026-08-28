# Phase 1: WebSocket Pub/Sub Frame Contracts

**Feature**: Asynchronous Background Streaming & Resilient Reconnection (`003-async-streaming-resilience`)
**Date**: 2026-08-28

---

## 1. Client → Server Frame Types

### `query` (Submit new question)
```json
{
  "type": "query",
  "text": "What does the employee handbook state regarding sick leaves?",
  "client_msg_id": "opt-1740733800000"
}
```

### `cancel` (Cancel active background task)
```json
{
  "type": "cancel"
}
```

### `ping` (Heartbeat keepalive)
```json
{
  "type": "ping"
}
```

---

## 2. Server → Client Frame Types

### `connected` (Initial handshake ack with active state)
```json
{
  "type": "connected",
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "is_generating": true
}
```

### `catch_up` (Buffer sent upon reconnect during in-flight generation)
```json
{
  "type": "catch_up",
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "content": "According to page 4 of the employee handbook...",
  "status": "generating"
}
```

### `status` (Pipeline progression update)
```json
{
  "type": "status",
  "step": "searching_documents",
  "message": "Searching your uploaded documents..."
}
```

### `token` (Real-time token delta)
```json
{
  "type": "token",
  "content": " sick leave"
}
```

### `done` (Finalized completion payload)
```json
{
  "type": "done",
  "client_msg_id": "opt-1740733800000",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "assistant",
  "content": "According to page 4 of the employee handbook, sick leave requires a medical note if exceeding 3 days.",
  "citations": [
    {
      "document_id": "2fa85f64-5717-4562-b3fc-2c963f66afa6",
      "document_name": "Employee_Handbook_2026.pdf",
      "page_number": 4,
      "snippet": "Sick leave requires a medical certificate if consecutive absence exceeds 3 days..."
    }
  ]
}
```
