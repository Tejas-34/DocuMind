<template>
  <button
    @click="toggleTheme"
    class="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
    :title="theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
    aria-label="Toggle Theme"
  >
    <Sun v-if="theme === 'dark'" class="w-5 h-5 text-amber-400" />
    <Moon v-else class="w-5 h-5 text-indigo-600" />
  </button>
</template>

<script setup lang="ts">
import { Sun, Moon } from 'lucide-vue-next'
import { useTheme } from '../../composables/useTheme'

const { theme, toggleTheme } = useTheme()
</script>
