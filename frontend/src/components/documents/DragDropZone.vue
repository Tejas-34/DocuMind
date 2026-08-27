<template>
  <div
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
    class="relative rounded-3xl border-2 p-10 sm:p-16 text-center transition-all duration-200 cursor-pointer group select-none shadow-xs"
    :class="
      isDragging
        ? 'border-solid border-indigo-600 dark:border-indigo-500 bg-indigo-50/80 dark:bg-indigo-950/40 scale-[1.01] shadow-lg shadow-indigo-500/10'
        : 'border-dashed border-gray-300/90 dark:border-gray-700/80 hover:border-indigo-400 dark:hover:border-indigo-500/60 bg-white/80 dark:bg-gray-900/60 hover:bg-indigo-50/20 dark:hover:bg-indigo-950/10'
    "
    @click="triggerBrowse"
  >
    <input
      ref="fileInput"
      type="file"
      class="hidden"
      accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
      @change="handleFileInput"
      multiple
    />

    <div class="flex flex-col items-center justify-center gap-4 max-w-md mx-auto">
      <div
        class="w-16 h-16 rounded-2xl flex items-center justify-center transition-transform duration-200 group-hover:scale-105 shadow-inner"
        :class="
          isDragging
            ? 'bg-indigo-600 text-white shadow-indigo-500/30'
            : 'bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400'
        "
      >
        <UploadCloud class="w-8 h-8" />
      </div>

      <div class="space-y-1.5">
        <p class="text-base font-semibold text-gray-900 dark:text-gray-100">
          <span class="text-indigo-600 dark:text-indigo-400 hover:underline">Click to browse</span>
          or drag & drop files here
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Supports PDF, TXT, and Markdown files up to 25MB
        </p>
      </div>

      <div v-if="validationError" class="mt-1 text-xs font-medium text-rose-500 flex items-center gap-1.5 bg-rose-50 dark:bg-rose-950/50 px-3 py-1.5 rounded-lg border border-rose-200 dark:border-rose-800">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ validationError }}</span>
      </div>

      <div v-if="isUploading" class="mt-1 flex items-center gap-2 text-xs font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/50 px-4 py-2 rounded-xl animate-pulse">
        <Loader2 class="w-4 h-4 animate-spin" />
        <span>Uploading and extracting text in background...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadCloud, AlertCircle, Loader2 } from 'lucide-vue-next'

defineProps<{
  isUploading: boolean
}>()

const emit = defineEmits<{
  (e: 'filesSelected', files: File[]): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const validationError = ref<string | null>(null)

const triggerBrowse = () => {
  fileInput.value?.click()
}

const validateAndEmit = (fileList: FileList | null) => {
  validationError.value = null
  if (!fileList || fileList.length === 0) return

  const validFiles: File[] = []
  const maxBytes = 25 * 1024 * 1024 // 25MB

  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i]
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!['pdf', 'txt', 'md'].includes(ext || '')) {
      validationError.value = `File "${file.name}" is unsupported. Only PDF, TXT, and MD are allowed.`
      return
    }
    if (file.size > maxBytes) {
      validationError.value = `File "${file.name}" exceeds maximum allowed size of 25MB.`
      return
    }
    if (file.size === 0) {
      validationError.value = `File "${file.name}" is empty (0 bytes).`
      return
    }
    validFiles.push(file)
  }

  if (validFiles.length > 0) {
    emit('filesSelected', validFiles)
  }
}

const handleFileInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  validateAndEmit(target.files)
  if (fileInput.value) fileInput.value.value = ''
}

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  validateAndEmit(e.dataTransfer?.files || null)
}
</script>
