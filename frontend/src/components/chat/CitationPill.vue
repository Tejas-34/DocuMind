<template>
  <div class="w-full rounded-lg border border-gray-200/80 dark:border-gray-800 bg-gray-50/60 dark:bg-gray-850/60 hover:bg-gray-50 dark:hover:bg-gray-800 transition-all duration-150 overflow-hidden">
    <!-- Header toggle -->
    <button
      type="button"
      @click="isOpen = !isOpen"
      class="w-full flex items-center justify-between px-3 py-2 text-left text-xs font-medium text-gray-700 dark:text-gray-300 gap-2"
    >
      <div class="flex items-center gap-2 min-w-0 flex-1">
        <FileText class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
        <span class="truncate font-semibold text-gray-800 dark:text-gray-200" :title="citation.document_name">
          {{ citation.document_name }}
        </span>
        <span
          v-if="citation.page_number"
          class="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-mono bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 border border-indigo-200/50 dark:border-indigo-800/50"
        >
          Page {{ citation.page_number }}
        </span>
      </div>

      <ChevronDown
        class="w-3.5 h-3.5 text-gray-400 transition-transform duration-200 shrink-0"
        :class="{ 'rotate-180 text-indigo-500': isOpen }"
      />
    </button>

    <!-- Collapsible excerpt drawer -->
    <div
      v-if="isOpen"
      class="px-3 pb-2.5 pt-1 text-[11px] text-gray-600 dark:text-gray-400 border-t border-gray-100 dark:border-gray-800 bg-white/70 dark:bg-gray-900/70"
    >
      <div class="flex items-start gap-1.5 leading-relaxed font-serif italic pt-1">
        <Quote class="w-3 h-3 text-indigo-400 shrink-0 mt-0.5 not-italic" />
        <span>"{{ citation.snippet || 'Referenced document excerpt' }}"</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FileText, ChevronDown, Quote } from 'lucide-vue-next'
import type { Citation } from '../../services/chatService'

defineProps<{
  citation: Citation
}>()

const isOpen = ref(false)
</script>
