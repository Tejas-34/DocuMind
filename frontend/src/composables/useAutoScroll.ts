import { ref, onMounted, onUnmounted, nextTick, type Ref } from 'vue'

export function useAutoScroll(containerRef: Ref<HTMLElement | null>) {
  const isPinnedToBottom = ref(true)
  const threshold = 60 // pixels from bottom to consider "pinned"

  const checkScrollPosition = () => {
    if (!containerRef.value) return
    const { scrollTop, scrollHeight, clientHeight } = containerRef.value
    const distanceFromBottom = scrollHeight - (scrollTop + clientHeight)
    isPinnedToBottom.value = distanceFromBottom <= threshold
  }

  const scrollToBottom = async (force: boolean = false) => {
    await nextTick()
    if (!containerRef.value) return

    if (force || isPinnedToBottom.value) {
      containerRef.value.scrollTo({
        top: containerRef.value.scrollHeight,
        behavior: 'smooth',
      })
    }
  }

  const attachScrollListener = () => {
    if (containerRef.value) {
      containerRef.value.addEventListener('scroll', checkScrollPosition, { passive: true })
    }
  }

  const detachScrollListener = () => {
    if (containerRef.value) {
      containerRef.value.removeEventListener('scroll', checkScrollPosition)
    }
  }

  onMounted(() => {
    attachScrollListener()
  })

  onUnmounted(() => {
    detachScrollListener()
  })

  return {
    isPinnedToBottom,
    scrollToBottom,
    checkScrollPosition,
  }
}
