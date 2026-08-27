<template>
  <span
    class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium"
    :class="statusClasses"
  >
    <span class="w-1.5 h-1.5 rounded-full" :class="dotClasses"></span>
    <span class="capitalize">{{ displayStatus }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: 'uploading' | 'processing' | 'ready' | 'failed' | string
}>()

const displayStatus = computed(() => {
  if (props.status === 'processing') return 'Processing'
  if (props.status === 'uploading') return 'Uploading'
  if (props.status === 'ready') return 'Ready'
  if (props.status === 'failed') return 'Failed'
  return props.status
})

const statusClasses = computed(() => {
  switch (props.status) {
    case 'ready':
      return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
    case 'processing':
    case 'uploading':
      return 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-200 dark:border-amber-800 animate-pulse'
    case 'failed':
      return 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-800'
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
  }
})

const dotClasses = computed(() => {
  switch (props.status) {
    case 'ready':
      return 'bg-emerald-500'
    case 'processing':
    case 'uploading':
      return 'bg-amber-500'
    case 'failed':
      return 'bg-rose-500'
    default:
      return 'bg-gray-400'
  }
})
</script>
