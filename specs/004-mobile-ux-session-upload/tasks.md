# Tasks: Global Navigation Consistency & Document Page Theme Parity

**Feature Branch**: `004-mobile-ux-session-upload` | **Date**: 2026-08-29

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Baseline verification of frontend dependencies and working tree

- [X] T001 [P] Verify development environment dependencies and Git working tree state

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ensure global navigation bar is consistently fixed and visible across all routes

**⚠️ CRITICAL**: Must complete before view-specific refinements

- [X] T002 [P] Restore consistent fixed global top navigation in frontend/src/components/layout/AppNavbar.vue across all views

**Checkpoint**: Fixed navigation bar active across all views on both desktop and mobile.

---

## Phase 3: User Story 1 - Remove Left Sidebar & Restore Layout Consistency (Priority: P1) 🎯 MVP

**Goal**: Remove the duplicate left sidebar from the document page, restore a clean container layout under the fixed `AppNavbar`, and ensure seamless layout consistency between Document Workspace and AI Chat views.

**Independent Test**: Navigate to `http://localhost:5173/documents` on desktop. Verify that `AppNavbar` is fixed at the top, the left sidebar is completely removed, and the Document Workspace content is cleanly centered (`max-w-6xl mx-auto`).

### Implementation for User Story 1

- [X] T003 [US1] Remove desktop left sidebar and redundant top controls from frontend/src/views/DocumentsView.vue
- [X] T004 [P] [US1] Clean up layout structure and container padding in frontend/src/App.vue

**Checkpoint**: User Story 1 is fully functional and layout is consistent across all pages.

---

## Phase 4: User Story 2 - Complete Light & Dark Theme Parity (Priority: P1)

**Goal**: Ensure all document components (DocumentGrid, DragDropZone, Modals, Search, Filters, Tables, Pagination) look flawless and cohesive in both light theme and dark theme.

**Independent Test**: Toggle theme between Light and Dark on `/documents`. Verify all table backgrounds, borders, search inputs, dropdowns, buttons, text, and badges transition cleanly with optimal contrast in both modes.

### Implementation for User Story 2

- [X] T005 [P] [US2] Update frontend/src/components/documents/DragDropZone.vue with complete light/dark theme class parity
- [X] T006 [P] [US2] Update frontend/src/components/documents/DocumentGrid.vue with complete light/dark theme styling for search, filters, table, and pagination
- [X] T007 [US2] Ensure complete light/dark theme styling on modals and badges in frontend/src/views/DocumentsView.vue

**Checkpoint**: User Story 2 is verified with full dark and light mode fidelity.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verification, type safety, and responsive theme regression testing

- [X] T008 [P] Run TypeScript typecheck and frontend production build via npm run build in frontend/
- [X] T009 Verify visual presentation and theme toggle across desktop (1920px, 1440px, 1024px) and mobile (375px) viewports

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - starts immediately.
- **Foundational (Phase 2)**: Depends on Setup (T001) - blocks User Stories.
- **User Stories (Phases 3, 4)**: Depend on Foundational completion (T002).
  - User Story 1 (Phase 3) and User Story 2 (Phase 4) can proceed concurrently.
- **Polish (Phase 5)**: Depends on all user story implementation tasks (T003-T007).

### Parallel Opportunities

- `T003` ([US1]), `T005` ([US2]), and `T006` ([US2]) can execute in parallel as they touch distinct components.
- `T008` and `T009` execute in parallel during Polish.

---

## Implementation Strategy

### Incremental Delivery

1. Fix global top navigation bar in `AppNavbar.vue` (`T002`).
2. Remove desktop left sidebar from `DocumentsView.vue` (`T003`, `T004`).
3. Add full light/dark theme parity to `DragDropZone.vue` (`T005`) and `DocumentGrid.vue` (`T006`, `T007`).
4. Validate with `npm run build` and responsive visual checks (`T008`, `T009`).
