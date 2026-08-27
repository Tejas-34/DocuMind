# Quickstart & Verification Guide: Multi-Tenant Document Q&A Platform

**Feature**: [spec.md](./spec.md) | **Date**: 2026-08-27

---

## 1. Environment & Prerequisites

### Required Software
- **Python**: 3.11+
- **Node.js**: 20+ (with `npm` or `pnpm`)
- **PostgreSQL**: 16+ with `pgvector` extension enabled (`CREATE EXTENSION IF NOT EXISTS vector;`)
- **Google Gemini API Key**: `GEMINI_API_KEY` set in environment

### Environment Variables (`backend/.env`)
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/documind
JWT_SECRET=supersecret_dev_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## 2. Setup & Installation

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 3. End-to-End & Detailed UI Verification Scenarios

### Scenario 1: Navigation Guard & Route Protection
1. **Action**: In an incognito window without logging in, directly navigate to `http://localhost:5173/documents` or `http://localhost:5173/chat`.
2. **Expected Outcome**:
   - Router navigation guard intercepts the attempt.
   - User is redirected to `/login?redirect=%2Fdocuments`.
   - After logging in with valid credentials, user is redirected back to `/documents`.

### Scenario 2: Drag-and-Drop Ingestion & Document Grid/List View
1. **Action**: Navigate to `/documents`. Drag a PDF file (e.g. `Handbook.pdf`) directly onto the drag-and-drop upload zone.
2. **Expected Outcome**:
   - Dropzone displays active hover state.
   - File appears in Document Grid / List showing:
     - Document Name (`Handbook.pdf`)
     - Upload Date (e.g., `Aug 27, 2026, 10:30 PM`)
     - Document UUID (e.g., `8f03c025-a13f-4e08-8f5b-11758ce60172`) with a click-to-copy button
     - Status Badge (`Uploading` → `Processing` → `Ready`)
     - Delete action button (with confirmation modal) and View details action.

### Scenario 3: Chat Sidebar, Clear Context & Thread Switching
1. **Action**: Navigate to `/chat`. Create two distinct sessions: "Contract Review" and "Policy Q&A".
2. **Expected Outcome**:
   - Both sessions appear in the sidebar with intuitive titles.
   - Clicking a thread switches the active conversation and restores message history without full-page reload.
   - Clicking "Clear Current Context" resets the session context memory with a visual notification.

### Scenario 4: Optimistic Messages & Smooth Auto-Scrolling (No Layout Shift)
1. **Action**: In an active chat session, submit a question.
2. **Expected Outcome**:
   - User message bubble renders instantly (optimistic UI update).
   - Real-time token streaming begins with a subtle typing indicator.
   - Chat window smoothly auto-scrolls down as tokens stream in.
   - If the user scrolls up during streaming to inspect previous text, auto-scrolling automatically pauses to avoid layout shifts.
   - Answer completes with citation badge referencing document name and page number.

### Scenario 5: Persistent Dark / Light Mode
1. **Action**: Click the theme toggle button in the navbar/sidebar to switch to Dark Mode, then refresh the page or open in a new tab.
2. **Expected Outcome**:
   - Entire interface applies dark theme styles (`dark:` Tailwind classes).
   - Theme preference persists across page reloads via `localStorage`.

### Scenario 6: Robust WebSocket Auto-Reconnect on Network Drop
1. **Action**: In Chrome DevTools Network tab, toggle "Offline" while on the chat view, wait 3 seconds, then toggle back "Online".
2. **Expected Outcome**:
   - Composable displays a subtle "Reconnecting..." badge.
   - On network restoration, WebSocket automatically reconnects using exponential backoff, validates authentication, and re-subscribes to the active thread seamlessly.

### Scenario 7: Multi-Tenant Cross-Access Security Gate
1. **Action**: Authenticated User 2 attempts to fetch User 1's document via API:
   ```bash
   curl -H "Authorization: Bearer <USER2_JWT>" http://localhost:8000/api/v1/documents/<USER1_DOC_ID>
   ```
2. **Expected Outcome**: Returns HTTP `404 Not Found`. Zero data or existence leakage.
