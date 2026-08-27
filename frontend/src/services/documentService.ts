import { apiClient } from './api'

export interface DocumentItem {
  id: string
  user_id: string
  filename: string
  file_size: number
  mime_type: string
  status: 'uploading' | 'processing' | 'ready' | 'failed'
  error_message?: string | null
  total_pages?: number | null
  created_at: string
  updated_at: string
}

export const documentService = {
  async uploadDocument(file: File): Promise<DocumentItem> {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post<DocumentItem>('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return res.data
  },

  async listDocuments(): Promise<DocumentItem[]> {
    const res = await apiClient.get<DocumentItem[]>('/documents')
    return res.data
  },

  async getDocument(documentId: string): Promise<DocumentItem> {
    const res = await apiClient.get<DocumentItem>(`/documents/${documentId}`)
    return res.data
  },

  async deleteDocument(documentId: string): Promise<void> {
    await apiClient.delete(`/documents/${documentId}`)
  },
}
