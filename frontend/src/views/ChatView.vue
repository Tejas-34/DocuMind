<template>
  <div class="flex h-[calc(100vh-4rem)] overflow-hidden">
    <!-- Sidebar -->
    <ChatSidebar
      :sessions="chatStore.sessions"
      :activeSessionId="chatStore.activeSession?.id || null"
      @newChat="handleNewChat"
      @selectSession="handleSelectSession"
      @renameSession="openRenameModal"
      @deleteSession="handleDeleteSession"
      @clearContext="isClearContextModalOpen = true"
    />

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
          class="w-full px-3.5 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
        />
        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            @click="isRenameModalOpen = false"
            class="px-4 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-4 py-2 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
          >
            Save Title
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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

const isClearContextModalOpen = ref(false)
const isRenameModalOpen = ref(false)
const renameSessionTarget = ref<ChatSession | null>(null)
const renameTitle = ref('')

onMounted(async () => {
  await chatStore.fetchSessions()
  const targetId = (route.params.sessionId as string) || (chatStore.sessions[0]?.id ?? null)
  if (targetId) {
    await handleSelectSession(targetId)
  } else {
    await handleNewChat()
  }
})

const handleSelectSession = async (sessionId: string) => {
  await chatStore.selectSession(sessionId)
  if (route.params.sessionId !== sessionId) {
    router.replace(`/chat/${sessionId}`)
  }

  // Connect WebSocket
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
    })
  }
}

const handleNewChat = async () => {
  const session = await chatStore.createNewSession('New Conversation')
  if (session) {
    await handleSelectSession(session.id)
  }
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
