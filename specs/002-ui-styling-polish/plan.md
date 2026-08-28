# Implementation Plan: UI Styling & Visual Polish

**Branch**: `002-ui-styling-polish` | **Date**: 2026-08-28 | **Spec**: [specs/002-ui-styling-polish/spec.md](spec.md)

**Input**: Feature specification from `specs/002-ui-styling-polish/spec.md` and high-fidelity reference design (`ChatGPT Image Aug 28, 2026, 01_20_12 PM.png`).

---

## Summary

Refactor the frontend UI styling across the Authentication (Login/Signup), Document Workspace, and AI Chat views to achieve high-fidelity parity with the provided reference designs. The overhaul introduces a deep forest green brand palette (`#153826`), 24px container radii, diffuse ambient drop shadows, tracked uppercase data headers, active status dots, interactive chat suggestion chips, and a mobile collapsible sidebar drawer, while strictly preserving all existing Vue reactivity, stores, API services, and WebSocket streaming logic.

---

## Technical Context

**Language/Version**: TypeScript 5.x, Vue 3.5 (Composition API `<script setup>`)  
**Primary Dependencies**: Vite 5.x, Tailwind CSS 3.4 (`@tailwindcss/typography`), Pinia 2.2, Vue Router 4.4, Lucide Vue Next, Marked  
**Storage**: Client LocalStorage (Theme & Auth token persistence)  
**Testing**: `npm run build` (Vue-TSC / Vite compilation check), Playwright / Manual browser visual regression  
**Target Platform**: Responsive Web (Mobile 375px+, Tablet 768px+, Desktop 1024px-1920px+)  
**Project Type**: Single-Page Web Application (Frontend only)  
**Performance Goals**: Instant theme toggling (<50ms), 60fps smooth drawer animations, zero layout shifts  
**Constraints**: Strict Zero-Logic Change Invariant (No modifications to Pinia stores, API contracts, props, emits, or WebSocket streaming)  
**Scale/Scope**: 4 primary views (Login, Register, Documents, Chat) + 6 child components (Navbar, Dropzone, Grid, Sidebar, Window, Badges)  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Library-First & Modular Components**: PASS. Refactoring remains cleanly compartmentalized in Vue presentation components without coupling.
- **Principle II: Zero-Logic / Contract Invariant**: PASS. Props, emits, and store signatures remain 100% backward-compatible.
- **Principle III: Design Consistency & Dark Mode**: PASS. All new components implement complete light/dark Tailwind class parity.
- **Principle IV: Responsiveness**: PASS. Fluid grids, horizontal table wrappers, and collapsible mobile navigation are specified and designed.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-ui-styling-polish/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── ui-contracts.md
└── checklists/
    └── requirements.md  # Requirements validation checklist
```

### Source Code (repository layout)

```text
frontend/
├── src/
│   ├── assets/
│   │   └── main.css                          # Global tokens, scrollbar & ambient styles
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatSidebar.vue               # Polished hierarchy, tracked header, mobile drawer integration
│   │   │   ├── ChatWindow.vue                # Suggestion chips 2x2 grid, floating chat input bar
│   │   │   ├── CitationPill.vue              # Inline source attribution badge
│   │   │   └── MessageBubble.vue             # Differentiated user/assistant bubbles, markdown prose
│   │   ├── common/
│   │   │   ├── Modal.vue                     # Blurred backdrop, rounded-3xl dialog container
│   │   │   ├── StatusBadge.vue               # Pulsating dot indicator (• Ready / • Processing)
│   │   │   └── ThemeToggle.vue               # Theme switcher button
│   │   ├── documents/
│   │   │   ├── DeleteDocModal.vue            # Delete confirmation modal
│   │   │   ├── DocumentGrid.vue              # Tracked uppercase headers, PDF badges, copy pill, overflow scroll
│   │   │   └── DragDropZone.vue              # Tinted dropzone, soft dashed border, active drag state
│   │   └── layout/
│   │       └── AppNavbar.vue                 # Brand green logo, active tab bottom border indicator, user initials
│   ├── views/
│   │   ├── ChatView.vue                      # Mobile hamburger menu & collapsible sidebar drawer state
│   │   ├── DocumentsView.vue                 # Header with + Upload button, responsive layout
│   │   ├── LoginView.vue                     # 2-column split layout with value props & floating card
│   │   └── RegisterView.vue                  # 2-column split layout with value props & floating card
│   ├── tailwind.config.js                    # Extended brand palette (#153826), border radii, shadows
│   └── main.ts
```

**Structure Decision**: Standard Vue 3 frontend architecture. All edits are localized to `frontend/tailwind.config.js`, `frontend/src/assets/main.css`, and `frontend/src/{views,components}/**/*.vue`.

---

## Complexity Tracking

*No constitution violations or unjustified complexities identified.*
