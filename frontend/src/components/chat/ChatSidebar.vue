<template>
  <aside
    class="w-80 border-r border-gray-100 dark:border-gray-800 bg-white dark:bg-[#0f1713] flex flex-col h-full shrink-0 select-none transition-colors duration-200"
  >
    <!-- Top Action Area: New Chat & Clear Context -->
    <div class="p-4 border-b border-gray-100 dark:border-gray-800/80 space-y-2">
      <button
        @click="$emit('newChat')"
        class="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[#153826] hover:bg-[#1b4932] text-white rounded-xl text-xs font-semibold shadow-xs transition-all duration-150 active:scale-[0.99] cursor-pointer"
      >
        <Plus class="w-4 h-4" />
        <span>New Chat Session</span>
      </button>

      <button
        v-if="activeSessionId"
        @click="$emit('clearContext')"
        class="w-full flex items-center justify-center gap-2 px-3 py-2 bg-amber-50/60 hover:bg-amber-100/60 dark:bg-amber-950/20 dark:hover:bg-amber-950/40 text-amber-700 dark:text-amber-400 rounded-xl text-xs font-medium border border-amber-200/50 dark:border-amber-900/40 transition-colors cursor-pointer"
        title="Reset conversational context memory for the current thread"
      >
        <Eraser class="w-3.5 h-3.5 text-amber-500" />
        <span>Clear Current Context</span>
      </button>
    </div>

    <!-- History Header -->
    <div class="px-4 pt-4 pb-1.5 flex items-center justify-between">
      <span class="text-[10px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
        Conversation Threads
      </span>
      <span class="text-[10px] text-gray-500 dark:text-gray-400 font-mono bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">
        {{ sessions.length }}
      </span>
    </div>

    <!-- Sessions List -->
    <div class="flex-1 overflow-y-auto p-3 space-y-1.5 scrollbar-thin">
      <div v-if="sessions.length === 0" class="p-6 text-center text-xs text-gray-400">
        <MessageSquare class="w-8 h-8 mx-auto mb-2 opacity-30" />
        <p>No chat history yet.</p>
        <p class="text-[11px] text-gray-400 mt-0.5">Start a new session to query your files.</p>
      </div>

      <div
        v-for="session in sessions"
        :key="session.id"
        @click="$emit('selectSession', session.id)"
        class="group relative flex items-center justify-between px-3.5 py-2.5 rounded-xl cursor-pointer text-xs font-medium transition-all duration-150"
        :class="
          session.id === activeSessionId
            ? 'bg-emerald-50/80 dark:bg-emerald-950/40 text-[#153826] dark:text-emerald-300 font-semibold border border-emerald-100/80 dark:border-emerald-900/40 shadow-2xs'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/40 border border-transparent'
        "
      >
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          <MessageSquare
            class="w-3.5 h-3.5 shrink-0 transition-colors"
            :class="session.id === activeSessionId ? 'text-[#153826] dark:text-emerald-400' : 'text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'"
          />
          <span class="truncate" :title="session.title">{{ session.title }}</span>
        </div>

        <!-- Action buttons: only visible on hover / focus-within -->
        <div class="opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity duration-150 flex items-center gap-1 shrink-0 ml-1.5">
          <button
            @click.stop="$emit('renameSession', session)"
            class="p-1 text-gray-400 hover:text-[#153826] dark:hover:text-emerald-300 rounded hover:bg-white dark:hover:bg-gray-700 transition-colors"
            title="Rename session"
          >
            <Edit2 class="w-3.5 h-3.5" />
          </button>
          <button
            @click.stop="$emit('deleteSession', session)"
            class="p-1 text-gray-400 hover:text-rose-600 dark:hover:text-rose-400 rounded hover:bg-white dark:hover:bg-gray-700 transition-colors"
            title="Delete session"
          >
            <Trash2 class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Persistent Footer Sandbox Notice -->
    <div class="p-3.5 m-3 rounded-2xl border border-gray-100 dark:border-gray-800/80 bg-gray-50/50 dark:bg-[#121915]/60 text-xs shadow-2xs">
      <div class="flex items-center gap-1.5 text-gray-800 dark:text-gray-200 font-semibold text-[11px] mb-1">
        <ShieldCheck class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
        <span>Strict Privacy Sandbox</span>
      </div>
      <p class="text-[10px] text-gray-400 dark:text-gray-500 leading-relaxed">
        All vector searches and chat threads are partitioned strictly by your user identity.
      </p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { Plus, Eraser, MessageSquare, Edit2, Trash2, ShieldCheck } from 'lucide-vue-next'
import type { ChatSession } from '../../services/chatService'

defineProps<{
  sessions: ChatSession[]
  activeSessionId: string | null
}>()

defineEmits<{
  (e: 'newChat'): void
  (e: 'selectSession', id: string): void
  (e: 'renameSession', session: ChatSession): void
  (e: 'deleteSession', session: ChatSession): void
  (e: 'clearContext'): void
}>()
</script>
