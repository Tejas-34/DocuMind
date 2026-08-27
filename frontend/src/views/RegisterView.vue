<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-xl p-8 space-y-6">
      <div class="text-center space-y-2">
        <div class="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center text-white mx-auto shadow-md shadow-indigo-500/20">
          <Bot class="w-6 h-6" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Create your account</h2>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Get started with your private, secure Document Q&A assistant.
        </p>
      </div>

      <div v-if="authStore.error" class="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-800 text-rose-600 dark:text-rose-400 text-xs font-medium flex items-center gap-2">
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ authStore.error }}</span>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Email Address</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="you@example.com"
            class="w-full px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-all"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Password</label>
          <input
            v-model="password"
            type="password"
            required
            minlength="8"
            placeholder="At least 8 characters"
            class="w-full px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-all"
          />
        </div>

        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-sm shadow-md shadow-indigo-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-60"
        >
          <Loader2 v-if="authStore.isLoading" class="w-4 h-4 animate-spin" />
          <span>{{ authStore.isLoading ? 'Creating Account...' : 'Get Started' }}</span>
        </button>
      </form>

      <div class="text-center pt-2 text-xs text-gray-500 dark:text-gray-400">
        Already have an account?
        <RouterLink to="/login" class="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline ml-1">
          Sign in
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Bot, AlertCircle, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')

const handleRegister = async () => {
  const success = await authStore.register(email.value, password.value)
  if (success) {
    router.push('/documents')
  }
}
</script>
