<template>
  <div class="py-8 px-4 sm:px-8 max-w-6xl mx-auto space-y-6 pb-24 md:pb-8">
    <!-- Workspace Title Header & Upload Action -->
    <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-2">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
          Document Workspace
        </h1>
        <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1 max-w-2xl leading-relaxed">
          Upload and manage your private files (.pdf, .txt, .md). Vector embeddings are generated automatically for strict Q&A retrieval.
        </p>
      </div>

      <button
        type="button"
        @click="triggerUpload"
        class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#153826] hover:bg-[#1b4932] dark:bg-[#0f2e1e] dark:hover:bg-[#153e29] text-white dark:text-emerald-400 border border-transparent dark:border-emerald-800/60 font-semibold text-xs transition-all shadow-xs cursor-pointer shrink-0 self-start sm:self-auto"
      >
        <Plus class="w-4 h-4 text-emerald-300 dark:text-emerald-400" />
        <span>Upload Documents</span>
      </button>
    </div>

    <!-- Drag & Drop Upload Zone -->
    <DragDropZone
      ref="dropZoneRef"
      :isUploading="documentStore.isUploading"
      @filesSelected="handleFilesSelected"
    />

    <!-- Upload Error Notice -->
    <div
      v-if="documentStore.uploadError"
      class="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-400 text-xs font-medium flex items-center justify-between gap-3 shadow-xs transition-all"
    >
      <div class="flex items-center gap-2.5">
        <AlertCircle class="w-4 h-4 shrink-0 text-rose-600 dark:text-rose-400" />
        <span class="leading-relaxed">{{ documentStore.uploadError }}</span>
      </div>
      <button
        type="button"
        @click="documentStore.clearUploadError"
        class="p-1 text-rose-400 hover:text-rose-700 dark:hover:text-rose-200 rounded-lg transition-colors cursor-pointer"
        title="Dismiss error"
      >
        <X class="w-4 h-4" />
      </button>
    </div>

    <!-- Documents List/Grid -->
    <DocumentGrid
      :documents="documentStore.documents"
      @refresh="documentStore.fetchDocuments"
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
      <div v-if="selectedDoc" class="space-y-4 font-sans text-xs">
        <div>
          <span class="text-gray-500 dark:text-gray-400 block mb-1 font-medium">Filename</span>
          <span class="font-semibold text-gray-900 dark:text-white text-sm">{{ selectedDoc.filename }}</span>
        </div>
        <div>
          <span class="text-gray-500 dark:text-gray-400 block mb-1 font-medium">Document UUID</span>
          <span class="font-mono bg-gray-100 dark:bg-gray-800/80 text-gray-800 dark:text-gray-200 p-2 rounded-xl block text-[11px] select-all border border-gray-200 dark:border-gray-700/80">
            {{ selectedDoc.id }}
          </span>
        </div>
        <div class="grid grid-cols-2 gap-3 pt-1">
          <div class="p-3 rounded-2xl bg-gray-50 dark:bg-[#16221c]/40 border border-gray-200/80 dark:border-gray-800">
            <span class="text-gray-500 dark:text-gray-400 block text-[11px] mb-0.5 font-medium">File Size</span>
            <span class="font-semibold text-gray-800 dark:text-gray-200">{{ (selectedDoc.file_size / 1024).toFixed(1) }} KB</span>
          </div>
          <div class="p-3 rounded-2xl bg-gray-50 dark:bg-[#16221c]/40 border border-gray-200/80 dark:border-gray-800">
            <span class="text-gray-500 dark:text-gray-400 block text-[11px] mb-0.5 font-medium">Total Pages</span>
            <span class="font-semibold text-gray-800 dark:text-gray-200">{{ selectedDoc.total_pages || 1 }}</span>
          </div>
        </div>
        <div class="pt-1">
          <span class="text-gray-500 dark:text-gray-400 block mb-1 font-medium">Processing Status</span>
          <div class="flex items-center gap-2">
            <StatusBadge :status="selectedDoc.status" />
          </div>
        </div>

        <!-- Failure Reason Callout Box -->
        <div
          v-if="selectedDoc.status === 'failed'"
          class="p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800/80 text-rose-800 dark:text-rose-300 space-y-1.5"
        >
          <div class="flex items-center gap-2 font-semibold text-xs text-rose-700 dark:text-rose-400">
            <AlertCircle class="w-4 h-4 shrink-0" />
            <span>Failure Reason</span>
          </div>
          <p class="text-[11px] leading-relaxed text-rose-700/90 dark:text-rose-300/90 break-words">
            {{ selectedDoc.error_message || 'Document could not be processed. Please verify that the file contains readable text and is not encrypted.' }}
          </p>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Plus, AlertCircle, X } from 'lucide-vue-next'
import { useDocumentStore } from '../stores/document'
import DragDropZone from '../components/documents/DragDropZone.vue'
import DocumentGrid from '../components/documents/DocumentGrid.vue'
import DeleteDocModal from '../components/documents/DeleteDocModal.vue'
import Modal from '../components/common/Modal.vue'
import StatusBadge from '../components/common/StatusBadge.vue'
import type { DocumentItem } from '../services/documentService'

const documentStore = useDocumentStore()
const dropZoneRef = ref<{ triggerBrowse?: () => void } | null>(null)

const selectedDoc = ref<DocumentItem | null>(null)
const isDeleteModalOpen = ref(false)
const isDetailsModalOpen = ref(false)

onMounted(() => {
  documentStore.fetchDocuments()
})

onUnmounted(() => {
  documentStore.stopPolling()
})

const triggerUpload = () => {
  dropZoneRef.value?.triggerBrowse?.()
}

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
