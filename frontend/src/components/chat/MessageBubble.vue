<template>
  <div class="w-full max-w-3xl mx-auto py-1">
    <!-- User Message Bubble (Right-aligned, soft pill container) -->
    <div
      v-if="message.role === 'user'"
      class="flex flex-col items-end"
    >
      <div
        class="rounded-3xl px-5 py-2.5 max-w-[85%] sm:max-w-[75%] bg-[#f0f4f9] dark:bg-[#282a2c] text-gray-900 dark:text-gray-100 text-[15px] leading-relaxed break-words"
      >
        <div class="whitespace-pre-wrap font-sans">
          {{ message.content }}
        </div>
      </div>

      <!-- Sending indicator -->
      <div v-if="message.isPending" class="flex items-center gap-1.5 text-xs text-gray-400 animate-pulse pt-1 pr-2">
        <Loader2 class="w-3 h-3 animate-spin" />
        <span>Sending...</span>
      </div>
    </div>

    <!-- AI Assistant Response (No logo, no background box, clean prose + copy button) -->
    <div
      v-else
      class="w-full text-left space-y-3"
    >
      <!-- Markdown Output -->
      <div
        class="prose prose-slate dark:prose-invert max-w-none text-gray-900 dark:text-gray-100 text-[15px] sm:text-base leading-relaxed prose-p:my-2.5 prose-p:leading-relaxed prose-headings:font-semibold prose-strong:font-semibold prose-code:text-[#153826] dark:prose-code:text-emerald-300 prose-code:bg-gray-100 dark:prose-code:bg-gray-800/80 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none"
        v-html="renderedMarkdown"
      ></div>

      <!-- Inline Source Citations (if any) -->
      <div
        v-if="message.citations && message.citations.length > 0"
        class="pt-1 flex flex-wrap items-center gap-1.5"
      >
        <span class="text-[10px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500 mr-1 select-none">
          Sources:
        </span>
        <CitationPill
          v-for="(citation, idx) in message.citations"
          :key="idx"
          :citation="citation"
        />
      </div>

      <!-- Action Bar: Only Copy Function -->
      <div class="flex items-center gap-2 pt-0.5">
        <button
          type="button"
          @click="copyResponse"
          class="p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800/70 rounded-lg transition-colors cursor-pointer inline-flex items-center gap-1.5 text-xs"
          :title="isCopied ? 'Copied to clipboard' : 'Copy response'"
        >
          <Check v-if="isCopied" class="w-4 h-4 text-emerald-500" />
          <Copy v-else class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Copy, Check, Loader2 } from 'lucide-vue-next'
import { marked } from 'marked'
import CitationPill from './CitationPill.vue'
import type { Message } from '../../services/chatService'

const props = defineProps<{
  message: Message
}>()

const isCopied = ref(false)

// Configure marked options for clean prose rendering
marked.setOptions({
  gfm: true,
  breaks: true,
})

const renderedMarkdown = computed(() => {
  if (!props.message.content) return ''
  return marked.parse(props.message.content) as string
})

const copyResponse = async () => {
  if (!props.message.content) return
  await navigator.clipboard.writeText(props.message.content)
  isCopied.value = true
  setTimeout(() => {
    isCopied.value = false
  }, 2000)
}
</script>
