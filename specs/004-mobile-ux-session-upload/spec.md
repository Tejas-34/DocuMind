# Feature Specification: Mobile Navigation, Session Fallback & Mobile Upload Patch

**Feature Branch**: `004-mobile-ux-session-upload`

**Created**: 2026-08-29

**Status**: Draft

**Input**: User description: "Session Fallback (Vue Router): We will intercept the logic that loads a specific chat session. If the API returns a 404 Not Found (or if the session ID doesn't exist in the local Pinia store), Vue Router will programmatically push the user back to the base /chat view to start a fresh thread. Mobile Navigation (Tailwind UI): Since the desktop sidebars collapse or disappear on mobile, we will add a sticky mobile-only navigation bar (e.g., a bottom tab bar or a simplified top header). We'll use Tailwind's responsive classes (flex md:hidden) to ensure it only appears on small screens, allowing users to toggle between /documents and /chat. Mobile Upload Patch: Mobile browsers often assign generic application/octet-stream MIME types to PDFs or fail to trigger the @change event on hidden file inputs. We will ensure the Vue file input strictly accepts our required extensions and gracefully handles mobile-specific file objects before appending them to the FormData payload."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Graceful Chat Session Fallback & Recovery (Priority: P1)

As a user opening an expired, deleted, or invalid chat session link (or accessing a bookmarked thread that no longer exists), I want the application to detect the missing session and automatically redirect me to the base chat workspace (`/chat`) to create or load a valid conversation, so that I never get stuck on a broken, blank, or crashing screen.

**Why this priority**: Directly prevents unhandled UI crashes and dead-end blank states when navigating via direct URLs or old history.

**Independent Test**: Navigate directly to `/chat/00000000-0000-0000-0000-000000000000` (or any non-existent session UUID). Verify that the app intercepts the 404 response, redirects the URL to `/chat`, and initializes a clean, functional conversation thread without errors in the console.

**Acceptance Scenarios**:
1. **Given** a user navigating directly to `/chat/:sessionId` where `:sessionId` returns 404 from `GET /api/v1/chat/sessions/:id` (or is not in the local store), **When** the session fetch fails, **Then** the router programmatically replaces the route with `/chat`, resets active session state, and initiates a new session or selects the first available session.
2. **Given** a user inside an active session that is deleted from another tab or client, **When** the user triggers a reload or re-select, **Then** the application falls back gracefully to `/chat` instead of displaying corrupted message history.
3. **Given** a direct URL with an invalid non-UUID string format (e.g., `/chat/invalid-id`), **When** evaluated, **Then** the app smoothly routes back to `/chat` without uncaught client exceptions.

---

### User Story 2 - Sticky Mobile Bottom Navigation Bar (Priority: P1)

As a mobile user accessing DocuMind on a smartphone screen, I want a persistent, thumb-friendly navigation bar at the bottom of the screen so that I can effortlessly switch between the Document Workspace (`/documents`) and AI Chat (`/chat`) without needing desktop sidebars or opening nested menus.

**Why this priority**: Mobile screens currently hide the desktop top navbar links (`hidden md:flex`), leaving mobile users with no way to navigate between documents and chat.

**Independent Test**: View the app on a mobile viewport (<768px width) while authenticated. Verify the bottom tab bar is visible, contains active route indicators for "Documents" and "AI Chat", smoothly navigates between routes upon tapping, and is completely hidden on tablet/desktop viewports (>=768px).

**Acceptance Scenarios**:
1. **Given** an authenticated user on a screen narrower than 768px, **When** viewing any authenticated route, **Then** a sticky mobile navigation bar is displayed at the bottom (`flex md:hidden`) with touch targets for `/documents` and `/chat`.
2. **Given** the mobile navigation bar, **When** the current route matches `/documents` or `/chat`, **Then** the corresponding tab displays the active green brand styling (`#153826` / `text-emerald-500` / bold font) with proper accessibility attributes (`aria-current="page"`).
3. **Given** a mobile device with home-indicator / safe-area insets (e.g., iOS Safari), **When** viewing the mobile bar, **Then** the bar accounts for safe-area padding (`pb-safe`) and does not obstruct chat input boxes or bottom content.
4. **Given** an unauthenticated user on `/login` or `/register`, **When** on a mobile screen, **Then** the mobile navigation bar is not displayed.

---

### User Story 3 - Resilient Mobile File Upload Normalization (Priority: P1)

As a user uploading PDF, TXT, or Markdown documents from a mobile browser (iOS Safari, Android Chrome, mobile webviews), I want file selection and uploads to work seamlessly regardless of whether the mobile OS assigns generic `application/octet-stream` MIME types or handles file picker events uniquely.

**Why this priority**: Mobile OS file pickers frequently report generic MIME types (`application/octet-stream` or empty strings) or fail to fire subsequent `@change` events on hidden file inputs, resulting in false rejection or unresponsive file pickers.

**Independent Test**: On a mobile browser (or simulated mobile user agent / file picker with `application/octet-stream` PDF), select a `.pdf` file. Verify the file is recognized as valid PDF, correctly converted/assigned the proper MIME type, successfully uploaded to the backend `/api/v1/documents`, and processed into vectors.

**Acceptance Scenarios**:
1. **Given** a user selecting a file on mobile where `file.type` is `application/octet-stream` or `""` but `file.name` ends with `.pdf`, `.txt`, or `.md`, **When** validated by `DragDropZone.vue`, **Then** validation succeeds and the normalized file is appended to `FormData`.
2. **Given** a hidden `<input type="file" />`, **When** the user taps the upload dropzone, **Then** the input value is reset before browse trigger to guarantee subsequent selections of the same file always emit the `@change` event.
3. **Given** the file input element, **When** rendered in the DOM, **Then** the `accept` attribute includes both extension patterns (`.pdf,.txt,.md`) and standard MIME types (`application/pdf,text/plain,text/markdown,application/octet-stream`) to prevent mobile OS file pickers from disabling valid documents.

---

## Edge Cases

- **Rapid Multiple Session Transitions**: Rapidly switching session IDs in URL while requests are in-flight should abort or ignore stale 404 responses from earlier session requests.
- **Empty File Uploads on Mobile**: Files with 0 bytes or corrupt mobile pointers must display a clear, friendly error toast ("File is empty or unreadable").
- **iOS Viewport Keyboard Resizing**: When virtual keyboard opens in mobile chat, the sticky mobile bottom bar should adapt or hide to prevent consuming vertical viewport space during active typing.
- **Session List Empty**: If a 404 occurs and the user has 0 existing sessions in their account, redirect to `/chat` and create a fresh session smoothly.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `chatStore.selectSession(sessionId)` MUST catch 404 / 400 errors from `chatService.getSession` and return a boolean status (`true` on success, `false` on failure).
- **FR-002**: In `ChatView.vue`, if `selectSession` returns `false` (or session is not found in local state), the router MUST call `router.replace('/chat')` and invoke `handleNewChat()`.
- **FR-003**: The router MUST support dynamic route watcher on `route.params.sessionId` to trigger graceful fallback when the user updates the URL parameters directly.
- **FR-004**: An authenticated Mobile Navigation component (`MobileNavBar.vue` or integrated in layout) MUST be displayed on small viewports (`flex md:hidden`) and hidden on desktop (`hidden md:flex`).
- **FR-005**: The Mobile Navigation bar MUST provide persistent links to `/documents` (Document Workspace) and `/chat` (AI Chat) with distinct active state highlights.
- **FR-006**: The Mobile Navigation bar MUST be sticky/fixed with high z-index (`z-40`), safe-area padding (`env(safe-area-inset-bottom)`), and top border separation.
- **FR-007**: Main content wrappers and views MUST include bottom padding (`pb-16` / `pb-20 md:pb-0`) to prevent UI overlap with the sticky mobile bottom bar.
- **FR-008**: `DragDropZone.vue` validation logic MUST inspect the lowercase file extension (`.pdf`, `.txt`, `.md`) as the primary format validator, allowing `application/octet-stream` or empty MIME types if the extension is valid.
- **FR-009**: When uploading a file with generic `application/octet-stream` or empty MIME type, the frontend client MUST normalize the `Blob`/`File` content type to the appropriate canonical MIME type (`application/pdf`, `text/plain`, `text/markdown`) before appending to `FormData`.
- **FR-010**: The hidden file input's `accept` attribute MUST allow `.pdf,.txt,.md,application/pdf,text/plain,text/markdown,application/octet-stream`.
- **FR-011**: The hidden file input element MUST clear its `value` before triggering the native file browser and immediately after change event emission to guarantee re-selection reliability.
- **FR-012**: Mobile tap interactions on `DragDropZone.vue` MUST prevent duplicate event triggers and provide responsive visual feedback.

---

## Key Entities & State

- **NavigationState**: Active route path (`/documents` vs `/chat`), authenticated user presence.
- **SessionLoadState**: `isLoadingActiveSession`, `activeSession` (`ChatSession | null`), session selection outcome (`success: boolean`).
- **NormalizedFile**: File object with guaranteed valid extension (`pdf` | `txt` | `md`), validated size (<=25MB, >0B), and canonical MIME type.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of invalid or 404 session route visits redirect to `/chat` and initialize a functional thread within <300ms without unhandled JavaScript exceptions.
- **SC-002**: Mobile navigation allows single-tap switching between `/documents` and `/chat` on all viewports <768px with <100ms response time.
- **SC-003**: 100% of valid `.pdf`, `.txt`, and `.md` files selected on mobile browsers (including those emitting `application/octet-stream`) pass validation and upload successfully.
- **SC-004**: Re-selecting the identical file consecutively in `DragDropZone.vue` triggers the `@change` event 100% of the time across mobile and desktop browsers.
- **SC-005**: Zero visual occlusion or overlap of mobile chat input / send button caused by the sticky navigation bar.

---

## Assumptions

- **Target Viewports**: Mobile viewports ranging from 320px to 767px width; desktop viewports >= 768px width.
- **Browser Capabilities**: Target mobile browsers support Vue Router 4 History mode, standard `FormData`, `File`/`Blob` APIs, and CSS `env(safe-area-inset-bottom)`.
- **Backend API**: The backend `/api/v1/chat/sessions/{id}` returns standard HTTP 404 when a session does not exist or does not belong to the requesting tenant.
