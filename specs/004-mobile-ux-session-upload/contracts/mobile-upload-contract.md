# Contract: Mobile Upload Validation & Normalization

**Feature Branch**: `004-mobile-ux-session-upload` | **Date**: 2026-08-29

---

## 1. File Input Contract (`DragDropZone.vue`)

### HTML Input Definition
```html
<input
  ref="fileInput"
  type="file"
  class="hidden"
  accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown,application/octet-stream"
  @change="handleFileInput"
  multiple
/>
```

### Event Lifecycle & Input Reset Contract
```typescript
const triggerBrowse = () => {
  if (fileInput.value) {
    fileInput.value.value = '' // Reset before trigger to ensure iOS change event fires
    fileInput.value.click()
  }
}

const handleFileInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  validateAndEmit(target.files)
  if (fileInput.value) {
    fileInput.value.value = '' // Reset after emit to allow selecting same file again
  }
}
```

---

## 2. File Normalization & Validation Contract

### Validation Function
```typescript
const ALLOWED_EXTENSIONS = ['pdf', 'txt', 'md'] as const
const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024 // 25MB

const CANONICAL_MIME_MAP: Record<string, string> = {
  pdf: 'application/pdf',
  txt: 'text/plain',
  md: 'text/markdown',
}

export function normalizeAndValidateFile(file: File): { valid: boolean; error?: string; file?: File } {
  const ext = file.name.split('.').pop()?.toLowerCase() || ''
  
  if (!ALLOWED_EXTENSIONS.includes(ext as any)) {
    return {
      valid: false,
      error: `File "${file.name}" is unsupported. Only PDF, TXT, and MD are allowed.`,
    }
  }

  if (file.size === 0) {
    return {
      valid: false,
      error: `File "${file.name}" is empty (0 bytes).`,
    }
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      valid: false,
      error: `File "${file.name}" exceeds maximum allowed size of 25MB.`,
    }
  }

  // Normalize MIME type for mobile browsers that assign generic or empty types
  const canonicalMime = CANONICAL_MIME_MAP[ext] || 'application/octet-stream'
  const isGeneric = !file.type || file.type === 'application/octet-stream'
  
  const normalizedFile = isGeneric
    ? new File([file], file.name, { type: canonicalMime, lastModified: file.lastModified })
    : file

  return {
    valid: true,
    file: normalizedFile,
  }
}
```
