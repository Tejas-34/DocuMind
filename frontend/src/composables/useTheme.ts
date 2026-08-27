import { ref } from 'vue'

export type Theme = 'light' | 'dark'

const currentTheme = ref<Theme>('light')

export function useTheme() {
  const initTheme = () => {
    const savedTheme = localStorage.getItem('documind_theme') as Theme | null
    if (savedTheme) {
      currentTheme.value = savedTheme
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      currentTheme.value = 'dark'
    } else {
      currentTheme.value = 'light'
    }
    applyTheme(currentTheme.value)
  }

  const applyTheme = (theme: Theme) => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('documind_theme', theme)
  }

  const toggleTheme = () => {
    currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
    applyTheme(currentTheme.value)
  }

  return {
    theme: currentTheme,
    initTheme,
    toggleTheme,
  }
}
