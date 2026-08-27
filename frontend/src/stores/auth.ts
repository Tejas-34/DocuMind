import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService, type User } from '../services/authService'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('documind_token'))
  const user = ref<User | null>(
    localStorage.getItem('documind_user')
      ? JSON.parse(localStorage.getItem('documind_user')!)
      : null
  )
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  const setAuth = (accessToken: string, userData: User) => {
    token.value = accessToken
    user.value = userData
    localStorage.setItem('documind_token', accessToken)
    localStorage.setItem('documind_user', JSON.stringify(userData))
  }

  const clearAuth = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('documind_token')
    localStorage.removeItem('documind_user')
  }

  const register = async (email: string, pass: string) => {
    isLoading.value = true
    error.value = null
    try {
      const data = await authService.register(email, pass)
      setAuth(data.access_token, data.user)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed.'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const login = async (email: string, pass: string) => {
    isLoading.value = true
    error.value = null
    try {
      const data = await authService.login(email, pass)
      setAuth(data.access_token, data.user)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed.'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return
    try {
      const userData = await authService.getMe()
      user.value = userData
      localStorage.setItem('documind_user', JSON.stringify(userData))
    } catch (e) {
      clearAuth()
    }
  }

  const logout = () => {
    clearAuth()
  }

  return {
    token,
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    fetchCurrentUser,
  }
})
