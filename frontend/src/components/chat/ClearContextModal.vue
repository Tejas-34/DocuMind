<template>
  <Modal :isOpen="isOpen" title="Clear Current Context" @close="$emit('close')">
    <p>
      Are you sure you want to reset the conversational context memory for this session?
    </p>
    <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
      This instructs the AI to ignore previous exchanges when generating subsequent answers. Your historical message log will remain saved in this thread.
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
        class="px-4 py-2 text-sm font-medium text-white bg-amber-600 hover:bg-amber-700 rounded-lg shadow-sm"
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
