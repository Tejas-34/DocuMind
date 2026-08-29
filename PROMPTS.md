# Prompt & Development Approach

## Development Approach

I developed DocuMind using a **spec-driven approach with Antigravity.**

check specs: [`specs`](./specs)

Instead of directly starting with implementation, I first worked on understanding the requirements, planning the architecture, breaking the work into smaller tasks, and then implementing them.

The general workflow was:

```text
/clarify
   ↓
/plan
   ↓
/task
   ↓
/implement
```

### Reference

[GitHub - Spec-Driven Development with AI](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)


## Phase 1 — Initial Project Understanding & Planning

### /clarify

>I need to build a secure, multi-tenant Document Q&A web application.
>
>**What we are building:**
>A platform where users can register, log in, upload text-heavy documents (like PDFs and plain text), and interact with an AI assistant to ask questions about the contents of those files. The application needs a dashboard to manage uploaded files, and a chat interface where users can create distinct, titled conversation threads. The AI must only answer questions based on the specific documents the user has uploaded, acting as a strict reference tool rather than a general chatbot.
>
>**Why we are building it:**
>To solve the problem of information retrieval across large personal or business documents without compromising data privacy. The absolute most critical business requirement is strict data isolation. A user must never be able to access, query, or receive AI answers derived from another user's documents or chat history. We are building this to provide a trustworthy, isolated environment where individuals can leverage AI to understand their own files rapidly and securely.
>
>**Key User Flows:**
>
>- User signs up and logs in.
>- User uploads a PDF, which is processed in the background.
>- User opens a new chat session and asks a question like "What does the contract say about termination?"
>- The system streams an answer back in real-time, sourced strictly from that user's uploaded documents.

---

### /plan

>I need a detailed technical implementation plan for a secure, multi-tenant Document Q&A web application. Please generate a step-by-step build plan strictly adhering to the following architectural decisions and constraints.
>
>**Core Architecture & Stack**
>
>- Backend: FastAPI (fully asynchronous).
>- Database: A single Postgres instance utilizing the `pgvector` extension for both relational and vector storage.
>- Frontend: Vue.js 3 with Pinia for state management.
>- AI/ML: Gemini API using the modern `google-genai` Python SDK (targeting `gemini-3.>5-flash` for speed). Use local `sentence-transformers` (`all-MiniLM-L6-v2`) for embeddings.
>
>**Data Isolation & Multi-Tenancy (Strict Constraint)**
>Use SQLAlchemy 2.0 (async) and Alembic for schema management. You must enforce strict multi-tenancy at the database query layer. Every operational table (`users`, `documents`, `chunks`, `chat_sessions`, `messages`) must include a `user_id` foreign key. Every single query—especially the `pgvector` cosine similarity search—must be filtered by the `user_id` extracted from the user's JWT.
>
>**Ingestion & Chunking Pipeline**
>Handle document uploads and text extraction. Chunk the text using `langchain-text-splitters` (`RecursiveCharacterTextSplitter`). Configure chunks for approximately 800 tokens with a 15% overlap to maintain semantic boundaries. Generate embeddings locally using the 384-dimensional `all-MiniLM-L6-v2` model to avoid network bottlenecks, storing them in the `chunks` table.
>
>**Chat & RAG Infrastructure**
>Implement the core chat functionality over FastAPI WebSockets for real-time token streaming. The WebSocket lifecycle should: receive the query, generate the local embedding, execute the `user_id`-scoped pgvector similarity search, assemble a strict anti-hallucination system prompt with the retrieved context, stream the Groq LLM response back to the client, and finally persist the interaction to the `messages` table.
>
>**Frontend Implementation**
>Create a Vue SPA with routing for authentication, a document management dashboard, and a chat interface. The chat interface must implement a native WebSocket client to handle incoming token streams and render optimistic UI updates. Use basic JWT attached to Axios/Fetch for protected API routes.
>
---

### /task

>Please break down the technical implementation plan for the multi-tenant Document Q&A application into a prioritized, actionable checklist of tasks. Group the tasks into logical phases (e.g., Environment Setup, Database & Models, Authentication, Document Processing, RAG & WebSockets, Frontend Integration). For each task, briefly specify the core requirement and highlight the critical constraints, particularly ensuring that every database interaction incorporates the `user_id` filter for strict data isolation. Include tasks for writing the system prompt, setting up the Vue.js dashboard, and implementing the optimistic UI updates in the chat interface.



## Phase 2 — UI/UX Improvements

### /plan

> I need to refine the UI/UX of our Vue.js frontend to make it look professional and production-ready.
>
> **CRITICAL CONSTRAINT:** The application currently works perfectly. You are strictly forbidden from modifying any underlying business logic, Pinia state stores, Axios API calls, or WebSocket event handlers. Do not alter data structures. This is purely a Tailwind CSS and Vue template layout update.
>
> Please implement the following UI improvements:
>
> **1. Layout & Global Polish**
>
> - **Navigation Restructure:** Remove the double-sidebar layout. Move the primary navigation ("Document Workspace" and "AI Document Q&A") to a sleek top navigation bar.
> - **Sidebar Dedication:** The left sidebar should now be entirely dedicated to the Chat Session history, giving it more breathing room.
> - **Header Clean-up:** Demote the "Tenant Isolated" badge next to the logo. Change it from a solid bright color to a subtle, muted gray outline, or move it to a persistent footer near the "Strict Privacy Sandbox" notice.
>
> **2. Chat Interface (Component)**
>
> - **Message Bubbles:** Create clear visual distinction. User messages should have a solid primary-theme background (e.g., purple/indigo) with white text. AI messages should have a clean white or very soft gray (`bg-gray-50`) background with a subtle drop shadow (`shadow-sm`).
> - **Input Alignment:** Ensure the message input box at the bottom perfectly aligns its `max-width` with the conversation container above it so it doesn't look narrower than the reading area.
> - **Grounded Sources:** Redesign the current row of blue source pills. Convert them into a discrete, collapsible accordion or neatly stacked micro-cards underneath the AI response to prevent visual clutter and awkward wrapping.
>
> **3. Document Management Table (Component)**
>
> - **Drag-and-Drop Zone:** Increase the vertical padding significantly to make it a clear focal point. Add an active drag state (e.g., the dashed border turns solid primary, and the background subtly dims when a file is hovered over it).
> - **Table Headers:** Make the typography professional. Use uppercase text, a smaller font size (e.g., `text-xs`), wider letter spacing (`tracking-wider`), and a muted gray text color.
> - **Table Rows:** Add interactive hover states (e.g., `hover:bg-gray-50` and a subtle cursor change) so the table feels responsive to mouse movements.
>
> Output only the updated Vue component files (`.vue`), focusing purely on the `<template>` and `<style>` blocks or Tailwind class changes within the templates.

---

### /task

**Prompt:**

> Please implement the following UI/CSS refinements to the Chat Interface in our Vue template.
>
> **CRITICAL CONSTRAINT:** Do not alter any underlying business logic, state management, or component data structures. This is strictly a Tailwind CSS and HTML structure update.
>
> **1. AI Response Typography (The Output Text)**
>
> - **Rich Text Styling:** The AI text currently looks like raw markdown or unstyled text. Wrap the AI response content in a `prose` container (if using Tailwind Typography) or apply classes like `text-gray-800 leading-relaxed text-sm` to make it highly legible.
> - **Spacing:** Ensure proper margin between paragraphs and lists so bullet points don't look cramped.
>
> **2. Ultra-Compact Grounded Sources**
>
> - **Chip Layout:** Remove the large, bulky vertical accordion rows. Transform the "Grounded Sources" into a compact, inline list of small chips/badges positioned at the very bottom of the AI bubble.
> - **Styling:** Use a `flex flex-wrap gap-2` container. Style the individual source chips to be tiny and unobtrusive: `text-[11px] px-2 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200 cursor-pointer hover:bg-slate-200 transition-colors`.
> - **Iconography:** Keep a very small document icon (like an SVG or FontAwesome icon) next to the filename inside the chip.
>
> **3. Color Palette & Canvas Contrast**
>
> - **Chat Canvas Background:** Change the main chat background (behind the message bubbles) to a very soft gray (e.g., `bg-slate-50` or `bg-gray-50/50`). This creates depth and allows the white AI message bubbles (`bg-white shadow-sm`) to stand out naturally.
> - **User Bubble Color:** The current user message blue/purple is quite intense. Soften it slightly to a more modern, premium shade (e.g., `bg-indigo-600` instead of a harsh blue) and ensure the text is pure white (`text-white`).
> - **Borders:** Soften the heavy border on the AI message container to a subtle `ring-1 ring-slate-900/5` or a very light `border-gray-100` so it doesn't look like a wireframe.

---


## Phase 3 — Error Handling & Mobile Improvements

### /plan

>Session Fallback (Vue Router): We will intercept the logic that loads a specific chat session. If the API returns a 404 Not Found (or if the session ID doesn't exist in the local Pinia store), Vue Router will programmatically push the user back to the base /chat view to start a fresh thread.
>
>Mobile Navigation (Tailwind UI): Since the desktop sidebars collapse or disappear on mobile, we will add a sticky mobile-only navigation bar (e.g., a bottom tab bar or a simplified top header). We'll use Tailwind's responsive classes (flex md:hidden) to ensure it only appears on small screens, allowing users to toggle between /documents and /chat.
>
>Mobile Upload Patch: Mobile browsers often assign generic application/octet-stream MIME types to PDFs or fail to trigger the @change event on hidden file inputs. We will ensure the Vue file input strictly accepts our required extensions and gracefully handles mobile-specific file objects before appending them to the FormData payload.

---

### /task

>Please implement the following three fixes in our Vue.js and FastAPI application. Do not alter the core RAG or embedding logic.
>
>1. Route Error Handling (Session Not Found):
>
>Update the Vue component or Pinia action responsible for fetching a specific chat session by ID.
>Wrap the API call in a try/catch block. If the backend returns a 404, use Vue Router (router.push('/chat')) to redirect the user to the default new chat state.
>
>2. Mobile Navigation Toggle:
>
>In the main application layout, implement a mobile-only navigation menu (e.g., a fixed bottom tab bar or header links) using Tailwind classes (block md:hidden).
>Include clear buttons/icons to route the user between the /documents (Document Workspace) and /chat (AI Assistant) views so they aren't trapped on one screen on mobile devices.





## About These Prompts

These are some of the major prompts I used during the development of DocuMind.

I did not track every prompt used during development. For smaller features, bug fixes, UI changes, and simple code changes, I usually used shorter prompts that did not require a full `/clarify`, `/plan`, and `/task` process.