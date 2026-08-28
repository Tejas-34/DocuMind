<template>
  <div class="bg-white dark:bg-[#121915] rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm overflow-hidden transition-colors duration-200">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800/80 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <FileText class="w-4 h-4 text-[#153826] dark:text-emerald-400" />
        <h3 class="font-semibold text-sm text-gray-900 dark:text-gray-100">
          Document Library
        </h3>
        <span class="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-[#153826] dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40">
          {{ documents.length }}
        </span>
      </div>
      <div class="flex items-center gap-1.5 text-[11px] text-gray-400 dark:text-gray-500 font-medium">
        <span>Auto-refreshing</span>
        <RotateCw class="w-3 h-3 animate-spin text-gray-400" />
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="documents.length === 0" class="p-16 text-center">
      <Inbox class="w-12 h-12 text-gray-300 dark:text-gray-700 mx-auto mb-3 opacity-60" />
      <p class="text-sm font-semibold text-gray-800 dark:text-gray-200">No documents uploaded yet</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1 max-w-xs mx-auto">
        Drag and drop a PDF or text file into the upload zone above to enable Q&A.
      </p>
    </div>

    <!-- Responsive Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-left text-sm min-w-[700px]">
        <thead class="bg-gray-50/70 dark:bg-[#16221c]/40 border-b border-gray-100 dark:border-gray-800 text-[10px] text-gray-400 dark:text-gray-500 font-semibold uppercase tracking-wider select-none">
          <tr>
            <th class="py-3.5 px-6">FILE NAME</th>
            <th class="py-3.5 px-6">DOCUMENT ID</th>
            <th class="py-3.5 px-6">UPLOADED ON</th>
            <th class="py-3.5 px-6">SIZE</th>
            <th class="py-3.5 px-6">STATUS</th>
            <th class="py-3.5 px-6 text-right">ACTIONS</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-800/60">
          <tr
            v-for="doc in documents"
            :key="doc.id"
            class="hover:bg-gray-50/60 dark:hover:bg-[#16221c]/30 transition-colors duration-150 cursor-default group"
          >
            <!-- Filename -->
            <td class="py-4 px-6 font-medium text-gray-900 dark:text-gray-100">
              <div class="flex items-center gap-3">
                <div
                  v-if="doc.filename.toLowerCase().endsWith('.pdf')"
                  class="w-7 h-7 rounded-lg bg-rose-500 text-white flex items-center justify-center shrink-0 shadow-2xs font-bold text-[9px] tracking-tighter"
                >
                  PDF
                </div>
                <div
                  v-else
                  class="w-7 h-7 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-100 dark:border-emerald-900/40 text-[#153826] dark:text-emerald-400 flex items-center justify-center shrink-0"
                >
                  <FileIcon class="w-3.5 h-3.5" />
                </div>
                <span class="truncate max-w-[220px] font-semibold text-xs text-gray-900 dark:text-white" :title="doc.filename">
                  {{ doc.filename }}
                </span>
              </div>
            </td>

            <!-- Document UUID with copy button -->
            <td class="py-4 px-6 font-mono text-xs text-gray-500 dark:text-gray-400">
              <div class="flex items-center gap-1.5">
                <span class="truncate max-w-[130px] bg-gray-100/80 dark:bg-gray-800/80 px-2 py-0.5 rounded-md text-[11px]" :title="doc.id">
                  {{ doc.id }}
                </span>
                <button
                  type="button"
                  @click.stop="copyId(doc.id)"
                  class="p-1 hover:text-[#153826] dark:hover:text-emerald-400 rounded transition-colors"
                  :title="copiedId === doc.id ? 'Copied!' : 'Copy Document ID'"
                >
                  <Check v-if="copiedId === doc.id" class="w-3.5 h-3.5 text-emerald-500" />
                  <Copy v-else class="w-3.5 h-3.5" />
                </button>
              </div>
            </td>

            <!-- Upload Date -->
            <td class="py-4 px-6 text-xs text-gray-500 dark:text-gray-400">
              {{ formatDate(doc.created_at) }}
            </td>

            <!-- Size -->
            <td class="py-4 px-6 text-xs text-gray-500 dark:text-gray-400 font-mono">
              {{ formatSize(doc.file_size) }}
            </td>

            <!-- Status -->
            <td class="py-4 px-6">
              <StatusBadge :status="doc.status" />
              <div v-if="doc.error_message" class="text-[10px] text-rose-500 mt-1 max-w-[180px] truncate font-medium" :title="doc.error_message">
                {{ doc.error_message }}
              </div>
            </td>

            <!-- Actions -->
            <td class="py-4 px-6 text-right space-x-1">
              <button
                type="button"
                @click.stop="$emit('viewDetails', doc)"
                class="p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors inline-flex items-center"
                title="View Details"
              >
                <Eye class="w-4 h-4" />
              </button>
              <button
                type="button"
                @click.stop="$emit('deleteDoc', doc)"
                class="p-1.5 text-gray-400 hover:text-rose-600 dark:hover:text-rose-400 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors inline-flex items-center"
                title="Delete Document"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FileText, File as FileIcon, Copy, Check, Eye, Trash2, Inbox, RotateCw } from 'lucide-vue-next'
import StatusBadge from '../common/StatusBadge.vue'
import type { DocumentItem } from '../../services/documentService'

defineProps<{
  documents: DocumentItem[]
}>()

defineEmits<{
  (e: 'viewDetails', doc: DocumentItem): void
  (e: 'deleteDoc', doc: DocumentItem): void
}>()

const copiedId = ref<string | null>(null)

const copyId = async (id: string) => {
  await navigator.clipboard.writeText(id)
  copiedId.value = id
  setTimeout(() => {
    copiedId.value = null
  }, 2000)
}

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr)
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}
</script>
