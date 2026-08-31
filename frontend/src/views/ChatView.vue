<template>
  <div class="flex flex-col md:flex-row h-[calc(100vh-8rem)] md:h-[calc(100vh-4rem)] overflow-hidden relative">
    <!-- Mobile Top Bar with Hamburger Trigger -->
    <div class="md:hidden flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800 bg-white dark:bg-[#0f1713]">
      <button
        type="button"
        @click="isMobileSidebarOpen = true"
        class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-200/60 dark:border-gray-700 text-xs font-medium cursor-pointer"
      >
        <Menu class="w-4 h-4 text-[#153826] dark:text-emerald-400" />
        <span>Threads</span>
      </button>

      <span class="text-xs font-semibold text-gray-800 dark:text-gray-200 truncate max-w-[200px]">
        {{ chatStore.activeSession?.title || 'DocuMind AI' }}
      </span>

      <button
        type="button"
        @click="handleNewChat"
        class="p-1.5 rounded-xl bg-[#153826] text-white cursor-pointer"
        title="New Chat"
      >
        <Plus class="w-4 h-4" />
      </button>
    </div>

    <!-- Desktop Docked Sidebar -->
    <div class="hidden md:block h-full shrink-0">
      <ChatSidebar
        :sessions="chatStore.sessions"
        :activeSessionId="chatStore.activeSession?.id || null"
        @newChat="handleNewChat"
        @selectSession="handleSelectSession"
        @renameSession="openRenameModal"
        @deleteSession="handleDeleteSession"
        @clearContext="isClearContextModalOpen = true"
      />
    </div>

    <!-- Mobile Collapsible Sidebar Drawer with Overlay Backdrop -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="isMobileSidebarOpen"
          class="fixed inset-0 z-50 md:hidden bg-black/40 backdrop-blur-xs flex"
          @click.self="isMobileSidebarOpen = false"
        >
          <div class="w-80 max-w-[85vw] h-full bg-white dark:bg-[#0f1713] shadow-2xl flex flex-col transform transition-transform">
            <div class="p-3 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
              <span class="text-xs font-bold text-gray-900 dark:text-white pl-2">Conversation History</span>
              <button
                @click="isMobileSidebarOpen = false"
                class="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
            <div class="flex-1 overflow-hidden">
              <ChatSidebar
                :sessions="chatStore.sessions"
                :activeSessionId="chatStore.activeSession?.id || null"
                @newChat="handleMobileNewChat"
                @selectSession="handleMobileSelectSession"
                @renameSession="openRenameModal"
                @deleteSession="handleDeleteSession"
                @clearContext="isClearContextModalOpen = true"
              />
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Main Chat Window -->
    <ChatWindow
      :messages="chatStore.activeMessages"
      :streamingContent="chatStore.streamingContent"
      :statusMessage="ws.statusMessage.value"
      :isStreaming="chatStore.isStreaming"
      :isConnected="ws.isConnected.value"
      @sendQuery="handleSendQuery"
    />

    <!-- Clear Context Confirmation Modal -->
    <ClearContextModal
      :isOpen="isClearContextModalOpen"
      @close="isClearContextModalOpen = false"
      @confirm="confirmClearContext"
    />

    <!-- Rename Session Modal -->
    <Modal
      :isOpen="isRenameModalOpen"
      title="Rename Conversation"
      @close="isRenameModalOpen = false"
    >
      <form @submit.prevent="confirmRename" class="space-y-3">
        <input
          v-model="renameTitle"
          type="text"
          required
          class="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-[#153826] focus:border-[#153826] focus:outline-none"
        />
        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            @click="isRenameModalOpen = false"
            class="px-4 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-4 py-2 text-xs font-medium text-white bg-[#153826] hover:bg-[#1b4932] rounded-xl shadow-xs transition-colors"
          >
            Save Title
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, Plus, X } from 'lucide-vue-next'
import { useChatStore } from '../stores/chat'
import { useAuthStore } from '../stores/auth'
import { useChatWebSocket } from '../composables/useChatWebSocket'
import ChatSidebar from '../components/chat/ChatSidebar.vue'
import ChatWindow from '../components/chat/ChatWindow.vue'
import ClearContextModal from '../components/chat/ClearContextModal.vue'
import Modal from '../components/common/Modal.vue'
import type { ChatSession } from '../services/chatService'

const chatStore = useChatStore()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const ws = useChatWebSocket()

const isMobileSidebarOpen = ref(false)
const isClearContextModalOpen = ref(false)
const isRenameModalOpen = ref(false)
const renameSessionTarget = ref<ChatSession | null>(null)
const renameTitle = ref('')

const connectSocketForSession = (sessionId: string) => {
  if (authStore.token) {
    ws.connect(sessionId, authStore.token, {
      onToken: (tokenChunk) => {
        chatStore.appendStreamingToken(tokenChunk)
      },
      onDone: (payload) => {
        chatStore.finalizeStreamingMessage(payload)
      },
      onContextCleared: () => {
        chatStore.clearContext()
      },
      onError: (err) => {
        chatStore.handleStreamingError(err.message)
      },
    })
  }
}

const handleSelectSession = async (sessionId: string) => {
  const success = await chatStore.selectSession(sessionId)
  if (!success) {
    // 404 Not Found or load error: redirect back to base /chat view
    if (route.params.sessionId) {
      await router.push('/chat')
    }
    // Attempt fallback to first available session or fresh chat
    if (chatStore.sessions.length > 0 && chatStore.sessions[0].id !== sessionId) {
      await handleSelectSession(chatStore.sessions[0].id)
    } else {
      await handleNewChat()
    }
    return
  }

  if (route.params.sessionId !== sessionId) {
    router.replace(`/chat/${sessionId}`)
  }

  connectSocketForSession(sessionId)
}

onMounted(async () => {
  await chatStore.fetchSessions()
  const targetId = (route.params.sessionId as string) || (chatStore.sessions[0]?.id ?? null)
  if (targetId) {
    await handleSelectSession(targetId)
  } else {
    await handleNewChat()
  }
})

// Watch for direct URL navigation changes between chat sessions or back to /chat
watch(
  () => route.params.sessionId,
  async (newSessionId, oldSessionId) => {
    if (newSessionId && newSessionId !== oldSessionId && newSessionId !== chatStore.activeSession?.id) {
      await handleSelectSession(newSessionId as string)
    } else if (!newSessionId && oldSessionId && !chatStore.isStreaming) {
      if (chatStore.sessions.length > 0) {
        await handleSelectSession(chatStore.sessions[0].id)
      } else {
        await handleNewChat()
      }
    }
  }
)

const handleMobileSelectSession = async (sessionId: string) => {
  isMobileSidebarOpen.value = false
  await handleSelectSession(sessionId)
}

const handleNewChat = async () => {
  const session = await chatStore.createNewSession('New Conversation')
  if (session) {
    await handleSelectSession(session.id)
  }
}

const handleMobileNewChat = async () => {
  isMobileSidebarOpen.value = false
  await handleNewChat()
}

const handleSendQuery = (query: string) => {
  const clientMsgId = `opt-${Date.now()}`
  // 1. Optimistic UI update
  chatStore.addOptimisticUserMessage(query, clientMsgId)
  // 2. Send over WebSocket
  ws.sendQuery(query, clientMsgId)
}

const confirmClearContext = () => {
  ws.clearContext()
  chatStore.clearContext()
  isClearContextModalOpen.value = false
}

const openRenameModal = (session: ChatSession) => {
  renameSessionTarget.value = session
  renameTitle.value = session.title
  isRenameModalOpen.value = true
}

const confirmRename = async () => {
  if (renameSessionTarget.value && renameTitle.value.trim()) {
    await chatStore.updateSessionTitle(renameSessionTarget.value.id, renameTitle.value.trim())
    isRenameModalOpen.value = false
    renameSessionTarget.value = null
  }
}

const handleDeleteSession = async (session: ChatSession) => {
  if (confirm(`Are you sure you want to delete "${session.title}"?`)) {
    await chatStore.deleteSession(session.id)
    if (chatStore.sessions.length > 0) {
      await handleSelectSession(chatStore.sessions[0].id)
    } else {
      await handleNewChat()
    }
  }
}
</script>
