<template>
  <div class="flex-1 flex flex-col h-full bg-[#fcfdfc] dark:bg-[#0d1410] overflow-hidden transition-colors duration-200">
    <!-- Stream Message Container -->
    <div
      ref="scrollContainer"
      class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6"
    >
      <div class="max-w-3xl mx-auto space-y-6">
        <!-- Empty State with 4 Suggestion Chips -->
        <div
          v-if="messages.length === 0 && !streamingContent"
          class="min-h-[460px] flex flex-col items-center justify-center text-center p-6 sm:p-10 space-y-6"
        >
          <!-- Center Icon -->
          <div class="w-14 h-14 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-100 dark:border-emerald-900/40 text-[#153826] dark:text-emerald-400 flex items-center justify-center shadow-xs">
            <Sparkles class="w-7 h-7" />
          </div>

          <!-- Title & Subtitle -->
          <div class="space-y-2 max-w-md">
            <h3 class="font-bold text-xl sm:text-2xl text-[#153826] dark:text-emerald-400 tracking-tight">
              Document Reference Assistant
            </h3>
            <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
              Ask any question about your uploaded documents. Answers are grounded strictly in your files with interactive citations.
            </p>
          </div>

          <!-- Suggestion Chips Section -->
          <div class="w-full max-w-lg space-y-3 pt-2">
            <span class="text-xs text-gray-400 dark:text-gray-500 font-medium">Try asking:</span>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <!-- Chip 1 -->
              <button
                type="button"
                @click="handleSelectChip('Summarize the key points of the uploaded documents.')"
                class="flex items-center gap-2.5 px-3.5 py-3 rounded-2xl bg-white dark:bg-[#121915] border border-gray-200/80 dark:border-gray-800 hover:border-emerald-300 dark:hover:border-emerald-700/60 hover:bg-emerald-50/40 dark:hover:bg-emerald-950/30 text-xs font-medium text-gray-700 dark:text-gray-300 shadow-2xs transition-all text-left group cursor-pointer"
              >
                <FileText class="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 group-hover:scale-110 transition-transform" />
                <span class="truncate">Summarize the key points</span>
              </button>

              <!-- Chip 2 -->
              <button
                type="button"
                @click="handleSelectChip('What are the main topics covered in the uploaded documents?')"
                class="flex items-center gap-2.5 px-3.5 py-3 rounded-2xl bg-white dark:bg-[#121915] border border-gray-200/80 dark:border-gray-800 hover:border-emerald-300 dark:hover:border-emerald-700/60 hover:bg-emerald-50/40 dark:hover:bg-emerald-950/30 text-xs font-medium text-gray-700 dark:text-gray-300 shadow-2xs transition-all text-left group cursor-pointer"
              >
                <Sparkles class="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 group-hover:scale-110 transition-transform" />
                <span class="truncate">What are the main topics?</span>
              </button>

              <!-- Chip 3 -->
              <button
                type="button"
                @click="handleSelectChip('Find key terms and definitions in the documents.')"
                class="flex items-center gap-2.5 px-3.5 py-3 rounded-2xl bg-white dark:bg-[#121915] border border-gray-200/80 dark:border-gray-800 hover:border-emerald-300 dark:hover:border-emerald-700/60 hover:bg-emerald-50/40 dark:hover:bg-emerald-950/30 text-xs font-medium text-gray-700 dark:text-gray-300 shadow-2xs transition-all text-left group cursor-pointer"
              >
                <Search class="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 group-hover:scale-110 transition-transform" />
                <span class="truncate">Find terms related to...</span>
              </button>

              <!-- Chip 4 -->
              <button
                type="button"
                @click="handleSelectChip('List all important dates and deadlines mentioned in the files.')"
                class="flex items-center gap-2.5 px-3.5 py-3 rounded-2xl bg-white dark:bg-[#121915] border border-gray-200/80 dark:border-gray-800 hover:border-emerald-300 dark:hover:border-emerald-700/60 hover:bg-emerald-50/40 dark:hover:bg-emerald-950/30 text-xs font-medium text-gray-700 dark:text-gray-300 shadow-2xs transition-all text-left group cursor-pointer"
              >
                <Calendar class="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 group-hover:scale-110 transition-transform" />
                <span class="truncate">List important dates</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Messages List -->
        <MessageBubble
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
        />

        <!-- Clean Streaming Assistant Output (No logo, no background box) -->
        <div v-if="streamingContent" class="w-full max-w-3xl mx-auto py-1">
          <div class="prose prose-slate dark:prose-invert max-w-none text-gray-900 dark:text-gray-100 text-[15px] sm:text-base leading-relaxed prose-p:my-2.5 prose-p:leading-relaxed prose-headings:font-semibold prose-strong:font-semibold prose-code:text-[#153826] dark:prose-code:text-emerald-300 prose-code:bg-gray-100 dark:prose-code:bg-gray-800/80 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none">
            <div v-html="renderedStreamingMarkdown" class="inline"></div>
            <span class="inline-block w-1.5 h-4 bg-gray-500 dark:bg-gray-300 animate-pulse ml-0.5 align-middle"></span>
          </div>
        </div>

        <!-- Live Status indicator -->
        <div v-if="statusMessage" class="flex items-center justify-center gap-2 text-xs font-medium text-[#153826] dark:text-emerald-400 py-1">
          <Loader2 class="w-3.5 h-3.5 animate-spin" />
          <span>{{ statusMessage }}</span>
        </div>
      </div>
    </div>

    <!-- Floating Chat Input Bar -->
    <div class="p-4 sm:p-6 bg-transparent">
      <div class="max-w-3xl mx-auto">
        <form
          @submit.prevent="handleSubmit"
          class="relative flex items-center bg-white dark:bg-[#121915] rounded-2xl sm:rounded-3xl shadow-chat-input border border-gray-100 dark:border-gray-800/80 p-1.5 sm:p-2 transition-all focus-within:ring-2 focus-within:ring-[#153826] dark:focus-within:ring-emerald-500"
        >
          <div class="pl-3 pr-2 text-gray-400">
            <Paperclip class="w-4 h-4" />
          </div>
          <input
            v-model="inputQuery"
            type="text"
            placeholder="Ask a question about your uploaded documents..."
            :disabled="isStreaming || !isConnected"
            class="w-full py-2.5 pr-24 bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-400 text-xs sm:text-sm focus:outline-none disabled:opacity-60"
          />
          <button
            type="submit"
            :disabled="!inputQuery.trim() || isStreaming || !isConnected"
            class="absolute right-2 px-4 py-2 rounded-xl bg-[#153826] hover:bg-[#1b4932] text-white font-medium text-xs flex items-center justify-center gap-1.5 shadow-xs transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed active:scale-95 cursor-pointer"
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
import { ref, watch, computed } from 'vue'
import { Sparkles, Send, Loader2, FileText, Search, Calendar, Paperclip } from 'lucide-vue-next'
import { marked } from 'marked'
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

const renderedStreamingMarkdown = computed(() => {
  if (!props.streamingContent) return ''
  return marked.parse(props.streamingContent) as string
})

const handleSubmit = () => {
  const text = inputQuery.value.trim()
  if (!text || props.isStreaming || !props.isConnected) return
  emit('sendQuery', text)
  inputQuery.value = ''
  scrollToBottom(true)
}

const handleSelectChip = (chipPrompt: string) => {
  if (props.isStreaming || !props.isConnected) return
  emit('sendQuery', chipPrompt)
  scrollToBottom(true)
}

watch(
  () => [props.messages.length, props.streamingContent],
  () => {
    scrollToBottom()
  },
  { deep: true }
)
</script>
