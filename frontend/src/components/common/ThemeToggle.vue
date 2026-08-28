<template>
  <button
    type="button"
    @click="toggleTheme"
    class="p-2 rounded-xl text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
    :title="theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
    aria-label="Toggle Theme"
  >
    <Sun v-if="theme === 'dark'" class="w-4 h-4 text-amber-400" />
    <Moon v-else class="w-4 h-4 text-[#153826]" />
  </button>
</template>

<script setup lang="ts">
import { Sun, Moon } from 'lucide-vue-next'
import { useTheme } from '../../composables/useTheme'

const { theme, toggleTheme } = useTheme()
</script>
