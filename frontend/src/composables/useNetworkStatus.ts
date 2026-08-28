import { ref, onMounted, onUnmounted } from 'vue'

export function useNetworkStatus() {
  const isOnline = ref(typeof navigator !== 'undefined' ? navigator.onLine : true)
  const isRecentlyReconnected = ref(false)

  let dismissTimeout: any = null

  const handleOnline = () => {
    isOnline.value = true
    isRecentlyReconnected.value = true

    if (dismissTimeout) clearTimeout(dismissTimeout)
    dismissTimeout = setTimeout(() => {
      isRecentlyReconnected.value = false
    }, 4000)
  }

  const handleOffline = () => {
    isOnline.value = false
    isRecentlyReconnected.value = false
    if (dismissTimeout) clearTimeout(dismissTimeout)
  }

  onMounted(() => {
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
  })

  onUnmounted(() => {
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
    if (dismissTimeout) clearTimeout(dismissTimeout)
  })

  return {
    isOnline,
    isRecentlyReconnected,
  }
}
