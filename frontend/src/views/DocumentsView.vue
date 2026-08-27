<template>
  <div class="py-8 px-4 sm:px-8 max-w-6xl mx-auto space-y-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-gray-200/60 dark:border-gray-800">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
          Document Workspace
        </h1>
        <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1">
          Upload and manage your private files (.pdf, .txt, .md). Vector embeddings are generated automatically for strict Q&A retrieval.
        </p>
      </div>

      <RouterLink
        to="/chat"
        class="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all active:scale-[0.99] shrink-0"
      >
        <MessageSquare class="w-4 h-4" />
        <span>Open Chat Assistant</span>
      </RouterLink>
    </div>

    <!-- Drag & Drop Upload Zone -->
    <DragDropZone
      :isUploading="documentStore.isUploading"
      @filesSelected="handleFilesSelected"
    />

    <!-- Upload Error Notice -->
    <div
      v-if="documentStore.uploadError"
      class="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-800 text-rose-600 dark:text-rose-400 text-xs font-medium"
    >
      {{ documentStore.uploadError }}
    </div>

    <!-- Documents List/Grid -->
    <DocumentGrid
      :documents="documentStore.documents"
      @deleteDoc="openDeleteModal"
      @viewDetails="openDetailsModal"
    />

    <!-- Delete Confirmation Modal -->
    <DeleteDocModal
      :isOpen="isDeleteModalOpen"
      :doc="selectedDoc"
      @close="isDeleteModalOpen = false"
      @confirm="confirmDelete"
    />

    <!-- Document Metadata Details Modal -->
    <Modal
      :isOpen="isDetailsModalOpen"
      title="Document Details & Status"
      @close="isDetailsModalOpen = false"
    >
      <div v-if="selectedDoc" class="space-y-3.5 font-sans text-xs">
        <div>
          <span class="text-gray-400 dark:text-gray-500 block mb-1 font-medium">Filename</span>
          <span class="font-semibold text-gray-900 dark:text-white text-sm">{{ selectedDoc.filename }}</span>
        </div>
        <div>
          <span class="text-gray-400 dark:text-gray-500 block mb-1 font-medium">Document UUID</span>
          <span class="font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded-lg block text-[11px] select-all border border-gray-200/60 dark:border-gray-700/60">
            {{ selectedDoc.id }}
          </span>
        </div>
        <div class="grid grid-cols-2 gap-3 pt-1">
          <div class="p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800">
            <span class="text-gray-400 dark:text-gray-500 block text-[11px] mb-0.5 font-medium">File Size</span>
            <span class="font-semibold text-gray-800 dark:text-gray-200">{{ (selectedDoc.file_size / 1024).toFixed(1) }} KB</span>
          </div>
          <div class="p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800">
            <span class="text-gray-400 dark:text-gray-500 block text-[11px] mb-0.5 font-medium">Total Pages</span>
            <span class="font-semibold text-gray-800 dark:text-gray-200">{{ selectedDoc.total_pages || 1 }}</span>
          </div>
        </div>
        <div class="pt-1">
          <span class="text-gray-400 dark:text-gray-500 block mb-1 font-medium">Status</span>
          <StatusBadge :status="selectedDoc.status" />
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { MessageSquare } from 'lucide-vue-next'
import { useDocumentStore } from '../stores/document'
import DragDropZone from '../components/documents/DragDropZone.vue'
import DocumentGrid from '../components/documents/DocumentGrid.vue'
import DeleteDocModal from '../components/documents/DeleteDocModal.vue'
import Modal from '../components/common/Modal.vue'
import StatusBadge from '../components/common/StatusBadge.vue'
import type { DocumentItem } from '../services/documentService'

const documentStore = useDocumentStore()

const selectedDoc = ref<DocumentItem | null>(null)
const isDeleteModalOpen = ref(false)
const isDetailsModalOpen = ref(false)

onMounted(() => {
  documentStore.fetchDocuments()
})

onUnmounted(() => {
  documentStore.stopPolling()
})

const handleFilesSelected = async (files: File[]) => {
  for (const file of files) {
    await documentStore.uploadFile(file)
  }
}

const openDeleteModal = (doc: DocumentItem) => {
  selectedDoc.value = doc
  isDeleteModalOpen.value = true
}

const confirmDelete = async () => {
  if (selectedDoc.value) {
    await documentStore.deleteDocument(selectedDoc.value.id)
    isDeleteModalOpen.value = false
    selectedDoc.value = null
  }
}

const openDetailsModal = (doc: DocumentItem) => {
  selectedDoc.value = doc
  isDetailsModalOpen.value = true
}
</script>
