# UI & Navigation Contracts: Mobile Tab Bar & Session Fallback

**Feature Branch**: `004-mobile-ux-session-upload` | **Date**: 2026-08-29

---

## 1. Mobile Bottom Tab Bar Component Contract (`MobileNavBar.vue`)

### Component Description
Fixed bottom tab bar displayed only on viewport widths < 768px (`flex md:hidden`) when user is authenticated.

### Props & Emits
- **Props**: None (reads reactive state from `useAuthStore` and `useRoute`).
- **Emits**: None.

### DOM & Tailwind Specification
```html
<nav
  v-if="authStore.isAuthenticated"
  class="fixed bottom-0 left-0 right-0 z-40 h-16 bg-white/95 dark:bg-[#0d1410]/95 backdrop-blur-md border-t border-gray-100 dark:border-gray-800 flex md:hidden items-center justify-around px-4 pb-safe transition-colors duration-200"
  aria-label="Mobile Navigation"
>
  <!-- Documents Tab -->
  <RouterLink
    to="/documents"
    class="flex flex-col items-center justify-center gap-1 flex-1 py-2 text-[11px] font-medium transition-colors"
    :class="
      $route.path.startsWith('/documents')
        ? 'text-[#153826] dark:text-emerald-400 font-semibold'
        : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
    "
    :aria-current="$route.path.startsWith('/documents') ? 'page' : undefined"
  >
    <FolderClosed class="w-5 h-5" />
    <span>Documents</span>
  </RouterLink>

  <!-- AI Chat Tab -->
  <RouterLink
    to="/chat"
    class="flex flex-col items-center justify-center gap-1 flex-1 py-2 text-[11px] font-medium transition-colors"
    :class="
      $route.path.startsWith('/chat')
        ? 'text-[#153826] dark:text-emerald-400 font-semibold'
        : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
    "
    :aria-current="$route.path.startsWith('/chat') ? 'page' : undefined"
  >
    <MessageSquare class="w-5 h-5" />
    <span>AI Chat</span>
  </RouterLink>
</nav>
```

---

## 2. Session Fallback Contract (`ChatView.vue`)

### Router Redirection Contract
When a session is requested either during initial mount or route parameter change:

```typescript
const resolveSession = async (targetSessionId: string | null) => {
  if (!targetSessionId) {
    if (chatStore.sessions.length > 0) {
      await handleSelectSession(chatStore.sessions[0].id)
    } else {
      await handleNewChat()
    }
    return
  }

  const success = await chatStore.selectSession(targetSessionId)
  if (!success) {
    // Intercept 404 or missing session
    if (route.params.sessionId) {
      await router.replace('/chat')
    }
    if (chatStore.sessions.length > 0) {
      await handleSelectSession(chatStore.sessions[0].id)
    } else {
      await handleNewChat()
    }
  } else {
    // If route doesn't match loaded session, sync URL cleanly
    if (route.params.sessionId !== targetSessionId) {
      await router.replace(`/chat/${targetSessionId}`)
    }
    connectWebSocket(targetSessionId)
  }
}
```
