<template>
  <aside
    class="w-80 border-r border-gray-200/80 dark:border-gray-800 bg-white dark:bg-gray-900 flex flex-col h-full shrink-0 select-none transition-colors duration-200"
  >
    <!-- Top Action Area: New Chat & Clear Context -->
    <div class="p-4 border-b border-gray-100 dark:border-gray-800/80 space-y-2.5">
      <button
        @click="$emit('newChat')"
        class="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-medium shadow-sm shadow-indigo-500/10 transition-all duration-150 active:scale-[0.99]"
      >
        <Plus class="w-4 h-4" />
        <span>New Chat Session</span>
      </button>

      <button
        v-if="activeSessionId"
        @click="$emit('clearContext')"
        class="w-full flex items-center justify-center gap-2 px-3 py-1.5 bg-gray-50 hover:bg-gray-100 dark:bg-gray-800/60 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-300 rounded-lg text-xs font-medium border border-gray-200/60 dark:border-gray-700/60 transition-colors"
        title="Reset conversational context memory for the current thread"
      >
        <Eraser class="w-3.5 h-3.5 text-amber-500" />
        <span>Clear Current Context</span>
      </button>
    </div>

    <!-- History Header -->
    <div class="px-4 pt-3 pb-1 flex items-center justify-between">
      <span class="text-[11px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
        Conversation Threads
      </span>
      <span class="text-[11px] text-gray-400 dark:text-gray-600 font-mono">
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
        class="group relative flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer text-xs font-medium transition-all duration-150"
        :class="
          session.id === activeSessionId
            ? 'bg-indigo-50 dark:bg-indigo-950/70 text-indigo-700 dark:text-indigo-300 font-semibold border border-indigo-200/50 dark:border-indigo-800/50 shadow-xs'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/80 dark:hover:bg-gray-800/60 border border-transparent'
        "
      >
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          <MessageSquare
            class="w-3.5 h-3.5 shrink-0 transition-colors"
            :class="session.id === activeSessionId ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'"
          />
          <span class="truncate" :title="session.title">{{ session.title }}</span>
        </div>

        <div class="hidden group-hover:flex items-center gap-1 shrink-0 ml-1.5">
          <button
            @click.stop="$emit('renameSession', session)"
            class="p-1 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-300 rounded hover:bg-white dark:hover:bg-gray-700 transition-colors"
            title="Rename session"
          >
            <Edit2 class="w-3 h-3" />
          </button>
          <button
            @click.stop="$emit('deleteSession', session)"
            class="p-1 text-gray-400 hover:text-rose-600 dark:hover:text-rose-400 rounded hover:bg-white dark:hover:bg-gray-700 transition-colors"
            title="Delete session"
          >
            <Trash2 class="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>

    <!-- Persistent Footer Sandbox Notice -->
    <div class="p-3.5 border-t border-gray-100 dark:border-gray-800/80 bg-gray-50/50 dark:bg-gray-900/60 text-xs">
      <div class="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 font-medium text-[11px] mb-1">
        <ShieldCheck class="w-3.5 h-3.5 text-emerald-500" />
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
