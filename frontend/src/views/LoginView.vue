<template>
  <div class="min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 sm:p-8 lg:p-12">
    <!-- Main 2-Column Container -->
    <div class="max-w-5xl w-full mx-auto my-auto grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
      <!-- Left Column: Value Proposition & Brand Features -->
      <div class="space-y-8">
        <div class="space-y-3">
          <h1 class="text-3xl sm:text-4xl font-bold text-[#153826] dark:text-emerald-400 tracking-tight">
            Welcome back
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed max-w-md">
            Sign in to access your secure, tenant-isolated document workspace.
          </p>
        </div>

        <!-- 3 Feature Highlight Rows -->
        <div class="space-y-6 pt-2">
          <!-- Feature 1 -->
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-100 dark:border-emerald-900/50 flex items-center justify-center text-[#153826] dark:text-emerald-400 shrink-0">
              <ShieldCheck class="w-5 h-5" />
            </div>
            <div>
              <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100">Secure & Private</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Your data is encrypted and isolated.</p>
            </div>
          </div>

          <!-- Feature 2 -->
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-100 dark:border-emerald-900/50 flex items-center justify-center text-[#153826] dark:text-emerald-400 shrink-0">
              <Sparkles class="w-5 h-5" />
            </div>
            <div>
              <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100">AI-Powered Q&A</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Get answers grounded in your documents.</p>
            </div>
          </div>

          <!-- Feature 3 -->
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-100 dark:border-emerald-900/50 flex items-center justify-center text-[#153826] dark:text-emerald-400 shrink-0">
              <Search class="w-5 h-5" />
            </div>
            <div>
              <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100">Smart Retrieval</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Advanced search across your files.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Floating Auth Card -->
      <div class="w-full max-w-md mx-auto bg-white dark:bg-[#121915] rounded-3xl border border-gray-100 dark:border-gray-800/90 shadow-xl shadow-black/5 dark:shadow-black/20 p-8 sm:p-10 space-y-6">
        <!-- Top Card Icon & Title -->
        <div class="text-center space-y-3">
          <div class="w-10 h-10 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-100 dark:border-emerald-900/40 flex items-center justify-center text-[#153826] dark:text-emerald-400 mx-auto">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 3c-1.5 3-4 5-8 6 3 2 5 5 5 9 1-4 3-6 7-7-3-2-4-5-4-8z"/>
            </svg>
          </div>
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">
            Sign in to your account
          </h2>
        </div>

        <!-- Error Notice -->
        <div
          v-if="authStore.error"
          class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200/80 dark:border-rose-800/60 text-rose-600 dark:text-rose-400 text-xs font-medium flex items-center gap-2"
        >
          <AlertCircle class="w-4 h-4 shrink-0" />
          <span>{{ authStore.error }}</span>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Email Input -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Email address
            </label>
            <div class="relative">
              <Mail class="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                v-model="email"
                type="email"
                required
                placeholder="you@example.com"
                class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700/80 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-[#153826] focus:border-[#153826] focus:outline-none transition-all"
              />
            </div>
          </div>

          <!-- Password Input -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Password
            </label>
            <div class="relative">
              <Lock class="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="••••••••"
                class="w-full pl-10 pr-10 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700/80 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-[#153826] focus:border-[#153826] focus:outline-none transition-all"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                tabindex="-1"
              >
                <EyeOff v-if="showPassword" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Forgot Password Link -->
          <div class="flex justify-end">
            <a href="#" class="text-[11px] text-gray-500 dark:text-gray-400 hover:text-[#153826] dark:hover:text-emerald-400 transition-colors">
              Forgot password?
            </a>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="w-full py-3 bg-[#153826] hover:bg-[#1b4932] text-white font-medium rounded-xl text-sm shadow-xs transition-all flex items-center justify-center gap-2 disabled:opacity-60 cursor-pointer active:scale-[0.99]"
          >
            <Loader2 v-if="authStore.isLoading" class="w-4 h-4 animate-spin" />
            <span>{{ authStore.isLoading ? 'Signing In...' : 'Sign in' }}</span>
            <ArrowRight v-if="!authStore.isLoading" class="w-4 h-4" />
          </button>
        </form>

        <!-- Bottom Link -->
        <div class="text-center pt-2 text-xs text-gray-500 dark:text-gray-400">
          Don't have an account?
          <RouterLink to="/register" class="text-[#153826] dark:text-emerald-400 font-bold hover:underline ml-1">
            Create account
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Footer Security Notice -->
    <div class="text-center pt-8 pb-2 flex items-center justify-center gap-1.5 text-xs text-gray-400 dark:text-gray-500">
      <Lock class="w-3 h-3" />
      <span>© 2026 DocuMind. All rights reserved.</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ShieldCheck, Sparkles, Search, Mail, Lock, Eye, EyeOff, ArrowRight, AlertCircle, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const showPassword = ref(false)

const handleLogin = async () => {
  const success = await authStore.login(email.value, password.value)
  if (success) {
    const redirectPath = (route.query.redirect as string) || '/documents'
    router.push(redirectPath)
  }
}
</script>
