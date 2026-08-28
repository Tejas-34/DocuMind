# Phase 0: Research & Technical Decisions

**Feature**: Asynchronous Background Streaming & Resilient Reconnection (`003-async-streaming-resilience`)
**Date**: 2026-08-28

---

## 1. Background Task Decoupling & In-Memory Pub/Sub vs. Redis

### Decision
Implement an in-memory `SessionBroadcastManager` using Python's `asyncio.Queue` and `asyncio.create_task` combined with PostgreSQL `Message` table persistence.

### Rationale
- Current DocuMind architecture runs as a unified backend service backed by PostgreSQL/pgvector.
- An in-memory queue manager provides microsecond-latency token broadcasting to active WebSocket subscribers without the operational overhead of running and maintaining an external Redis broker container.
- Background worker tasks spawned via `asyncio.create_task` continue running even when the WebSocket client closes or disconnects, persisting the completed assistant response to PostgreSQL.
- If DocuMind is horizontally scaled across multiple backend nodes in the future, the `SessionBroadcastManager` interface can be cleanly swapped for a Redis Pub/Sub backend without modifying application services, frontend contracts, or database schemas.

### Alternatives Considered
- *Direct WebSocket Streaming Loop (Status Quo)*: Rejected because if the client socket drops, the stream dies and generated tokens are lost.
- *External Redis Pub/Sub*: Deferred as premature optimization for single-node deployment, adding unnecessary infrastructure dependency.

---

## 2. Reconnection & Catch-Up Protocol

### Decision
- When a client sends a `query` frame, `SessionBroadcastManager` creates an active session state tracking:
  - `accumulated_tokens`: string list of tokens emitted so far.
  - `status`: current pipeline step (`searching_documents`, `generating`, `completed`, `error`).
  - `subscribers`: set of active `asyncio.Queue` channels for connected WebSocket clients.
  - `background_task`: reference to the running `asyncio.Task`.
- When a client connects/reconnects to `/ws/chat/{session_id}`:
  - If a generation is currently active for that `session_id`, the server immediately pushes a `catch_up` frame containing all accumulated tokens, followed by live streaming frames as they are generated.
  - A REST sync endpoint `GET /api/v1/chat/sessions/{session_id}/sync` provides fallback synchronization when HTTP polling or page reloading occurs.

### Rationale
Guarantees zero token loss during network drops and provides an instantaneous, flicker-free recovery experience.

---

## 3. Frontend Offline State Detection & Reconnection Strategy

### Decision
- Create `useNetworkStatus` composable observing `navigator.onLine` and `window.addEventListener('online'/'offline')`.
- In `useChatWebSocket.ts`, implement exponential backoff with randomized jitter:
  - Initial delay: 1,000ms
  - Multiplier: 2x (1s, 2s, 4s, 8s, up to 30s max)
  - Jitter: ±20% randomized spread to prevent thundering herd
  - Immediate reconnection triggered upon browser `online` event.
- Display a sleek floating banner at the top of the chat area when disconnected, transitioning to "Reconnecting..." and "Reconnected".

### Rationale
Provides clear transparency to the user and avoids stuck spinners or silent failures.

---

## 4. Performant Token Rendering & Auto-Scrolling

### Decision
- In `ChatWindow.vue`, buffer rapid micro-tokens and flush updates inside a `requestAnimationFrame` loop.
- In `useAutoScroll.ts`, add user-scroll detection:
  - When user scrolls up past a 50px threshold from the bottom, pause auto-scrolling so the user can read earlier text comfortably.
  - When user scrolls back near the bottom, resume auto-scrolling.

### Rationale
Eliminates DOM layout thrashing and scroll fighting during fast 50+ token/sec streaming.
