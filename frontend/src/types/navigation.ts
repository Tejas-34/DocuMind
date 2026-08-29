import type { Component } from 'vue'

export interface MobileNavItem {
  id: string
  label: string
  path: string
  icon: Component
  ariaLabel: string
}

export const CANONICAL_MIME_TYPES: Record<string, string> = {
  pdf: 'application/pdf',
  txt: 'text/plain',
  md: 'text/markdown',
}

export const ALLOWED_EXTENSIONS = ['pdf', 'txt', 'md'] as const
export type AllowedExtension = (typeof ALLOWED_EXTENSIONS)[number]
