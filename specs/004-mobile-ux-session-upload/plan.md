# Implementation Plan: Mobile Navigation, Session Fallback & Mobile Upload Patch

**Branch**: `004-mobile-ux-session-upload` | **Date**: 2026-08-29 | **Spec**: [specs/004-mobile-ux-session-upload/spec.md](spec.md)

**Input**: Feature specification from `specs/004-mobile-ux-session-upload/spec.md` (Session Fallback via Vue Router, Sticky Mobile Navigation via Tailwind UI, and Mobile Upload MIME Normalization).

---

## Summary

Implement robust mobile navigation, 404 chat session recovery, and resilient mobile file uploads in the DocuMind frontend. Specifically:
1. **Session Fallback (Vue Router & Pinia)**: Intercept missing/404 chat session loads in `stores/chat.ts` and `views/ChatView.vue`, automatically redirecting to the base `/chat` view using `router.replace` to start or select a valid conversation thread without crashes.
2. **Mobile Navigation (Tailwind UI)**: Introduce a sticky mobile bottom tab bar (`MobileNavBar.vue` with `flex md:hidden`) allowing mobile users to toggle seamlessly between `/documents` and `/chat` with safe-area spacing (`pb-safe`).
3. **Mobile Upload Patch**: Update `DragDropZone.vue` to prioritize extension validation over volatile mobile MIME types, normalize `application/octet-stream` / empty types to canonical MIME headers, expand the file input `accept` whitelist, and reset hidden input values to guarantee consecutive `@change` event triggering.

---

## Technical Context

**Language/Version**: TypeScript 5.5+, Vue 3.5 (Composition API `<script setup>`), Python 3.11+  
**Primary Dependencies**: Vue Router 4.4, Pinia 2.2, Tailwind CSS 3.4 (`@tailwindcss/typography`), Lucide Vue Next 0.441, Axios 1.7  
**Storage**: Client LocalStorage (JWT token & Theme), Pinia Stores (`chat`, `document`, `auth`), PostgreSQL (Backend)  
**Testing**: `npm run build` (`vue-tsc && vite build`), manual responsive DevTools & mobile user-agent verification  
**Target Platform**: Responsive Web (iOS Safari, Android Chrome, Desktop 320px - 2560px)  
**Project Type**: Full-Stack Multi-Tenant Document Q&A RAG Application  
**Performance Goals**: <100ms tab transitions, <300ms session 404 recovery, 100% file picker event reliability  
**Constraints**: Zero changes to backend data schemas; full light/dark theme parity; complete backward compatibility with WebSocket streaming  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Modularity & Independence**: PASS. New mobile navigation is encapsulated in `MobileNavBar.vue` and upload normalization is scoped to `DragDropZone.vue`.
- **Principle II: Zero-Logic Breakage / Invariant**: PASS. Existing Pinia store interfaces and REST/WebSocket streaming contracts are preserved.
- **Principle III: Responsive UI & Dark Mode**: PASS. All new components include responsive classes (`flex md:hidden`) and full dark mode classes (`dark:bg-[#0d1410]`, `dark:text-emerald-400`).
- **Principle IV: Error Resilience & Graceful Fallback**: PASS. 404 session handling prevents unhandled exceptions and infinite redirection loops.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-mobile-ux-session-upload/
├── plan.md              # This file (/speckit-plan output)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Phase 1 output
    ├── ui-contracts.md
    └── mobile-upload-contract.md
```

### Source Code

```text
frontend/
├── src/
│   ├── App.vue                              # Register MobileNavBar & add bottom padding for mobile
│   ├── components/
│   │   ├── documents/
│   │   │   └── DragDropZone.vue             # Extension-first validation, MIME normalizer, input reset
│   │   └── layout/
│   │       └── MobileNavBar.vue             # NEW: Sticky bottom tab bar (flex md:hidden)
│   ├── stores/
│   │   └── chat.ts                          # Update selectSession to return boolean & catch 404s
│   └── views/
│       ├── ChatView.vue                     # Add 404 session fallback + route parameter watcher
│       └── DocumentsView.vue                # Ensure responsive spacing for mobile bottom bar
```

**Structure Decision**: Standard Vue 3 / Vite architecture. All modifications are localized to the frontend presentation layer (`frontend/src/`).

---

## Complexity Tracking

*No constitution violations or unjustified complexities identified.*
