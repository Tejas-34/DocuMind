<template>
  <Modal :isOpen="isOpen" title="Clear Current Context" @close="$emit('close')">
    <div class="space-y-3">
      <p class="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">
        Are you sure you want to reset the conversational context memory for this session?
      </p>
      <div class="p-3 rounded-xl bg-amber-50/80 dark:bg-amber-950/30 border border-amber-200/60 dark:border-amber-900/40 text-amber-800 dark:text-amber-300 text-xs leading-relaxed">
        This instructs the AI to ignore previous exchanges when generating subsequent answers. Your historical message log will remain saved in this thread.
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
        class="px-4 py-2 text-xs font-medium text-white bg-amber-600 hover:bg-amber-700 rounded-xl shadow-xs transition-colors"
      >
        Reset Context
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import Modal from '../common/Modal.vue'

defineProps<{
  isOpen: boolean
}>()

defineEmits(['close', 'confirm'])
</script>
