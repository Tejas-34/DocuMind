# Quickstart Validation Guide: Mobile Navigation, Session Fallback & Mobile Upload

**Feature Branch**: `004-mobile-ux-session-upload` | **Date**: 2026-08-29

This guide describes the end-to-end verification workflows to validate the implementation of Session Fallback, Sticky Mobile Navigation, and Mobile File Upload Normalization.

---

## Prerequisites

1. Frontend and Backend running locally:
   ```bash
   # Backend
   cd backend && uvicorn src.main:app --reload --port 8000
   
   # Frontend
   cd frontend && npm run dev
   ```
2. Authenticated user logged into `http://localhost:5173`.

---

## Validation Scenarios

### Scenario 1: Session Fallback (404 / Invalid Session ID Recovery)

**Objective**: Verify that direct navigation to a non-existent or invalid session ID gracefully redirects to `/chat` and recovers without UI freeze or error.

1. **Steps**:
   - Log into DocuMind.
   - In browser address bar, enter `http://localhost:5173/chat/00000000-0000-0000-0000-000000000000` (or `http://localhost:5173/chat/non-existent-session`).
   - Press Enter.
2. **Expected Outcome**:
   - URL immediately updates from `/chat/0000...` to `/chat` (or the first valid session `/chat/{validId}`).
   - No unhandled runtime error occurs in browser DevTools Console.
   - The user can immediately type and send a query in the chat input.

---

### Scenario 2: Mobile Sticky Bottom Navigation

**Objective**: Verify responsive bottom tab bar on viewports < 768px.

1. **Steps**:
   - Open DevTools and toggle Device Toolbar (set width to 375px or iPhone 14).
   - Ensure user is authenticated and on `/documents`.
   - Observe the sticky bottom bar with `Documents` and `AI Chat` tabs.
   - Tap `AI Chat`.
   - Tap `Documents`.
2. **Expected Outcome**:
   - The mobile bottom bar is visible with `flex md:hidden` styling.
   - Tapping `AI Chat` smoothly navigates to `/chat`, highlighting the AI Chat tab in emerald brand styling (`#153826` / `text-emerald-500`).
   - Tapping `Documents` navigates to `/documents`, highlighting the Documents tab.
   - Document cards and chat input prompt are padded from the bottom (`pb-20 md:pb-0`) with zero visual occlusion.
   - Resizing window to desktop (>= 768px) hides the bottom bar and shows the top navbar tabs.

---

### Scenario 3: Mobile Upload Normalization & Hidden Input Reset

**Objective**: Verify mobile file selection with generic MIME type and repeated selection.

1. **Steps**:
   - On `/documents`, click/tap the `DragDropZone` upload area.
   - Select a sample PDF file `sample.pdf`.
   - After upload completes, click/tap `DragDropZone` again and select the **exact same** `sample.pdf` file without refreshing the page.
2. **Expected Outcome**:
   - File validation succeeds even if MIME type is reported as `application/octet-stream` or empty `""`.
   - The hidden file input fires the `@change` event on both the first and second consecutive selection of the identical file.
   - Document appears in the DocumentGrid and transitions to Ready status.
