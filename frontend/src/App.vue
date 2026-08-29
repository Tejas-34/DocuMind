<template>
  <div class="min-h-screen flex flex-col bg-gray-50 text-gray-900 dark:bg-[#070d0a] dark:text-gray-100 font-sans transition-colors duration-200">
    <AppNavbar />

    <main class="flex-1 overflow-y-auto">
      <RouterView />
    </main>

    <MobileNavBar />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useTheme } from './composables/useTheme'
import AppNavbar from './components/layout/AppNavbar.vue'
import MobileNavBar from './components/layout/MobileNavBar.vue'

const authStore = useAuthStore()
const { initTheme } = useTheme()
onMounted(() => {
  initTheme()
  if (authStore.isAuthenticated) {
    authStore.fetchCurrentUser()
  }
})
</script>
