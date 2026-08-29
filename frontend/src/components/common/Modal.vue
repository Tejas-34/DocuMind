<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 dark:bg-black/60 backdrop-blur-sm"
        @click.self="close"
      >
        <div
          class="bg-white dark:bg-[#0c1611] rounded-3xl shadow-2xl border border-gray-200/80 dark:border-gray-800 w-full max-w-md p-6 transform transition-all scale-100"
        >
          <div class="flex items-center justify-between pb-3.5 border-b border-gray-100 dark:border-gray-800">
            <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">
              {{ title }}
            </h3>
            <button
              @click="close"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1.5 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <X class="w-4 h-4" />
            </button>
          </div>

          <div class="py-4 text-gray-600 dark:text-gray-300 text-sm">
            <slot />
          </div>

          <div class="flex items-center justify-end gap-2.5 pt-3.5 border-t border-gray-100 dark:border-gray-800">
            <slot name="footer">
              <button
                @click="close"
                class="px-4 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
              >
                Cancel
              </button>
            </slot>
          </div>
        </div>
      </div>
    </Transition>
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
