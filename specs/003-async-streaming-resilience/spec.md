# Feature Specification: Asynchronous Background Streaming & Resilient Reconnection

**Feature Branch**: `003-async-streaming-resilience`

**Created**: 2026-08-28

**Status**: Draft

**Input**: User description: "Backend Asynchronous Decoupling: When a prompt is received, FastAPI will trigger a background task (asyncio.create_task) to handle the LLM generation. This task will write tokens to a database or cache, regardless of the client's connection state. WebSocket Connection Manager: The ws/chat/stream/{sessionId} endpoint will act purely as a pub/sub consumer. If connected, it pushes tokens to the client. If the client disconnects and reconnects, the server fetches the missed tokens from the database and streams the remainder. Offline State Detection: Utilize the browser's native navigator.onLine API coupled with global event listeners in your component-based frontend to trigger a persistent 'You are disconnected' toast or banner. Optimistic UI & Reconnection: The chat component will instantly append the user's prompt to the local message array. A custom WebSocket hook will implement exponential backoff for reconnections, re-syncing the local message state with the /chat/stream/{sessionid} HTTP endpoint upon successful reconnection. Performant Rendering: Implement token chunking and requestAnimationFrame (or React's startTransition) to prevent layout thrashing and ensure smooth auto-scrolling during rapid token injection."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Decoupled Background LLM Generation (Priority: P1)

As a user asking a complex question about large documents, I want the AI generation task to continue running on the server even if my browser is closed or my laptop goes to sleep, so that the answer is completely generated and safely saved to my conversation history without data loss.

**Why this priority**: Eliminates generation cancellation caused by network blips or tab navigation, ensuring reliable query execution.

**Independent Test**: Send a query, immediately close the browser window or disconnect the socket, wait 10 seconds, reopen the chat thread, and verify the full grounded response is persisted and displayed.

**Acceptance Scenarios**:
1. **Given** an authenticated user sending a question over WebSocket, **When** FastAPI receives the query frame, **Then** an asynchronous background task (`asyncio.create_task`) is spawned to handle document retrieval and LLM streaming independently of the socket lifecycle.
2. **Given** an active background generation task, **When** the client WebSocket closes or terminates prematurely, **Then** the background worker continues executing until the entire response and citations are committed to PostgreSQL.

---

### User Story 2 - Resilient Pub/Sub Reconnection & Catch-Up (Priority: P1)

As a user with intermittent network connectivity, I want my chat stream to automatically reconnect with exponential backoff and resume streaming any missed tokens seamlessly so that I never miss part of an answer.

**Why this priority**: Users on mobile or fluctuating networks must experience seamless continuation rather than broken or stuck message states.

**Independent Test**: During an active response stream, drop the network connection in DevTools for 3 seconds, re-enable it, and verify the client reconnects, retrieves missed tokens, and finishes streaming smoothly.

**Acceptance Scenarios**:
1. **Given** a client disconnecting during an in-flight stream, **When** the client reconnects to the WebSocket endpoint, **Then** the server recognizes the in-progress generation, pushes the accumulated tokens buffer, and continues streaming live tokens.
2. **Given** a completed generation while the client was disconnected, **When** the client reconnects or syncs with the session endpoint, **Then** the finalized assistant message and citations are populated without duplication.

---

### User Story 3 - Offline State Detection & Reconnection Banner (Priority: P2)

As an active user in the application, I want to see an immediate, clear connectivity banner when my device goes offline and when it is reconnecting, so that I understand system state before submitting new queries.

**Why this priority**: Transparent network status prevents user confusion and avoids submitting failed requests when disconnected.

**Independent Test**: Toggle the browser to Offline in DevTools, verify the floating offline banner appears instantly, restore connection, and verify the banner disappears upon successful reconnection.

**Acceptance Scenarios**:
1. **Given** any active page in the application, **When** the device network status changes to offline (`navigator.onLine === false`), **Then** a floating "You are currently offline" warning banner is displayed.
2. **Given** an offline device, **When** network connectivity is restored, **Then** the banner transitions to "Reconnected" and auto-dismisses after sync.

---

### User Story 4 - High-Performance Token Chunking & Smooth Auto-Scrolling (Priority: P2)

As a user reading a rapid streaming response, I want the text to render smoothly at 60fps without layout thrashing, jitter, or jerky scroll jumping so that reading is effortless and comfortable.

**Why this priority**: High-speed token arrival can cause excessive Vue reactivity recalculations and DOM reflows; batching frames via `requestAnimationFrame` ensures smooth visual performance.

**Independent Test**: Stream a long, dense 1000-word response and inspect DevTools performance profile to confirm 60fps rendering with zero scroll thrashing.

**Acceptance Scenarios**:
1. **Given** rapid incoming token frames from the WebSocket, **When** appending content to the UI, **Then** micro-tokens are batched per display frame using `requestAnimationFrame`.
2. **Given** a user reading a stream, **When** the user manually scrolls up, **Then** automatic bottom scrolling pauses until the user scrolls back to the bottom.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: FastAPI MUST spawn generation as an in-process background worker task (`asyncio.create_task`), completely detached from the client WebSocket handler coroutine.
- **FR-002**: An in-memory `SessionBroadcastManager` MUST maintain active subscriber queues for connected WebSocket sessions, broadcasting tokens and status frames.
- **FR-003**: The WebSocket endpoint MUST act as a pub/sub subscriber, listening to the session's broadcast channel and forwarding frames to the client.
- **FR-004**: If a client disconnects mid-stream, the background worker MUST continue streaming tokens from the LLM, assembling the complete response, and writing the final `Message` record with citations to PostgreSQL.
- **FR-005**: When a client reconnects to an active session with an in-progress generation, the server MUST deliver the accumulated token buffer and stream subsequent tokens in real time.
- **FR-006**: A session sync REST endpoint (`GET /api/v1/chat/sessions/{session_id}/sync`) MUST provide the current active generation status (`idle` | `generating`), accumulated buffer, and latest message ID.
- **FR-007**: Frontend `useChatWebSocket` composable MUST implement exponential backoff reconnection with jitter (1s, 2s, 4s, 8s, up to 30s) when the connection drops unexpectedly.
- **FR-008**: Frontend MUST provide a reactive `useNetworkStatus` composable monitoring `navigator.onLine` and `online`/`offline` window events.
- **FR-009**: When offline, the chat interface MUST display a floating non-intrusive warning banner informing the user of the disconnected state.
- **FR-010**: Chat input MUST optimistically append the user message to the local store and display an animated pending indicator until acknowledged.
- **FR-011**: Rapid token streams MUST be batched using `requestAnimationFrame` before updating Vue reactive markdown content to prevent DOM layout thrashing.
- **FR-012**: Auto-scroll logic in `useAutoScroll` MUST detect user-initiated upward scroll and pause auto-scrolling until user returns to the scroll threshold.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of LLM generation tasks complete and persist to PostgreSQL even if the client disconnects immediately after sending the prompt.
- **SC-002**: Reconnecting clients successfully resume streaming in-progress answers within <500ms of socket re-establishment.
- **SC-003**: Zero lost messages or duplicate responses across 50 consecutive disconnect/reconnect cycles.
- **SC-004**: Frontend rendering maintains 60fps during rapid LLM token emission with zero perceptible layout jitter.
- **SC-005**: Offline network state triggers visual warning within <100ms of browser `offline` event.

## Assumptions

- **Single-Node In-Memory Pub/Sub**: The application currently runs as a single-node container deployment; an in-memory queue manager provides optimal speed and zero infrastructure overhead compared to Redis.
- **PostgreSQL as Source of Truth**: Completed messages and citations are durably stored in PostgreSQL and indexed by `session_id` and `created_at`.
- **Browser Capabilities**: Target browsers support standard WebSocket, `navigator.onLine`, and `requestAnimationFrame` APIs.
