<template>
  <Modal :isOpen="isOpen" title="Delete Document" @close="$emit('close')">
    <div class="space-y-3">
      <p class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
        Are you sure you want to permanently delete
        <strong class="text-gray-900 dark:text-white font-semibold">{{ doc?.filename }}</strong>?
      </p>
      <div class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200/80 dark:border-rose-800/60 text-rose-600 dark:text-rose-400 text-xs font-medium leading-relaxed">
        This action will immediately purge all extracted text chunks and vector embeddings from your private index.
      </div>
    </div>

    <template #footer>
      <button
        @click="$emit('close')"
        class="px-4 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
      >
        Cancel
      </button>
      <button
        @click="$emit('confirm')"
        class="px-4 py-2 text-xs font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-xs transition-colors"
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
