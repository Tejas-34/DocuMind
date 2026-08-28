<template>
  <span
    class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border select-none transition-colors"
    :class="statusClasses"
  >
    <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="dotClasses"></span>
    <span class="capitalize text-[11px] font-medium">{{ displayStatus }}</span>
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
      return 'bg-emerald-50/80 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 border-emerald-200/60 dark:border-emerald-800/40'
    case 'processing':
    case 'uploading':
      return 'bg-amber-50/80 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300 border-amber-200/60 dark:border-amber-800/40'
    case 'failed':
      return 'bg-rose-50/80 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300 border-rose-200/60 dark:border-rose-800/40'
    default:
      return 'bg-gray-50 text-gray-700 dark:bg-gray-800/60 dark:text-gray-300 border-gray-200/60 dark:border-gray-700/60'
  }
})

const dotClasses = computed(() => {
  switch (props.status) {
    case 'ready':
      return 'bg-emerald-500 animate-pulse'
    case 'processing':
    case 'uploading':
      return 'bg-amber-500 animate-ping'
    case 'failed':
      return 'bg-rose-500'
    default:
      return 'bg-gray-400'
  }
})
</script>
