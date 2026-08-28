<template>
  <div
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
    class="relative rounded-3xl border-2 p-8 sm:p-12 text-center transition-all duration-200 cursor-pointer group select-none shadow-xs"
    :class="
      isDragging
        ? 'border-solid border-[#153826] dark:border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/30 scale-[1.005] shadow-md'
        : 'border-dashed border-gray-200 dark:border-gray-800 hover:border-emerald-300 dark:hover:border-emerald-700/60 bg-[#f9faf9] dark:bg-[#111915]/40 hover:bg-[#f4f7f5] dark:hover:bg-[#14201a]/60'
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

    <div class="flex flex-col items-center justify-center gap-3.5 max-w-md mx-auto">
      <div
        class="w-14 h-14 rounded-2xl bg-white dark:bg-[#16221c] border border-gray-200/80 dark:border-gray-700/80 shadow-xs flex items-center justify-center text-[#153826] dark:text-emerald-400 transition-transform duration-200 group-hover:scale-105"
      >
        <UploadCloud class="w-7 h-7" />
      </div>

      <div class="space-y-1">
        <p class="text-sm sm:text-base font-semibold text-gray-900 dark:text-gray-100">
          Drag & drop files here or <span class="text-[#153826] dark:text-emerald-400 hover:underline">click to browse</span>
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Supports PDF, TXT, and Markdown files up to 25MB
        </p>
      </div>

      <div v-if="validationError" class="mt-1 text-xs font-medium text-rose-500 flex items-center gap-1.5 bg-rose-50 dark:bg-rose-950/50 px-3 py-1.5 rounded-xl border border-rose-200 dark:border-rose-800">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ validationError }}</span>
      </div>

      <div v-if="isUploading" class="mt-1 flex items-center gap-2 text-xs font-medium text-[#153826] dark:text-emerald-400 bg-emerald-50/80 dark:bg-emerald-950/50 px-4 py-2 rounded-xl border border-emerald-200/60 dark:border-emerald-800/40 animate-pulse">
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
