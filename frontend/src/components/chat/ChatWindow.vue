<template>
  <div class="flex-1 flex flex-col h-full bg-gray-50/40 dark:bg-gray-950 overflow-hidden">
    <!-- Stream Message Container -->
    <div
      ref="scrollContainer"
      class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6"
    >
      <div class="max-w-3xl mx-auto space-y-6">
        <!-- Empty State -->
        <div
          v-if="messages.length === 0 && !streamingContent"
          class="min-h-[420px] flex flex-col items-center justify-center text-center p-8 border border-dashed border-gray-200 dark:border-gray-800 rounded-3xl bg-white/50 dark:bg-gray-900/40 backdrop-blur-xs"
        >
          <div class="w-14 h-14 rounded-2xl bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4 shadow-inner">
            <Sparkles class="w-7 h-7" />
          </div>
          <h3 class="font-bold text-lg text-gray-900 dark:text-gray-100 tracking-tight">Document Reference Assistant</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2 max-w-sm leading-relaxed">
            Ask any question regarding your uploaded documents. Answers are derived strictly from your files with interactive citations.
          </p>
        </div>

        <!-- Messages List -->
        <MessageBubble
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
        />

        <!-- Streaming Assistant Bubble -->
        <div v-if="streamingContent" class="flex gap-3.5 max-w-3xl w-full mr-auto">
          <div class="w-8 h-8 rounded-xl bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-400 border border-gray-200/80 dark:border-gray-700 shrink-0 flex items-center justify-center text-xs font-semibold shadow-xs">
            <Bot class="w-4 h-4" />
          </div>
          <div class="rounded-2xl rounded-tl-none px-5 py-4 text-sm bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 border border-gray-200/80 dark:border-gray-800 shadow-sm leading-relaxed space-y-2 flex-1 max-w-[85%]">
            <div class="whitespace-pre-wrap font-sans text-sm leading-relaxed">
              {{ streamingContent }}
              <span class="inline-block w-1.5 h-4 bg-indigo-500 animate-pulse ml-0.5 align-middle rounded-xs"></span>
            </div>
          </div>
        </div>

        <!-- Live Status indicator -->
        <div v-if="statusMessage" class="flex items-center justify-center gap-2 text-xs font-medium text-indigo-600 dark:text-indigo-400 py-1">
          <Loader2 class="w-3.5 h-3.5 animate-spin" />
          <span>{{ statusMessage }}</span>
        </div>
      </div>
    </div>

    <!-- Chat Input Bar (Aligned with max-w-3xl reading area) -->
    <div class="p-4 border-t border-gray-200/80 dark:border-gray-800 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md">
      <div class="max-w-3xl mx-auto">
        <form @submit.prevent="handleSubmit" class="relative flex items-center">
          <input
            v-model="inputQuery"
            type="text"
            placeholder="Ask a question about your uploaded documents..."
            :disabled="isStreaming || !isConnected"
            class="w-full pl-4 pr-24 py-3.5 rounded-2xl border border-gray-200 dark:border-gray-700/80 bg-gray-50/90 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/80 focus:bg-white dark:focus:bg-gray-800/90 shadow-inner transition-all disabled:opacity-60"
          />
          <button
            type="submit"
            :disabled="!inputQuery.trim() || isStreaming || !isConnected"
            class="absolute right-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs flex items-center justify-center gap-1.5 shadow-sm transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed active:scale-95"
          >
            <Send class="w-3.5 h-3.5" />
            <span>Ask</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Sparkles, Bot, Send, Loader2 } from 'lucide-vue-next'
import MessageBubble from './MessageBubble.vue'
import { useAutoScroll } from '../../composables/useAutoScroll'
import type { Message } from '../../services/chatService'

const props = defineProps<{
  messages: Message[]
  streamingContent: string
  statusMessage: string
  isStreaming: boolean
  isConnected: boolean
}>()

const emit = defineEmits<{
  (e: 'sendQuery', query: string): void
}>()

const scrollContainer = ref<HTMLElement | null>(null)
const { scrollToBottom } = useAutoScroll(scrollContainer)

const inputQuery = ref('')

const handleSubmit = () => {
  const text = inputQuery.value.trim()
  if (!text || props.isStreaming || !props.isConnected) return
  emit('sendQuery', text)
  inputQuery.value = ''
  scrollToBottom(true)
}

// Auto-scroll when messages or tokens arrive
watch(
  () => [props.messages.length, props.streamingContent],
  () => {
    scrollToBottom()
  },
  { deep: true }
)
</script>
