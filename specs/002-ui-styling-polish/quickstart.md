# Quickstart & Visual Verification Guide: UI Styling & Visual Polish

**Feature**: UI Styling & Visual Polish (`002-ui-styling-polish`)
**Date**: 2026-08-28

---

## 1. Prerequisites & Dev Server Setup

1. Open a terminal in the project directory:
   ```bash
   cd frontend
   npm run dev
   ```
2. Open the application in your browser: `http://localhost:5173`

---

## 2. Visual Polish Verification Checklist

### A. Global Tokens & Theme System
- [ ] Inspect theme toggle (Sun/Moon icon in top right).
- [ ] Verify dark forest green primary buttons (`#153826`).
- [ ] Verify card corner radii (`rounded-[24px]` / `24px`).
- [ ] Verify diffuse ambient drop shadows (`shadow-xl shadow-black/5`).

### B. Authentication Views (`/login` and `/register`)
- [ ] **Desktop (>=1024px)**: Verify 2-column layout with left value-prop features and right floating card.
- [ ] **Mobile (<640px)**: Verify card scales fluidly with minimum 44px touch targets.
- [ ] **Input Adornments**: Verify leading `Mail` icon on email input and `Lock` icon + `Eye` toggle on password.
- [ ] **Form Submission**: Verify logging in navigates to `/documents` with active token.

### C. Document Workspace (`/documents`)
- [ ] **Top Navbar**: Verify "Document Workspace" active tab indicator (bottom green border).
- [ ] **Dropzone**: Verify soft dashed border, warm/greenish tint, and hover/drag highlight states.
- [ ] **Document Library Table**:
  - [ ] Headers are uppercase, smaller font, with wide tracking (`FILE NAME`, `DOCUMENT ID`, etc.).
  - [ ] Status badge displays active pulsating dot (`• Ready`).
  - [ ] PDF files display red PDF badge.
- [ ] **Mobile Viewport (<768px)**: Verify the document table scrolls horizontally without layout breaking.

### D. AI Chat View (`/chat`)
- [ ] **Top Navbar**: Verify "AI Document Q&A" active tab indicator.
- [ ] **Desktop Sidebar**: Verify `+ New Chat Session` (solid green) and `Clear Current Context` (subtle amber).
- [ ] **Mobile Sidebar (<768px)**:
  - [ ] Hamburger menu button appears in the mobile header.
  - [ ] Tapping hamburger opens the sidebar drawer with backdrop overlay.
  - [ ] Tapping outside or selecting a thread closes the drawer.
- [ ] **Empty State Suggestion Chips**:
  - [ ] Verify 4 chips in 2x2 grid (`Summarize the key points`, `What are the main topics?`, etc.).
  - [ ] Clicking any chip populates and triggers the query stream.
- [ ] **Chat Input Bar**:
  - [ ] Floating container with diffuse shadow and no heavy borders.
  - [ ] Green pill submit button (`Ask`).

---

## 3. Automated & Unit Validation Commands

```bash
# Run frontend build check to verify TypeScript and Vue template integrity
cd frontend
npm run build
```
