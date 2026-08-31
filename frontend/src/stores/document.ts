import { defineStore } from 'pinia'
import { ref } from 'vue'
import { documentService, type DocumentItem } from '../services/documentService'

export const useDocumentStore = defineStore('document', () => {
  const documents = ref<DocumentItem[]>([])
  const isLoading = ref(false)
  const isUploading = ref(false)
  const uploadError = ref<string | null>(null)
  let pollInterval: any = null

  const fetchDocuments = async () => {
    isLoading.value = true
    try {
      documents.value = await documentService.listDocuments()
      checkAndStartPolling()
    } catch (err: any) {
      console.error('Failed to fetch documents:', err)
    } finally {
      isLoading.value = false
    }
  }

  const clearUploadError = () => {
    uploadError.value = null
  }

  const uploadFile = async (file: File): Promise<boolean> => {
    isUploading.value = true
    uploadError.value = null
    try {
      const doc = await documentService.uploadDocument(file)
      // Add or update in list
      const idx = documents.value.findIndex((d) => d.id === doc.id)
      if (idx !== -1) {
        documents.value[idx] = doc
      } else {
        documents.value.unshift(doc)
      }
      checkAndStartPolling()
      return true
    } catch (err: any) {
      let detailMsg = 'Failed to upload document.'
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          detailMsg = err.response.data.detail
        } else if (Array.isArray(err.response.data.detail)) {
          detailMsg = err.response.data.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
        }
      } else if (err.message) {
        detailMsg = err.message
      }
      uploadError.value = `Upload failed for "${file.name}": ${detailMsg}`
      return false
    } finally {
      isUploading.value = false
    }
  }

  const deleteDocument = async (documentId: string): Promise<boolean> => {
    try {
      await documentService.deleteDocument(documentId)
      documents.value = documents.value.filter((d) => d.id !== documentId)
      return true
    } catch (err: any) {
      console.error('Failed to delete document:', err)
      return false
    }
  }

  const checkAndStartPolling = () => {
    const hasPending = documents.value.some(
      (d) => d.status === 'uploading' || d.status === 'processing'
    )
    if (hasPending && !pollInterval) {
      pollInterval = setInterval(async () => {
        try {
          const updatedDocs = await documentService.listDocuments()
          documents.value = updatedDocs
          const stillPending = updatedDocs.some(
            (d) => d.status === 'uploading' || d.status === 'processing'
          )
          if (!stillPending) {
            stopPolling()
          }
        } catch (e) {
          stopPolling()
        }
      }, 3000)
    } else if (!hasPending) {
      stopPolling()
    }
  }

  const stopPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  return {
    documents,
    isLoading,
    isUploading,
    uploadError,
    fetchDocuments,
    uploadFile,
    deleteDocument,
    clearUploadError,
    stopPolling,
  }
})
