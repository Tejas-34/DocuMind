# Feature Specification: UI Styling & Visual Polish

**Feature Branch**: `002-ui-styling-polish`

**Created**: 2026-08-28

**Status**: Draft

**Input**: User description: "Update the UI styling for the Login, Signup, Document Workspace, and AI Chat views to match the provided high-fidelity reference designs. The objective is purely visual polish. Critical constraints: Zero Logic Changes: Strictly preserve all state management, API calls, props, and event handlers. Mobile Responsiveness: Implement fluid scaling, horizontal scroll for tables on small screens, and a collapsible sidebar (hamburger menu) for the chat view. Dark Mode: Implement comprehensive dark: classes for all new visual elements (soft shadows, floating containers, tinted dropzones) to maintain a premium aesthetic across themes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Premium Authentication Views (Login & Signup) (Priority: P1)

As a returning or new user navigating to the authentication pages, I want to experience a polished, modern, and visually balanced interface with refined form elements, smooth focus transitions, floating card elevation, and clear contrast in both light and dark themes so that signing in or registering feels secure and seamless.

**Why this priority**: First impressions directly influence trust and perceived system security. Auth pages are the entry gateway for every user.

**Independent Test**: Can be tested independently by navigating to `/login` and `/register` in various screen sizes and themes, checking visual alignment, form field focus states, card elevation, button states, and error alerts without altering auth submission logic.

**Acceptance Scenarios**:

1. **Given** a user on the Login or Signup view in light or dark mode, **When** viewing the card container, **Then** the card displays soft, modern elevation shadows, rounded corners, subtle translucent borders, and clean brand accent styling.
2. **Given** a user interacting with input fields (email, password), **When** an input receives focus, **Then** a visible, polished highlight ring and accent border are applied smoothly without shifting layout.
3. **Given** an authentication error response (e.g., invalid credentials), **When** the error banner is displayed, **Then** it renders with a tinted soft background, subtle border, and high-contrast readable typography matching the active theme.
4. **Given** a user submitting credentials, **When** the submit button enters loading state, **Then** the button maintains its visual dimensions with a spinning loader and accessible disabled styling.

---

### User Story 2 - Modern & Responsive Document Workspace (Priority: P1)

As an authenticated user managing my private document library, I want a clean, floating workspace layout with an intuitive tinted dropzone, clear upload feedback, and a fully responsive document table with horizontal scrolling on smaller screens so that I can manage my files comfortably on any device.

**Why this priority**: The document workspace is the central repository where users organize their data. A clear visual hierarchy and responsive table are essential for file management.

**Independent Test**: Can be tested independently by viewing the Document Workspace on desktop (1280px+), tablet (768px), and mobile (375px) viewports, verifying dropzone hover/drag states, file list table scrolling, metadata badge clarity, and modal styling.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the Document Workspace, **When** dragging files over the upload dropzone, **Then** the zone smoothly transitions to an active tinted highlight state with elevated borders and clear drop indicators.
2. **Given** a user viewing the document library on mobile/tablet viewports, **When** the screen width is insufficient to display all columns, **Then** the document table gracefully supports horizontal scrolling with smooth touch deceleration, while maintaining sticky header and action readability.
3. **Given** documents with varying statuses (Ready, Processing, Failed), **When** rendering status badges, **Then** each status displays a distinct, high-contrast, theme-aware badge with soft background tinting and iconography.
4. **Given** a user opening the Document Details or Delete confirmation modal, **When** the modal appears, **Then** it renders centered with a darkened, blurred backdrop, smooth entrance scaling, and styled action buttons.

---

### User Story 3 - Responsive AI Chat Experience with Mobile Drawer (Priority: P1)

As an authenticated user querying my documents on mobile or desktop, I want a streamlined chat interface featuring a collapsible conversation history drawer (accessible via a mobile hamburger menu), polished message bubbles with distinct user vs. assistant styling, clean markdown typography, and interactive citation badges so that conversational research is effortless on all screens.

**Why this priority**: AI Chat is the core product feature. Chatting on mobile requires collapsible navigation to maximize message readability while preserving rapid session switching.

**Independent Test**: Can be tested independently by opening the Chat View on mobile viewports (<768px), toggling the hamburger menu to open/close the conversation sidebar overlay, sending questions, and inspecting streaming bubbles and citation pills.

**Acceptance Scenarios**:

1. **Given** a user on a mobile viewport (<768px) in the Chat View, **When** viewing the interface, **Then** the chat sidebar is hidden by default and a hamburger menu button is prominently available in the top bar.
2. **Given** the mobile chat view, **When** the user taps the hamburger menu button, **Then** the conversation sidebar slides in smoothly as a modal drawer with an overlay backdrop, allowing thread selection, new session creation, or thread renaming/deletion.
3. **Given** an open mobile conversation drawer, **When** the user taps outside the drawer or selects a thread, **Then** the drawer closes smoothly and returns focus to the active chat stream.
4. **Given** an active chat stream on desktop or mobile, **When** user and assistant messages appear, **Then** user messages display high-contrast accent bubble styling while assistant messages display floating card styling with formatted markdown prose and interactive citation pills.
5. **Given** a user typing into the chat input bar, **When** viewing the input container, **Then** it remains pinned to the bottom of the viewport with a floating frosted glass backdrop effect, subtle elevation, and responsive padding.

---

### User Story 4 - Comprehensive Dark Mode Aesthetic (Priority: P2)

As a user switching between light and dark themes, I want all components, floating cards, text hues, borders, dropzones, modals, and status badges to adapt with a unified dark color palette featuring deep tones, soft luminescence, and high legibility without harsh contrasts or unstyled white flashes.

**Why this priority**: Visual comfort across different ambient lighting conditions is a core expectation for modern desktop and mobile productivity tools.

**Independent Test**: Can be tested independently by toggling the theme switch across all 4 views (Login, Register, Workspace, Chat) and verifying that every element maintains correct dark background, text, border, and elevation classes.

**Acceptance Scenarios**:

1. **Given** any view in dark mode, **When** inspecting background surfaces, **Then** neutral slate/gray dark shades are applied with subtle border separation rather than harsh solid outlines.
2. **Given** empty state banners, drag-and-drop zones, and modals in dark mode, **When** rendered, **Then** containers use semi-transparent tinted dark layers with soft shadow elevation.
3. **Given** assistant markdown responses (headings, lists, bold text, code blocks) in dark mode, **When** rendered, **Then** syntax and prose maintain high legibility with inverted text colors and dark code containers.

---

### User Story 5 - Zero Logic Regression & Preservation (Priority: P1)

As an application user, I want all existing capabilities (form submission, document upload, real-time WebSocket streaming, session creation, citation interactions, theme toggling, error handling) to behave identically to their current functionality so that no functional regressions occur during the styling overhaul.

**Why this priority**: Visual polish must never break or modify the underlying data contracts, reactivity, or service layer.

**Independent Test**: Can be tested independently by running automated test suites or performing end-to-end user flows across authentication, document uploads, and streaming Q&A before and after visual updates.

**Acceptance Scenarios**:

1. **Given** the visual polish changes across all components, **When** testing user interactions, **Then** all Vue props, emits, store bindings, router transitions, and WebSocket event hooks remain completely intact and functional.
2. **Given** authentication or upload operations, **When** submitting data, **Then** existing payload formats, validation rules, and error states trigger exactly as previously implemented.

---

### Edge Cases

- **Ultra-Narrow Screen Widths (<360px)**: Ensure form padding, button label wrapping, and message bubble width dynamically adjust without overflowing viewport width or causing horizontal page jitter.
- **Large & Ultrawide Displays (>1920px)**: Ensure main container max-widths constrain readable content to balanced reading columns rather than stretching edge-to-edge.
- **Long Document Filenames & Thread Titles**: File names in the document table and conversation titles in the sidebar must truncate gracefully with ellipsis (`truncate`) while providing full title tooltips on hover.
- **Rapid Theme Switching**: Theme toggles must transition colors smoothly without flashing unstyled backgrounds or unformatted text blocks.
- **Mobile Soft Keyboard Pop-up**: When the mobile virtual keyboard opens on the Chat View, the chat input bar and message container must retain appropriate view height without hiding the latest messages.
- **Multi-Line & Code-Heavy Markdown Responses**: Assistant messages containing tables, code snippets, and nested lists must render cleanly within message bubbles without overflowing horizontal boundaries.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Auth Views)**: Login and Signup views MUST use a centered floating card layout with smooth elevation shadow, rounded corners (e.g. `rounded-2xl` / `rounded-3xl`), polished form inputs with clear focus rings, and theme-adaptive error banners.
- **FR-002 (Auth Responsiveness)**: Login and Signup forms MUST fluidly scale across mobile (<640px) and desktop screens, maintaining comfortable touch targets (minimum 44px height for interactive elements).
- **FR-003 (Document Workspace Layout)**: Document Workspace MUST feature a structured layout with a prominent header, action buttons, floating container cards, and responsive container max-width constraints.
- **FR-004 (Tinted Dropzone)**: The file drag-and-drop zone MUST provide distinct visual states for default, drag-over (tinted highlight, elevated border), uploading (animated progress indicator), and error states in both light and dark modes.
- **FR-005 (Responsive Document Table)**: The document library table MUST be housed within an overflow-x scroll container ensuring full column access on mobile devices with smooth horizontal swipe/scroll.
- **FR-006 (Document Status Badges)**: Status badges (Ready, Processing, Failed) MUST utilize theme-aware soft background fills, matching border accents, and clear typography.
- **FR-007 (Modals & Dialogs)**: All modals (Delete confirmation, Document Details, Rename Thread, Clear Context) MUST display centered with a backdrop blur overlay, smooth entrance animation, and high-contrast action buttons.
- **FR-008 (Collapsible Mobile Chat Sidebar)**: The AI Chat View MUST implement a responsive collapsible sidebar drawer with a mobile hamburger trigger button visible on screens narrower than `768px` (md breakpoint).
- **FR-009 (Mobile Chat Drawer Overlay)**: When opened on mobile, the chat sidebar MUST slide in over the main chat window with a darkened backdrop overlay that dismisses the drawer when tapped.
- **FR-010 (Desktop Chat Layout)**: On desktop viewports (`>=768px`), the chat sidebar MUST remain docked side-by-side with the main chat window.
- **FR-011 (Message Bubbles Styling)**: User message bubbles MUST be visually differentiated (e.g., solid brand accent fill with rounded corners and right alignment) from assistant message bubbles (floating card with subtle border and left alignment).
- **FR-012 (Markdown Prose & Citations)**: Assistant message bubbles MUST format markdown prose (headings, lists, code blocks, strong text) cleanly with appropriate spacing, and display source citations as compact pill badges.
- **FR-013 (Chat Input Bar)**: The chat input container MUST feature a pinned floating bar with subtle backdrop blur, rounded search/input styling, clear submit action button, and disabled states during streaming.
- **FR-014 (Comprehensive Dark Mode)**: All newly styled containers, surfaces, borders, shadows, and typography MUST include corresponding `dark:` classes for full theme parity.
- **FR-015 (Strict Zero-Logic Invariant)**: All component props, emitted events, Pinia store bindings, API calls, routing hooks, and WebSocket lifecycle logic MUST remain untouched.

### Key Entities *(include if feature involves data)*

- **Theme Mode**: Represents the active visual theme state (`light` | `dark`), persisted in local storage and applied via document root class.
- **Viewport Breakpoint**: Represents the responsive screen size state (`mobile` < 768px, `desktop` >= 768px), driving mobile drawer vs docked sidebar behavior and table horizontal scrolling.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of views (Login, Signup, Document Workspace, AI Chat, Modals, Navbar) render with consistent brand styling, soft elevation shadows, and rounded container aesthetics in both light and dark modes.
- **SC-002**: Mobile viewports (<768px) achieve full usability with 0 horizontal page-overflow bugs on main layouts and seamless drawer toggling for chat navigation.
- **SC-003**: Document library tables allow complete horizontal scrolling inspection on mobile screens without clipped action buttons or truncated columns.
- **SC-004**: Theme switching between light and dark modes occurs instantaneously with zero unstyled flashes or illegible text contrast issues.
- **SC-005**: 100% regression-free preservation of existing functional behavior, verified by successful authentication, document uploads, and real-time streaming chat interactions.

## Assumptions

- **Design System Tokens**: Modern Tailwind CSS utility classes (neutral slate/gray scales, brand indigo accents, rounded container radiuses, backdrop blur, ring focus states) will be utilized for styling execution.
- **Target Screen Sizes**: Primary support targets mobile phones (375px - 640px), tablets (641px - 1024px), laptops, and desktop displays (1025px - 1920px+).
- **Icons & Assets**: Existing `lucide-vue-next` icons (e.g., `Menu`, `X`, `Bot`, `Sparkles`, `UploadCloud`, `FileText`, `Send`) are used for new mobile controls (such as the hamburger menu and close buttons).
- **No Backend Changes**: All visual enhancements are strictly frontend presentation layers without modifying backend APIs, database schemas, or WebSocket protocols.
