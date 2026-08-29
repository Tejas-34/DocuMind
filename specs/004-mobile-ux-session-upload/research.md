# Research: Mobile Navigation, Session Fallback & Mobile Upload Patch

**Feature Branch**: `004-mobile-ux-session-upload` | **Date**: 2026-08-29

---

## 1. Chat Session 404 Fallback & URL Synchronization

### Context & Problem
When a user navigates directly to `/chat/:sessionId` with an expired, non-existent, or foreign session ID (or if a session was deleted from another device), `GET /api/v1/chat/sessions/{sessionId}` returns HTTP 404. Currently, `ChatView.vue` and `useChatStore` log the error to the console without updating the route or recovering the UI state, leaving the active session null and the user stranded on a blank conversation window.

### Decision
1. In `stores/chat.ts`, update `selectSession(sessionId: string): Promise<boolean>` to return `true` on successful retrieval, and catch 400/404 errors, clean up active session state, and return `false`.
2. In `views/ChatView.vue`, inspect the outcome of `selectSession`. If it returns `false`:
   - Replace the route using `router.replace('/chat')` (preventing history pollution and back-button traps).
   - If the user has other sessions in `chatStore.sessions`, select the first valid session; otherwise, call `handleNewChat()` to create a fresh conversation thread.
3. Add a watcher on `() => route.params.sessionId` to trigger graceful fallback when the user updates the URL parameters directly within an active session.

### Rationale
- `router.replace` ensures the user's browser back button doesn't loop back to the broken 404 session ID.
- Keeping the fallback logic inside `ChatView.vue` and `useChatStore` avoids polluting global Axios response interceptors (which could falsely intercept other legitimate 404s like search results).

### Alternatives Considered
- **Global Vue Router Navigation Guard**: Fetching session data in `router.beforeEach` blocks route transitions for all navigation, adding network latency to every page load.
- **Global Axios 404 Interceptor**: Intercepting all 404s globally would trigger inappropriate `/chat` redirects for missing documents or other REST resources.

---

## 2. Responsive Mobile Navigation Architecture

### Context & Problem
On desktop viewports (>=768px), navigation between `/documents` (Document Workspace) and `/chat` (AI Chat) is provided by the central links in `AppNavbar.vue` (`hidden md:flex`). On mobile screens (<768px), these links are hidden to fit the brand logo, theme toggle, and profile avatar. Consequently, mobile users cannot toggle between Document Workspace and AI Chat.

### Decision
1. Implement a sticky, thumb-friendly bottom navigation bar component (`MobileNavBar.vue`) rendered within `App.vue` or `AppNavbar.vue`.
2. Apply Tailwind responsive visibility: `flex md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 dark:bg-[#0d1410]/95 backdrop-blur-md border-t border-gray-100 dark:border-gray-800 pb-safe shadow-lg`.
3. Display clear tabs for `/documents` (Document Workspace) with `FolderClosed` icon and `/chat` (AI Chat) with `MessageSquare` icon, highlighting active routes with `#153826` (dark: `text-emerald-400`).
4. Apply bottom content padding (`pb-16` / `pb-20 md:pb-0`) to `<main>` so bottom navigation never occludes document cards, dropzones, or chat input prompts.
5. Hide the mobile bar when the user is unauthenticated (`!authStore.isAuthenticated` on `/login` or `/register`).

### Rationale
- Bottom navigation is the universal UX pattern for modern mobile web apps, offering optimal ergonomics for one-handed thumb navigation.
- Tailwind's responsive classes (`flex md:hidden`) ensure zero footprint or layout shift on tablet/desktop displays.
- `pb-safe` handles device-specific safe-area insets (e.g. iPhone home bar).

### Alternatives Considered
- **Top Hamburger Menu in AppNavbar**: Requires multi-step interaction (tap hamburger -> wait for drawer -> tap route), hindering frequent switching between document management and chat querying.
- **Responsive Overflow Menu**: Crowds the existing top header, clashing with the brand logo and tenant badge.

---

## 3. Mobile File Upload Normalization & Hidden Input Reliability

### Context & Problem
Mobile browsers (iOS Safari, Android Chrome, Samsung Internet, and embedded webviews) frequently assign generic `application/octet-stream` or empty MIME types (`""`) to valid `.pdf`, `.txt`, and `.md` files selected via native file pickers. Furthermore, hidden `<input type="file" />` elements often fail to trigger the `@change` event if a user re-selects the same file or if the input value is not reset properly before invoking `.click()`.

### Decision
1. **Extension-First Validation**: In `DragDropZone.vue`, validate files based on their lowercase filename extension:
   ```typescript
   const ext = file.name.split('.').pop()?.toLowerCase() || ''
   const isValidExt = ['pdf', 'txt', 'md'].includes(ext)
   ```
   Allow files with `application/octet-stream` or empty MIME type as long as their filename extension is valid.
2. **Canonical MIME Normalization**: In `DragDropZone.vue` / `documentService.ts`, when packaging files for `FormData`, map extensions to canonical MIME types:
   ```typescript
   const mimeMap: Record<string, string> = {
     pdf: 'application/pdf',
     txt: 'text/plain',
     md: 'text/markdown',
   }
   const normalizedMime = mimeMap[ext] || file.type || 'application/octet-stream'
   ```
   Reconstruct a normalized `File` or `Blob` if `file.type` is missing or generic:
   ```typescript
   const normalizedFile = file.type && file.type !== 'application/octet-stream'
     ? file
     : new File([file], file.name, { type: normalizedMime, lastModified: file.lastModified })
   ```
3. **Hidden Input Reset Pattern**:
   - Update `accept` attribute to `.pdf,.txt,.md,application/pdf,text/plain,text/markdown,application/octet-stream`.
   - In `triggerBrowse()`, explicitly clear `fileInput.value.value = ''` immediately before invoking `fileInput.value.click()`.
   - In `handleFileInput()`, clear `fileInput.value.value = ''` immediately after extracting `files` to guarantee subsequent picks of the same file always trigger `@change`.

### Rationale
- Normalizing at the client boundary guarantees the backend receives standard headers without compromising server-side security checks.
- Clearing the file input before and after selection is standard DOM practice to prevent swallowed `@change` events on all mobile browsers.

### Alternatives Considered
- **Client-Side Magic Byte Sniffing (FileReader)**: Reading the first 4 bytes (`%PDF`) for every file adds unnecessary CPU overhead for large 25MB files; the backend already performs server-side magic byte validation.
- **Loosening Backend Security Restrictions**: Permitting arbitrary MIME types on the backend would violate tenant isolation and upload safety rules.
