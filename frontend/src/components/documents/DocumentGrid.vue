<template>
  <div class="bg-white dark:bg-[#0a130f] rounded-2xl border border-gray-200 dark:border-gray-800/90 shadow-sm dark:shadow-xl overflow-hidden transition-colors duration-200">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white dark:bg-[#0a130f]">
      <!-- Left: Title & Count -->
      <div class="flex items-center gap-2.5">
        <FileText class="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
        <h3 class="font-bold text-sm text-gray-900 dark:text-gray-100">
          Document Library
        </h3>
        <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 dark:bg-[#0e271a] text-emerald-800 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/50">
          {{ filteredDocs.length }}
        </span>
      </div>

      <!-- Right: Search, Filter, Refresh Controls -->
      <div class="flex items-center gap-2">
        <!-- Search Input -->
        <div class="relative">
          <Search class="w-3.5 h-3.5 text-gray-400 dark:text-gray-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search documents..."
            class="pl-8 pr-3 py-1.5 rounded-xl bg-gray-50 dark:bg-[#09140e] border border-gray-200 dark:border-gray-800 text-xs text-gray-900 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-emerald-600 dark:focus:border-emerald-600 w-36 sm:w-48 transition-colors"
          />
        </div>

        <!-- Status Filter Dropdown -->
        <div class="relative">
          <select
            v-model="statusFilter"
            class="appearance-none pl-3 pr-8 py-1.5 rounded-xl bg-gray-50 dark:bg-[#09140e] border border-gray-200 dark:border-gray-800 text-xs text-gray-700 dark:text-gray-300 focus:outline-none focus:border-emerald-600 cursor-pointer"
          >
            <option value="all">All Status</option>
            <option value="ready">Ready</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
          <ChevronDown class="w-3.5 h-3.5 text-gray-400 dark:text-gray-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>

        <!-- Refresh Button -->
        <button
          type="button"
          @click="handleRefresh"
          class="p-1.5 rounded-xl bg-gray-50 dark:bg-[#09140e] border border-gray-200 dark:border-gray-800 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-gray-700 transition-colors"
          title="Refresh library"
        >
          <RotateCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isRefreshing }" />
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredDocs.length === 0" class="p-12 text-center">
      <Inbox class="w-10 h-10 text-gray-400 dark:text-gray-600 mx-auto mb-3 opacity-60" />
      <p class="text-sm font-semibold text-gray-800 dark:text-gray-200">
        {{ searchQuery || statusFilter !== 'all' ? 'No matching documents found' : 'No documents uploaded yet' }}
      </p>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-xs mx-auto">
        {{ searchQuery || statusFilter !== 'all' ? 'Try adjusting your search query or status filter.' : 'Drag and drop a PDF or text file into the upload zone above to enable Q&A.' }}
      </p>
    </div>

    <!-- Responsive Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-left text-sm min-w-[720px] border-collapse">
        <thead class="border-b border-gray-100 dark:border-gray-800/80 text-[10px] text-gray-500 dark:text-gray-400 font-semibold uppercase tracking-wider select-none bg-gray-50/70 dark:bg-[#08100c]/40">
          <tr>
            <th class="py-3 px-6">FILE NAME</th>
            <th class="py-3 px-6">DOCUMENT ID</th>
            <th class="py-3 px-6">UPLOADED ON</th>
            <th class="py-3 px-6">SIZE</th>
            <th class="py-3 px-6">STATUS</th>
            <th class="py-3 px-6 text-right">ACTIONS</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-800/40">
          <tr
            v-for="doc in paginatedDocs"
            :key="doc.id"
            class="hover:bg-gray-50/60 dark:hover:bg-white/[0.02] transition-colors duration-150 cursor-default group"
          >
            <!-- Filename -->
            <td class="py-3.5 px-6 font-medium text-gray-900 dark:text-gray-100">
              <div class="flex items-center gap-3">
                <!-- PDF Badge -->
                <div
                  v-if="doc.filename.toLowerCase().endsWith('.pdf')"
                  class="w-7 h-6 rounded bg-rose-500 text-white font-bold text-[9px] flex items-center justify-center shrink-0 tracking-tight shadow-xs"
                >
                  PDF
                </div>
                <!-- TXT / MD Icon Box -->
                <div
                  v-else
                  class="w-7 h-7 rounded-lg bg-emerald-50 dark:bg-[#0e271a] border border-emerald-200 dark:border-emerald-800/50 text-emerald-700 dark:text-emerald-400 flex items-center justify-center shrink-0"
                >
                  <FileIcon class="w-3.5 h-3.5" />
                </div>
                <span class="truncate max-w-[240px] font-medium text-xs text-gray-900 dark:text-gray-100" :title="doc.filename">
                  {{ doc.filename }}
                </span>
              </div>
            </td>

            <!-- Document UUID with copy button -->
            <td class="py-3.5 px-6 font-mono text-xs text-gray-500 dark:text-gray-400">
              <div class="flex items-center gap-2">
                <span class="truncate max-w-[130px] bg-gray-100 dark:bg-[#09140e] border border-gray-200 dark:border-gray-800 px-2 py-0.5 rounded-lg text-[11px]" :title="doc.id">
                  {{ doc.id }}
                </span>
                <button
                  type="button"
                  @click.stop="copyId(doc.id)"
                  class="p-1 text-gray-400 hover:text-emerald-700 dark:hover:text-emerald-400 transition-colors"
                  :title="copiedId === doc.id ? 'Copied!' : 'Copy Document ID'"
                >
                  <Check v-if="copiedId === doc.id" class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  <Copy v-else class="w-3.5 h-3.5" />
                </button>
              </div>
            </td>

            <!-- Upload Date -->
            <td class="py-3.5 px-6 text-xs text-gray-500 dark:text-gray-400">
              {{ formatDate(doc.created_at) }}
            </td>

            <!-- Size -->
            <td class="py-3.5 px-6 text-xs text-gray-500 dark:text-gray-400 font-mono">
              {{ formatSize(doc.file_size) }}
            </td>

            <!-- Status -->
            <td class="py-3.5 px-6">
              <span
                v-if="doc.status === 'ready'"
                class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 dark:bg-[#092215] text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400"></span>
                Ready
              </span>
              <span
                v-else-if="doc.status === 'processing' || doc.status === 'uploading'"
                class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 dark:bg-[#261905] text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800/60 animate-pulse"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-amber-500 dark:bg-amber-400"></span>
                Processing
              </span>
              <span
                v-else
                class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-50 dark:bg-[#290c10] text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-800/60"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-rose-500 dark:bg-rose-400"></span>
                Failed
              </span>
            </td>

            <!-- Actions -->
            <td class="py-3.5 px-6 text-right space-x-1.5">
              <button
                type="button"
                @click.stop="$emit('viewDetails', doc)"
                class="p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/[0.04] rounded-lg transition-colors inline-flex items-center"
                title="View Details"
              >
                <Eye class="w-4 h-4" />
              </button>
              <button
                type="button"
                @click.stop="$emit('deleteDoc', doc)"
                class="p-1.5 text-gray-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg transition-colors inline-flex items-center"
                title="Delete Document"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination / Footer Bar -->
    <div
      v-if="filteredDocs.length > 0"
      class="px-6 py-3.5 border-t border-gray-100 dark:border-gray-800/80 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 bg-gray-50/50 dark:bg-[#08100c]/40"
    >
      <div>
        Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, filteredDocs.length) }} of {{ filteredDocs.length }} documents
      </div>

      <div class="flex items-center gap-1.5">
        <button
          type="button"
          @click="currentPage--"
          :disabled="currentPage === 1"
          class="p-1.5 rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-[#09140e] text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          title="Previous page"
        >
          <ChevronLeft class="w-3.5 h-3.5" />
        </button>

        <button
          v-for="page in totalPages"
          :key="page"
          type="button"
          @click="currentPage = page"
          class="px-2.5 py-0.5 rounded-lg text-xs font-semibold transition-colors"
          :class="
            currentPage === page
              ? 'bg-emerald-50 dark:bg-[#0e271a] border border-emerald-300 dark:border-emerald-700/60 text-emerald-800 dark:text-emerald-400'
              : 'border border-gray-200 dark:border-gray-800 bg-white dark:bg-[#09140e] text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:text-white'
          "
        >
          {{ page }}
        </button>

        <button
          type="button"
          @click="currentPage++"
          :disabled="currentPage === totalPages || totalPages === 0"
          class="p-1.5 rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-[#09140e] text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          title="Next page"
        >
          <ChevronRight class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  FileText,
  File as FileIcon,
  Copy,
  Check,
  Eye,
  Trash2,
  Inbox,
  RotateCw,
  Search,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
} from 'lucide-vue-next'
import type { DocumentItem } from '../../services/documentService'

const props = defineProps<{
  documents: DocumentItem[]
}>()

const emit = defineEmits<{
  (e: 'viewDetails', doc: DocumentItem): void
  (e: 'deleteDoc', doc: DocumentItem): void
  (e: 'refresh'): void
}>()

const searchQuery = ref('')
const statusFilter = ref<'all' | 'ready' | 'processing' | 'failed'>('all')
const copiedId = ref<string | null>(null)
const isRefreshing = ref(false)

const currentPage = ref(1)
const pageSize = ref(10)

const filteredDocs = computed(() => {
  return props.documents.filter((doc) => {
    // Search query match
    const matchesSearch =
      !searchQuery.value.trim() ||
      doc.filename.toLowerCase().includes(searchQuery.value.toLowerCase().trim()) ||
      doc.id.toLowerCase().includes(searchQuery.value.toLowerCase().trim())

    // Status filter match
    const matchesStatus =
      statusFilter.value === 'all' ||
      (statusFilter.value === 'ready' && doc.status === 'ready') ||
      (statusFilter.value === 'processing' && (doc.status === 'processing' || doc.status === 'uploading')) ||
      (statusFilter.value === 'failed' && doc.status === 'failed')

    return matchesSearch && matchesStatus
  })
})

const totalPages = computed(() => {
  return Math.ceil(filteredDocs.value.length / pageSize.value) || 1
})

const paginatedDocs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredDocs.value.slice(start, start + pageSize.value)
})

const copyId = async (id: string) => {
  await navigator.clipboard.writeText(id)
  copiedId.value = id
  setTimeout(() => {
    copiedId.value = null
  }, 2000)
}

const handleRefresh = () => {
  isRefreshing.value = true
  emit('refresh')
  setTimeout(() => {
    isRefreshing.value = false
  }, 600)
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
