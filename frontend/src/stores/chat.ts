import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatService, type ChatSession, type Message, type Citation } from '../services/chatService'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<ChatSession[]>([])
  const activeSession = ref<ChatSession | null>(null)
  const isLoadingSessions = ref(false)
  const isLoadingActiveSession = ref(false)
  const isStreaming = ref(false)
  const streamingContent = ref('')

  const activeMessages = computed(() => {
    return activeSession.value?.messages || []
  })

  const fetchSessions = async () => {
    isLoadingSessions.value = true
    try {
      sessions.value = await chatService.listSessions()
    } catch (e) {
      console.error('Failed to fetch chat sessions:', e)
    } finally {
      isLoadingSessions.value = false
    }
  }

  const createNewSession = async (title?: string): Promise<ChatSession | null> => {
    try {
      const session = await chatService.createSession(title)
      sessions.value.unshift(session)
      await selectSession(session.id)
      return session
    } catch (e) {
      console.error('Failed to create session:', e)
      return null
    }
  }

  const selectSession = async (sessionId: string): Promise<boolean> => {
    isLoadingActiveSession.value = true
    streamingContent.value = ''
    isStreaming.value = false
    try {
      const detailed = await chatService.getSession(sessionId)
      activeSession.value = detailed
      return true
    } catch (e) {
      console.warn(`[useChatStore] Failed to load session ${sessionId}:`, e)
      activeSession.value = null
      return false
    } finally {
      isLoadingActiveSession.value = false
    }
  }

  const updateSessionTitle = async (sessionId: string, newTitle: string) => {
    try {
      const updated = await chatService.updateSessionTitle(sessionId, newTitle)
      const idx = sessions.value.findIndex((s) => s.id === sessionId)
      if (idx !== -1) sessions.value[idx].title = updated.title
      if (activeSession.value?.id === sessionId) activeSession.value.title = updated.title
    } catch (e) {
      console.error('Failed to rename session:', e)
    }
  }

  const deleteSession = async (sessionId: string) => {
    try {
      await chatService.deleteSession(sessionId)
      sessions.value = sessions.value.filter((s) => s.id !== sessionId)
      if (activeSession.value?.id === sessionId) {
        activeSession.value = sessions.value.length > 0 ? null : null
        if (sessions.value.length > 0) {
          await selectSession(sessions.value[0].id)
        }
      }
    } catch (e) {
      console.error('Failed to delete session:', e)
    }
  }

  // Optimistic UI updates
  const addOptimisticUserMessage = (text: string, clientMsgId: string) => {
    if (!activeSession.value) return
    if (!activeSession.value.messages) activeSession.value.messages = []

    const optMsg: Message = {
      id: clientMsgId,
      user_id: activeSession.value.user_id,
      session_id: activeSession.value.id,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
      isPending: true,
      client_msg_id: clientMsgId,
    }
    activeSession.value.messages.push(optMsg)
    streamingContent.value = ''
    isStreaming.value = true
  }

  const appendStreamingToken = (token: string) => {
    isStreaming.value = true
    streamingContent.value += token
  }

  const finalizeStreamingMessage = (payload: {
    message_id: string
    client_msg_id?: string
    role: string
    content: string
    citations?: Citation[]
  }) => {
    if (!activeSession.value) return
    if (!activeSession.value.messages) activeSession.value.messages = []

    // 1. Mark user optimistic message as confirmed
    if (payload.client_msg_id) {
      const userMsg = activeSession.value.messages.find(
        (m) => m.client_msg_id === payload.client_msg_id
      )
      if (userMsg) {
        userMsg.isPending = false
      }
    }

    // 2. Add assistant message
    const asstMsg: Message = {
      id: payload.message_id,
      user_id: activeSession.value.user_id,
      session_id: activeSession.value.id,
      role: 'assistant',
      content: payload.content || streamingContent.value,
      citations: payload.citations || [],
      created_at: new Date().toISOString(),
    }
    activeSession.value.messages.push(asstMsg)

    streamingContent.value = ''
    isStreaming.value = false

    // Update list title if changed
    const currentInList = sessions.value.find((s) => s.id === activeSession.value?.id)
    if (currentInList && activeSession.value.title !== currentInList.title) {
      currentInList.title = activeSession.value.title
    }
  }

  const handleStreamingError = (errorMessage?: string) => {
    if (activeSession.value) {
      if (!activeSession.value.messages) activeSession.value.messages = []
      // Resolve any pending message status
      activeSession.value.messages.forEach((m) => {
        if (m.isPending) m.isPending = false
      })

      const displayError = errorMessage || 'Failed to get an answer. Please verify server connection or API key.'
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        user_id: activeSession.value.user_id,
        session_id: activeSession.value.id,
        role: 'assistant',
        content: `⚠️ **Error:** ${displayError}`,
        citations: [],
        created_at: new Date().toISOString(),
      }
      activeSession.value.messages.push(errorMsg)
    }
    streamingContent.value = ''
    isStreaming.value = false
  }

  const clearContext = () => {
    streamingContent.value = ''
    isStreaming.value = false
  }

  return {
    sessions,
    activeSession,
    activeMessages,
    isLoadingSessions,
    isLoadingActiveSession,
    isStreaming,
    streamingContent,
    fetchSessions,
    createNewSession,
    selectSession,
    updateSessionTitle,
    deleteSession,
    addOptimisticUserMessage,
    appendStreamingToken,
    finalizeStreamingMessage,
    handleStreamingError,
    clearContext,
  }
})
