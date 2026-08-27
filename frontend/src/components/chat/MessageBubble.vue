<template>
  <div
    class="flex gap-3.5 max-w-3xl w-full"
    :class="message.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'"
  >
    <!-- Avatar Icon -->
    <div
      class="w-8 h-8 rounded-xl shrink-0 flex items-center justify-center text-xs font-semibold shadow-xs"
      :class="
        message.role === 'user'
          ? 'bg-indigo-600 text-white shadow-indigo-500/20'
          : 'bg-white dark:bg-gray-800 text-emerald-600 dark:text-emerald-400 border border-gray-200/80 dark:border-gray-700 shadow-xs'
      "
    >
      <User v-if="message.role === 'user'" class="w-4 h-4" />
      <Bot v-else class="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
    </div>

    <!-- Bubble Body -->
    <div
      class="rounded-2xl text-sm leading-relaxed space-y-2.5 flex-1 max-w-[85%]"
      :class="
        message.role === 'user'
          ? 'bg-indigo-600 text-white rounded-tr-none px-5 py-3.5 shadow-sm ml-auto'
          : 'bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 rounded-tl-none px-5 py-4 border border-gray-200/80 dark:border-gray-800 shadow-sm mr-auto'
      "
    >
      <!-- Message Content -->
      <div class="whitespace-pre-wrap font-sans text-sm leading-relaxed">
        {{ message.content }}
      </div>

      <!-- Optimistic sending indicator -->
      <div v-if="message.isPending" class="flex items-center gap-1.5 text-xs text-indigo-200 animate-pulse pt-0.5">
        <Loader2 class="w-3 h-3 animate-spin" />
        <span>Sending query...</span>
      </div>

      <!-- Grounded Sources Collapsible Accordion -->
      <div
        v-if="message.citations && message.citations.length > 0"
        class="pt-3 mt-3 border-t border-gray-100 dark:border-gray-800/80"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="text-[11px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
            Grounded Sources ({{ message.citations.length }})
          </span>
        </div>

        <!-- Neatly stacked micro-cards -->
        <div class="space-y-1.5">
          <CitationPill
            v-for="(citation, idx) in message.citations"
            :key="idx"
            :citation="citation"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Bot, Loader2 } from 'lucide-vue-next'
import CitationPill from './CitationPill.vue'
import type { Message } from '../../services/chatService'

defineProps<{
  message: Message
}>()
</script>
