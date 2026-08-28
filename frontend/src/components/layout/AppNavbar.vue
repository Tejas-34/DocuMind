<template>
  <header
    class="h-16 border-b border-gray-100 dark:border-gray-800 bg-white/90 dark:bg-[#0d1410]/90 backdrop-blur-md sticky top-0 z-40 flex items-center justify-between px-4 sm:px-8 transition-colors duration-200"
  >
    <!-- Left: Brand Logo & Tenant Pill -->
    <div class="flex items-center gap-3 shrink-0">
      <RouterLink to="/" class="flex items-center gap-2.5 group">
        <div class="w-8 h-8 rounded-xl bg-[#153826] flex items-center justify-center text-white shadow-xs group-hover:bg-[#1b4932] transition-colors">
          <!-- Lotus / Sparkles Flower Icon -->
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" v-if="false"/>
            <path d="M12 3c-1.5 3-4 5-8 6 3 2 5 5 5 9 1-4 3-6 7-7-3-2-4-5-4-8z"/>
          </svg>
        </div>
        <span class="font-bold text-base text-gray-900 dark:text-white tracking-tight">DocuMind</span>
      </RouterLink>

      <!-- Tenant Isolated Badge -->
      <span
        class="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium text-gray-500 dark:text-gray-400 border border-gray-200/80 dark:border-gray-800 bg-gray-50/60 dark:bg-gray-900/40"
      >
        <ShieldCheck class="w-3 h-3 text-gray-400 dark:text-gray-500" />
        <span>Tenant Isolated</span>
      </span>
    </div>

    <!-- Center: Tab Navigation (when authenticated) -->
    <nav
      v-if="authStore.isAuthenticated"
      class="hidden md:flex items-center gap-8 h-full"
    >
      <RouterLink
        to="/documents"
        class="flex items-center gap-2 h-full text-xs font-medium border-b-2 transition-all duration-150"
        :class="
          $route.path.startsWith('/documents')
            ? 'border-[#153826] text-gray-900 dark:text-white font-semibold'
            : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
        "
      >
        <FolderClosed class="w-3.5 h-3.5" />
        <span>Document Workspace</span>
      </RouterLink>

      <RouterLink
        to="/chat"
        class="flex items-center gap-2 h-full text-xs font-medium border-b-2 transition-all duration-150"
        :class="
          $route.path.startsWith('/chat')
            ? 'border-[#153826] text-gray-900 dark:text-white font-semibold'
            : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
        "
      >
        <MessageSquare class="w-3.5 h-3.5" />
        <span>AI Document Q&A</span>
      </RouterLink>
    </nav>

    <!-- Right: Theme Toggle, User Profile & Actions -->
    <div class="flex items-center gap-3 shrink-0">
      <ThemeToggle />

      <template v-if="authStore.isAuthenticated">
        <div class="flex items-center gap-2 pl-2 border-l border-gray-100 dark:border-gray-800">
          <div class="w-7 h-7 rounded-full bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex items-center justify-center text-xs font-bold text-gray-700 dark:text-gray-300">
            {{ userInitial }}
          </div>
          <span class="hidden sm:inline text-xs text-gray-700 dark:text-gray-300 max-w-[140px] truncate font-medium">
            {{ authStore.user?.email }}
          </span>
          <button
            @click="handleLogout"
            class="p-1.5 text-gray-400 hover:text-rose-600 dark:hover:text-rose-400 rounded-lg transition-colors"
            title="Sign out"
          >
            <LogOut class="w-3.5 h-3.5" />
          </button>
        </div>
      </template>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { LogOut, FolderClosed, MessageSquare, ShieldCheck } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import ThemeToggle from '../common/ThemeToggle.vue'

const authStore = useAuthStore()
const router = useRouter()

const userInitial = computed(() => {
  return authStore.user?.email ? authStore.user.email.charAt(0).toUpperCase() : 'U'
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
