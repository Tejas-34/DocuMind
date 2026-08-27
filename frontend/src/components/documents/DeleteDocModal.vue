<template>
  <Modal :isOpen="isOpen" title="Delete Document" @close="$emit('close')">
    <p>
      Are you sure you want to permanently delete
      <strong class="text-gray-900 dark:text-white font-semibold">{{ doc?.filename }}</strong>?
    </p>
    <p class="text-xs text-rose-500 mt-2 font-medium">
      This action will immediately purge all extracted text chunks and vector embeddings from your private index.
    </p>

    <template #footer>
      <button
        @click="$emit('close')"
        class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
      >
        Cancel
      </button>
      <button
        @click="$emit('confirm')"
        class="px-4 py-2 text-sm font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-lg shadow-sm"
      >
        Delete Document
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import Modal from '../common/Modal.vue'
import type { DocumentItem } from '../../services/documentService'

defineProps<{
  isOpen: boolean
  doc: DocumentItem | null
}>()

defineEmits(['close', 'confirm'])
</script>
