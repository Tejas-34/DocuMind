<template>
  <div
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
    class="relative rounded-2xl border border-dashed p-8 sm:p-10 text-center transition-all duration-200 cursor-pointer group select-none shadow-xs"
    :class="
      isDragging
        ? 'border-emerald-600 dark:border-emerald-500 bg-emerald-50/80 dark:bg-emerald-950/40 scale-[1.002] shadow-md'
        : 'border-gray-300 dark:border-emerald-800/40 hover:border-emerald-500 dark:hover:border-emerald-600/60 bg-gray-50/60 dark:bg-[#07110c]/80 hover:bg-emerald-50/30 dark:hover:bg-[#0c1a13]/80'
    "
    @click="triggerBrowse"
  >
    <input
      ref="fileInput"
      type="file"
      class="hidden"
      accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown,application/octet-stream"
      @change="handleFileInput"
      multiple
    />

    <div class="flex flex-col items-center justify-center gap-2.5 max-w-md mx-auto">
      <div
        class="w-12 h-12 rounded-full bg-emerald-50 dark:bg-[#0b1d14] border border-emerald-200/80 dark:border-emerald-800/50 flex items-center justify-center text-emerald-700 dark:text-emerald-400 mx-auto transition-transform duration-200 group-hover:scale-105 shadow-xs"
      >
        <UploadCloud class="w-6 h-6" />
      </div>

      <div class="space-y-1">
        <p class="text-sm sm:text-base font-semibold text-gray-900 dark:text-gray-100">
          Drag & drop files here
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          or <span class="text-emerald-700 dark:text-emerald-400 font-semibold hover:underline">click to browse</span>
        </p>
        <p class="text-xs text-gray-400 dark:text-gray-500 pt-1">
          Supports PDF, TXT, and Markdown files up to 25MB
        </p>
      </div>

      <div v-if="validationError" class="mt-2 text-xs font-medium text-rose-600 dark:text-rose-400 flex items-center gap-1.5 bg-rose-50 dark:bg-rose-950/50 px-3 py-1.5 rounded-xl border border-rose-200 dark:border-rose-800">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ validationError }}</span>
      </div>

      <div v-if="isUploading" class="mt-2 flex items-center gap-2 text-xs font-medium text-emerald-800 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-4 py-2 rounded-xl border border-emerald-200 dark:border-emerald-800/60 animate-pulse">
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

const CANONICAL_MIMES: Record<string, string> = {
  pdf: 'application/pdf',
  txt: 'text/plain',
  md: 'text/markdown',
}

const triggerBrowse = () => {
  if (fileInput.value) {
    fileInput.value.value = ''
    fileInput.value.click()
  }
}

const validateAndEmit = (fileList: FileList | null) => {
  validationError.value = null
  if (!fileList || fileList.length === 0) return

  const validFiles: File[] = []
  const maxBytes = 25 * 1024 * 1024 // 25MB

  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i]
    const ext = file.name.split('.').pop()?.toLowerCase() || ''
    if (!['pdf', 'txt', 'md'].includes(ext)) {
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

    // Gracefully handle mobile generic or empty MIME types
    const canonicalMime = CANONICAL_MIMES[ext] || 'application/octet-stream'
    const isGenericMime = !file.type || file.type === 'application/octet-stream'
    const normalizedFile = isGenericMime
      ? new File([file], file.name, { type: canonicalMime, lastModified: file.lastModified })
      : file

    validFiles.push(normalizedFile)
  }

  if (validFiles.length > 0) {
    emit('filesSelected', validFiles)
  }
}

const handleFileInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  validateAndEmit(target.files)
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  validateAndEmit(e.dataTransfer?.files || null)
}

defineExpose({
  triggerBrowse,
})
</script>
