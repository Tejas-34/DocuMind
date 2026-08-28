# Phase 1: Component Interface & Props Invariant Contracts

**Feature**: UI Styling & Visual Polish (`002-ui-styling-polish`)
**Date**: 2026-08-28

---

## 1. Zero-Logic Component Contracts

All Vue components being refactored must strictly preserve their external props, emits, and slot contracts without breaking changes.

### A. Auth Views (`LoginView.vue`, `RegisterView.vue`)
- **Internal State Preserved**: `email` (string), `password` (string), `isPasswordVisible` (boolean, optional UI state).
- **Store Actions Preserved**: `authStore.login(email, password)`, `authStore.register(email, password)`.
- **Router Navigation**: Redirects to `/documents` or `route.query.redirect`.

---

### B. DragDropZone (`DragDropZone.vue`)
- **Props**:
  ```typescript
  defineProps<{
    isUploading: boolean
  }>()
  ```
- **Emits**:
  ```typescript
  defineEmits<{
    (e: 'filesSelected', files: File[]): void
  }>()
  ```
- **File Validation Rules**: Accepts `.pdf`, `.txt`, `.md`, size <= 25MB, non-zero bytes.

---

### C. DocumentGrid (`DocumentGrid.vue`)
- **Props**:
  ```typescript
  defineProps<{
    documents: DocumentItem[]
  }>()
  ```
- **Emits**:
  ```typescript
  defineEmits<{
    (e: 'viewDetails', doc: DocumentItem): void
    (e: 'deleteDoc', doc: DocumentItem): void
  }>()
  ```
- **Features**: Copy Document ID to clipboard, responsive table horizontal scroll wrapper.

---

### D. StatusBadge (`StatusBadge.vue`)
- **Props**:
  ```typescript
  defineProps<{
    status: 'ready' | 'processing' | 'failed' | string
  }>()
  ```
- **Rendering**: Pill with pulsating dot indicator, theme-adaptive tint.

---

### E. ChatSidebar (`ChatSidebar.vue`)
- **Props**:
  ```typescript
  defineProps<{
    sessions: ChatSession[]
    activeSessionId: string | null
  }>()
  ```
- **Emits**:
  ```typescript
  defineEmits<{
    (e: 'newChat'): void
    (e: 'selectSession', id: string): void
    (e: 'renameSession', session: ChatSession): void
    (e: 'deleteSession', session: ChatSession): void
    (e: 'clearContext'): void
  }>()
  ```

---

### F. ChatWindow (`ChatWindow.vue`)
- **Props**:
  ```typescript
  defineProps<{
    messages: Message[]
    streamingContent: string
    statusMessage: string
    isStreaming: boolean
    isConnected: boolean
  }>()
  ```
- **Emits**:
  ```typescript
  defineEmits<{
    (e: 'sendQuery', query: string): void
  }>()
  ```
- **Suggestion Chips**: When a chip is clicked, trigger `emit('sendQuery', chip.promptText)` or populate `inputQuery` and submit.

---

### G. AppNavbar (`AppNavbar.vue`)
- **Navigation Links**:
  - `/documents` (Document Workspace)
  - `/chat` (AI Document Q&A)
- **Controls**:
  - Theme toggle (`<ThemeToggle />`)
  - User initials avatar & email indicator
  - Logout action (`authStore.logout()`)
