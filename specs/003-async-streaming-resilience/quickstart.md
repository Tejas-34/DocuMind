# Quickstart & Verification Guide: Asynchronous Background Streaming

**Feature**: `003-async-streaming-resilience`
**Date**: 2026-08-28

---

## 1. Automated Validation
```bash
# Run backend test suite
cd backend
pytest tests/ -v

# Run frontend build check
cd frontend
npm run build
```

---

## 2. End-to-End Resilience Scenarios

### Scenario A: Background Generation with Closed Tab
1. Open DocuMind and navigate to `/chat`.
2. Ask a detailed multi-paragraph question (e.g. "Summarize the key points of all uploaded files in detail").
3. As soon as generation starts ("Streaming answer..."), close the browser tab or navigate away.
4. Wait 10 seconds.
5. Reopen the browser tab to `/chat`.
6. **Expected Outcome**: The full completed response is stored in PostgreSQL and rendered in the message thread with citations.

### Scenario B: Drop and Reconnect Mid-Stream
1. Ask a question in chat.
2. In Chrome DevTools > Network tab, switch throttling preset to "Offline" for 3 seconds.
3. Observe the floating "You are disconnected" warning banner.
4. Switch throttling back to "Online".
5. **Expected Outcome**: The WebSocket automatically reconnects, receives the `catch_up` token buffer, clears the banner, and completes the stream without losing a single token.

### Scenario C: High-Speed Token Batching & Scroll Lock
1. Ask a question resulting in a long response.
2. While streaming, scroll up to inspect previous messages.
3. **Expected Outcome**: The auto-scroll locks in place, allowing comfortable reading without snapping back down until the user scrolls back to the bottom.
