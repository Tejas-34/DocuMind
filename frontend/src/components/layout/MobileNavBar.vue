<template>
  <nav
    v-if="authStore.isAuthenticated"
    class="fixed bottom-0 left-0 right-0 z-40 h-16 bg-white/95 dark:bg-[#0d1410]/95 backdrop-blur-md border-t border-gray-100 dark:border-gray-800 flex md:hidden items-center justify-around px-4 pb-safe transition-colors duration-200 shadow-lg"
    aria-label="Mobile Navigation"
  >
    <!-- Documents Tab -->
    <RouterLink
      to="/documents"
      class="flex flex-col items-center justify-center gap-1 flex-1 py-2 text-[11px] font-medium transition-colors"
      :class="
        $route.path.startsWith('/documents')
          ? 'text-[#153826] dark:text-emerald-400 font-bold'
          : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
      "
      :aria-current="$route.path.startsWith('/documents') ? 'page' : undefined"
    >
      <FolderClosed class="w-5 h-5 transition-transform active:scale-95" />
      <span>Documents</span>
    </RouterLink>

    <!-- AI Chat Tab -->
    <RouterLink
      to="/chat"
      class="flex flex-col items-center justify-center gap-1 flex-1 py-2 text-[11px] font-medium transition-colors"
      :class="
        $route.path.startsWith('/chat')
          ? 'text-[#153826] dark:text-emerald-400 font-bold'
          : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
      "
      :aria-current="$route.path.startsWith('/chat') ? 'page' : undefined"
    >
      <MessageSquare class="w-5 h-5 transition-transform active:scale-95" />
      <span>AI Chat</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { FolderClosed, MessageSquare } from 'lucide-vue-next'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
</script>
