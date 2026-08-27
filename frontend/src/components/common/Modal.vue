<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm transition-opacity"
      @click.self="close"
    >
      <div
        class="bg-white dark:bg-gray-900 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-800 w-full max-w-md p-6 transform transition-all"
      >
        <div class="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-800">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ title }}
          </h3>
          <button
            @click="close"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1 rounded-md"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="py-4 text-gray-600 dark:text-gray-300 text-sm">
          <slot />
        </div>

        <div class="flex items-center justify-end gap-3 pt-3 border-t border-gray-100 dark:border-gray-800">
          <slot name="footer">
            <button
              @click="close"
              class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            >
              Cancel
            </button>
          </slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'

defineProps<{
  isOpen: boolean
  title: string
}>()

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}
</script>
