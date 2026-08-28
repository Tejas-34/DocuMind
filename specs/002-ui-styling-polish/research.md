# Phase 0: Research & Technical Decisions

**Feature**: UI Styling & Visual Polish (`002-ui-styling-polish`)
**Date**: 2026-08-28

---

## 1. Brand Color System & Design Tokens

### Decision
Adopt a deep forest green primary brand system (`#153826` / `rgb(21, 56, 38)`) with complementary sage/emerald tints, elevated 24px border radius (`rounded-[24px]` / `rounded-3xl`), diffuse ambient drop shadows (`shadow-xl shadow-black/5`), and refined typography tracking (`tracking-wider`, `tracking-widest` for uppercase table/section headers).

### Rationale
- The provided high-fidelity reference design (`ChatGPT Image Aug 28, 2026, 01_20_12 PM.png`) establishes a distinctive, authoritative aesthetic centered on deep forest green `#153826`.
- High border radii (24px) give cards and modal containers a soft, modern floating appearance.
- Soft diffuse drop shadows reduce visual harshness compared to heavy 1px solid borders.
- Increased tracking on small uppercase headers (`text-[10px]` / `text-[11px]`) enhances readability and aligns with enterprise-grade UI design standards.

### Alternatives Considered
- *Standard Indigo/Blue palette*: Rejected because it diverges from the reference design.
- *Sharp rectangular borders (`rounded-md` / 6px)*: Rejected because the reference design emphasizes organic 24px rounded corners across all panels, cards, and dropzones.

---

## 2. Authentication Views (Login & Signup) 2-Column Responsive Layout

### Decision
Implement a responsive 2-column split layout (`grid lg:grid-cols-2 gap-12 items-center max-w-5xl mx-auto`) for both `LoginView.vue` and `RegisterView.vue`:
- **Left Column**: Brand value proposition header, subtitle, and 3 feature rows with iconography (`ShieldCheck`, `Sparkles`, `Search` for Login; `UploadCloud`, `MessageSquare`, `Shield` for Register).
- **Right Column**: Floating card container (`rounded-[24px] bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow-xl shadow-black/5`) housing the form inputs, input icon adornments (`Mail`, `Lock`, `Eye`/`EyeOff`), submit button (`bg-[#153826] hover:bg-[#1e4d35] text-white py-3 rounded-xl`), and navigation links.
- On mobile (`<1024px`), stack the layout gracefully with the card prominently displayed and value propositions neatly positioned.

### Rationale
- Matches the exact reference design mockup.
- Retains 100% of existing Vue bindings (`v-model="email"`, `v-model="password"`, `handleLogin`, `handleRegister`, `authStore.isLoading`, `authStore.error`).

### Alternatives Considered
- *Single-column centered card on all viewports*: Rejected because it underutilizes desktop screen real estate and misses the reference design's 3-point value proposition columns.

---

## 3. Workspace Components & Dropzone Refactoring

### Decision
- **Dropzone (`DragDropZone.vue`)**:
  - Apply softer dashed border (`border-dashed border-gray-200 dark:border-gray-800 hover:border-emerald-300 dark:hover:border-emerald-700/60`).
  - Subtle background tint (`bg-[#f9faf9] dark:bg-[#121915]/50 hover:bg-[#f3f6f4] dark:hover:bg-[#15211b]/60`).
  - Cloud upload icon within rounded container.
  - Active drag-and-drop state with smooth scaling and border highlight.
- **DataTable (`DocumentGrid.vue`)**:
  - Header styling: small uppercase typography with increased tracking (`text-[10px] uppercase tracking-wider font-semibold text-gray-400 dark:text-gray-500`).
  - Red PDF icon badge for `.pdf` files.
  - Document ID pill with copy action.
  - Responsive horizontal scroll wrapper (`overflow-x-auto`) to support mobile viewing without column clipping.
- **Status Badge (`StatusBadge.vue`)**:
  - Add pulsating status dot indicator (`<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>`) to the Ready badge (`• Ready`) and corresponding dots for Processing and Failed states.

### Rationale
- Perfectly reproduces the visual hierarchy in the reference design.
- Preserves all file handling emits (`@filesSelected`), delete/view events, and clipboard copying.

---

## 4. AI Chat Components & Interactive Suggestion Chips

### Decision
- **Chat Empty State & Suggestion Chips (`ChatWindow.vue`)**:
  - Circular soft green tinted badge with Sparkles icon.
  - Header: "Document Reference Assistant" in `#153826`.
  - Subtitle: "Ask any question about your uploaded documents. Answers are grounded strictly in your files with interactive citations."
  - "Try asking:" label above 4 interactive suggestion chips in a 2x2 grid:
    1. `Summarize the key points` (`FileText` icon)
    2. `What are the main topics?` (`Sparkles` icon)
    3. `Find terms related to...` (`Search` icon)
    4. `List important dates` (`Calendar` icon)
  - Clicking any chip populates `inputQuery` and submits the query via existing `handleSubmit` / `emit('sendQuery')`.
- **Chat Input Bar (`ChatWindow.vue`)**:
  - Floating card container with `rounded-2xl` / `rounded-3xl`, diffuse shadow (`shadow-lg shadow-black/5`), no rigid outer borders.
  - Input field with placeholder and trailing green pill button (`bg-[#153826] hover:bg-[#1e4d35] text-white rounded-xl px-4 py-2 font-medium`).
- **Sidebar Button Hierarchy (`ChatSidebar.vue`)**:
  - Primary button: `+ New Chat Session` (solid `#153826` green fill).
  - Secondary button: `Clear Current Context` (subtle amber tint `bg-amber-50/50 text-amber-700 border border-amber-200/50`, reduced visual weight).
  - Tracked uppercase section header: `CONVERSATION THREADS` with counter badge.
  - Persistent bottom card: "Strict Privacy Sandbox" with shield icon.
- **Mobile Collapsible Sidebar Drawer (`ChatView.vue` + `ChatSidebar.vue`)**:
  - Add reactive `isSidebarOpen` state in `ChatView.vue`.
  - On mobile (`<768px`), display a top bar with a hamburger menu button (`Menu` icon) to toggle sidebar overlay with transition backdrop.

### Rationale
- Enhances discoverability and onboarding for new users while preserving chat session selection and WebSocket streaming functionality.

---

## 5. Navigation Bar & Global Layout

### Decision
- **Navbar (`AppNavbar.vue`)**:
  - Brand logo with `#153826` green background and flower/lotus icon.
  - "Tenant Isolated" outline pill badge with shield icon.
  - Tab navigation with bottom active indicator:
    - Active tab: bottom border underline `border-b-2 border-[#153826] text-gray-900 dark:text-white font-semibold`.
    - Inactive tab: `text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white`.
  - Right: Theme toggle, Avatar circle with initial, Email address with dropdown chevron.

---

## 6. Zero-Logic Invariant Verification Strategy

### Decision
Every Vue template change will preserve all existing:
- `v-model` bindings
- Props definitions (`defineProps`)
- Emits definitions (`defineEmits`)
- Pinia store invocations (`useAuthStore`, `useDocumentStore`, `useChatStore`)
- WebSocket callbacks (`useChatWebSocket`)
- Router links & navigation guards

No backend endpoints, database models, or API payloads will be altered.
