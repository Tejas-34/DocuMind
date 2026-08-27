<template>
  <aside
    class="w-64 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex flex-col justify-between h-[calc(100vh-4rem)] p-4 shrink-0"
  >
    <nav class="space-y-1.5">
      <RouterLink
        to="/documents"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors"
        :class="
          $route.path.startsWith('/documents')
            ? 'bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 font-semibold'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/60 hover:text-gray-900 dark:hover:text-gray-200'
        "
      >
        <FolderClosed class="w-4 h-4" />
        <span>Document Workspace</span>
      </RouterLink>

      <RouterLink
        to="/chat"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors"
        :class="
          $route.path.startsWith('/chat')
            ? 'bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 font-semibold'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/60 hover:text-gray-900 dark:hover:text-gray-200'
        "
      >
        <MessageSquare class="w-4 h-4" />
        <span>AI Document Q&A</span>
      </RouterLink>
    </nav>

    <div class="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-800 text-xs text-gray-500 dark:text-gray-400">
      <div class="flex items-center gap-1.5 font-medium text-gray-700 dark:text-gray-300 mb-1">
        <ShieldCheck class="w-4 h-4 text-emerald-500" />
        <span>Strict Privacy Sandbox</span>
      </div>
      <p class="text-[11px] leading-relaxed">
        All vector searches & chat histories are partitioned strictly by your user identity.
      </p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { FolderClosed, MessageSquare, ShieldCheck } from 'lucide-vue-next'
</script>
