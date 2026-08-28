<template>
  <div class="relative inline-block">
    <!-- Ultra-compact chip -->
    <button
      type="button"
      @click="isOpen = !isOpen"
      class="text-[11px] px-2.5 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200/80 dark:border-gray-700/80 cursor-pointer hover:border-emerald-300 dark:hover:border-emerald-700 hover:bg-emerald-50/50 dark:hover:bg-emerald-950/40 transition-colors inline-flex items-center gap-1.5 shadow-2xs group"
      :title="`View excerpt from ${citation.document_name}`"
    >
      <FileText class="w-3 h-3 text-gray-400 dark:text-gray-500 group-hover:text-[#153826] dark:group-hover:text-emerald-400 transition-colors shrink-0" />
      <span class="max-w-[140px] truncate font-medium">{{ citation.document_name }}</span>
      <span v-if="citation.page_number" class="text-[10px] text-gray-400 dark:text-gray-500 font-mono">
        p.{{ citation.page_number }}
      </span>
    </button>

    <!-- Source Snippet Micro-Popover -->
    <div
      v-if="isOpen"
      class="absolute left-0 bottom-full mb-2 z-30 w-72 sm:w-80 p-3 rounded-2xl bg-white dark:bg-[#121915] border border-gray-200/90 dark:border-gray-700 shadow-xl text-xs text-gray-700 dark:text-gray-200 animate-in fade-in zoom-in-95 duration-150"
    >
      <div class="flex items-center justify-between pb-1.5 mb-1.5 border-b border-gray-100 dark:border-gray-800 text-[11px] font-semibold text-gray-800 dark:text-gray-200">
        <div class="flex items-center gap-1.5 truncate">
          <FileText class="w-3.5 h-3.5 text-[#153826] dark:text-emerald-400 shrink-0" />
          <span class="truncate">{{ citation.document_name }}</span>
        </div>
        <span v-if="citation.page_number" class="shrink-0 text-gray-400 font-normal">
          Page {{ citation.page_number }}
        </span>
      </div>
      <p class="leading-relaxed text-[11px] text-gray-600 dark:text-gray-400 italic">
        "{{ citation.snippet || 'Referenced document excerpt.' }}"
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FileText } from 'lucide-vue-next'
import type { Citation } from '../../services/chatService'

defineProps<{
  citation: Citation
}>()

const isOpen = ref(false)
</script>
