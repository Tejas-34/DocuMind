import { apiClient } from './api'

export interface Citation {
  document_id: string
  document_name: string
  page_number?: number | null
  snippet?: string | null
}

export interface Message {
  id: string
  user_id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[] | null
  created_at: string
  // UI states
  isPending?: boolean
  client_msg_id?: string
}

export interface ChatSession {
  id: string
  user_id: string
  title: string
  created_at: string
  updated_at: string
  messages?: Message[]
}

export const chatService = {
  async listSessions(): Promise<ChatSession[]> {
    const res = await apiClient.get<ChatSession[]>('/chat/sessions')
    return res.data
  },

  async createSession(title?: string): Promise<ChatSession> {
    const res = await apiClient.post<ChatSession>('/chat/sessions', { title: title || 'New Conversation' })
    return res.data
  },

  async getSession(sessionId: string): Promise<ChatSession> {
    const res = await apiClient.get<ChatSession>(`/chat/sessions/${sessionId}`)
    return res.data
  },

  async updateSessionTitle(sessionId: string, title: string): Promise<ChatSession> {
    const res = await apiClient.patch<ChatSession>(`/chat/sessions/${sessionId}`, { title })
    return res.data
  },

  async deleteSession(sessionId: string): Promise<void> {
    await apiClient.delete(`/chat/sessions/${sessionId}`)
  },
}
