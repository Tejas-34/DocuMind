<template>
  <header
    class="h-16 border-b border-gray-200/80 dark:border-gray-800 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md sticky top-0 z-40 flex items-center justify-between px-4 sm:px-8 transition-colors duration-200"
  >
    <!-- Left: Brand Logo & Muted Tenant Badge -->
    <div class="flex items-center gap-3 shrink-0">
      <RouterLink to="/" class="flex items-center gap-2.5 group">
        <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-500/20 group-hover:bg-indigo-700 transition-colors">
          <Bot class="w-5 h-5 text-white" />
        </div>
        <span class="font-bold text-lg text-gray-900 dark:text-white tracking-tight">DocuMind</span>
      </RouterLink>

      <!-- Subtle Muted Gray Outline Badge -->
      <span
        class="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-800 bg-gray-50/80 dark:bg-gray-800/40"
      >
        <ShieldCheck class="w-3 h-3 text-gray-400 dark:text-gray-500" />
        <span>Tenant Isolated</span>
      </span>
    </div>

    <!-- Center: Primary Top Navigation (only when authenticated) -->
    <nav
      v-if="authStore.isAuthenticated"
      class="flex items-center gap-1.5 p-1 rounded-xl bg-gray-100/80 dark:bg-gray-800/60 border border-gray-200/60 dark:border-gray-700/60"
    >
      <RouterLink
        to="/documents"
        class="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-150"
        :class="
          $route.path.startsWith('/documents')
            ? 'bg-white dark:bg-gray-900 text-indigo-600 dark:text-indigo-400 font-semibold shadow-xs'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white/50 dark:hover:bg-gray-700/40'
        "
      >
        <FolderClosed class="w-3.5 h-3.5" />
        <span>Document Workspace</span>
      </RouterLink>

      <RouterLink
        to="/chat"
        class="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-150"
        :class="
          $route.path.startsWith('/chat')
            ? 'bg-white dark:bg-gray-900 text-indigo-600 dark:text-indigo-400 font-semibold shadow-xs'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white/50 dark:hover:bg-gray-700/40'
        "
      >
        <MessageSquare class="w-3.5 h-3.5" />
        <span>AI Document Q&A</span>
      </RouterLink>
    </nav>

    <!-- Right: Theme Toggle, User Profile & Actions -->
    <div class="flex items-center gap-2 sm:gap-4 shrink-0">
      <ThemeToggle />

      <template v-if="authStore.isAuthenticated">
        <div class="hidden sm:flex items-center gap-2 pl-2 border-l border-gray-200 dark:border-gray-800">
          <div class="w-8 h-8 rounded-full bg-indigo-50 dark:bg-indigo-950/80 border border-indigo-200/60 dark:border-indigo-800/60 flex items-center justify-center text-xs font-bold text-indigo-600 dark:text-indigo-400">
            {{ authStore.user?.email.charAt(0).toUpperCase() }}
          </div>
          <span class="text-xs text-gray-600 dark:text-gray-300 max-w-[140px] truncate font-medium">
            {{ authStore.user?.email }}
          </span>
        </div>

        <button
          @click="handleLogout"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition-colors"
          title="Sign out"
        >
          <LogOut class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">Logout</span>
        </button>
      </template>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Bot, LogOut, FolderClosed, MessageSquare, ShieldCheck } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import ThemeToggle from '../common/ThemeToggle.vue'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
