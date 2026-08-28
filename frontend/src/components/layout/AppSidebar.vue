<template>
  <aside
    class="w-64 border-r border-gray-100 dark:border-gray-800 bg-white dark:bg-[#0f1713] flex flex-col justify-between h-[calc(100vh-4rem)] p-4 shrink-0"
  >
    <nav class="space-y-1.5">
      <RouterLink
        to="/documents"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-colors"
        :class="
          $route.path.startsWith('/documents')
            ? 'bg-emerald-50/80 dark:bg-emerald-950/40 text-[#153826] dark:text-emerald-300 font-semibold'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/60 hover:text-gray-900 dark:hover:text-gray-200'
        "
      >
        <FolderClosed class="w-4 h-4" />
        <span>Document Workspace</span>
      </RouterLink>

      <RouterLink
        to="/chat"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-colors"
        :class="
          $route.path.startsWith('/chat')
            ? 'bg-emerald-50/80 dark:bg-emerald-950/40 text-[#153826] dark:text-emerald-300 font-semibold'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/60 hover:text-gray-900 dark:hover:text-gray-200'
        "
      >
        <MessageSquare class="w-4 h-4" />
        <span>AI Document Q&A</span>
      </RouterLink>
    </nav>

    <div class="p-3 bg-gray-50/50 dark:bg-[#121915]/60 rounded-2xl border border-gray-100 dark:border-gray-800 text-xs text-gray-500 dark:text-gray-400">
      <div class="flex items-center gap-1.5 font-medium text-gray-700 dark:text-gray-300 mb-1 text-[11px]">
        <ShieldCheck class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
        <span>Strict Privacy Sandbox</span>
      </div>
      <p class="text-[10px] leading-relaxed text-gray-400 dark:text-gray-500">
        All vector searches & chat histories are partitioned strictly by your user identity.
      </p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { FolderClosed, MessageSquare, ShieldCheck } from 'lucide-vue-next'
</script>
