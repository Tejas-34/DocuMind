import { ref, onUnmounted } from 'vue'

export interface WebSocketCallbacks {
  onToken?: (token: string) => void
  onStatus?: (status: { step: string; message: string }) => void
  onDone?: (payload: {
    message_id: string
    client_msg_id?: string
    role: string
    content: string
    citations?: any[]
  }) => void
  onContextCleared?: () => void
  onError?: (error: { message: string }) => void
}

export function useChatWebSocket() {
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const isReconnecting = ref(false)
  const statusMessage = ref('')
  
  let pingInterval: any = null
  let reconnectTimeout: any = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 5
  
  let currentSessionId = ''
  let currentToken = ''
  let activeCallbacks: WebSocketCallbacks = {}

  const connect = (sessionId: string, token: string, callbacks: WebSocketCallbacks = {}) => {
    currentSessionId = sessionId
    currentToken = token
    activeCallbacks = callbacks

    // Close previous socket if any
    disconnect()

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/api/v1/ws/chat/${sessionId}?token=${encodeURIComponent(token)}`

    try {
      socket.value = new WebSocket(wsUrl)

      socket.value.onopen = () => {
        isConnected.value = true
        isReconnecting.value = false
        reconnectAttempts = 0
        statusMessage.value = ''
        startHeartbeat()
      }

      socket.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleIncomingFrame(data)
        } catch (e) {
          console.error('Failed to parse WebSocket message frame:', e)
        }
      }

      socket.value.onclose = (event) => {
        isConnected.value = false
        stopHeartbeat()
        
        // Code 1000 is normal closure
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
          scheduleReconnect()
        }
      }

      socket.value.onerror = (err) => {
        console.error('WebSocket connection error:', err)
      }
    } catch (e) {
      console.error('Failed to establish WebSocket connection:', e)
      scheduleReconnect()
    }
  }

  const handleIncomingFrame = (data: any) => {
    switch (data.type) {
      case 'status':
        statusMessage.value = data.message || ''
        if (activeCallbacks.onStatus) activeCallbacks.onStatus(data)
        break
      case 'token':
        if (activeCallbacks.onToken) activeCallbacks.onToken(data.content)
        break
      case 'done':
        statusMessage.value = ''
        if (activeCallbacks.onDone) activeCallbacks.onDone(data)
        break
      case 'context_cleared':
        if (activeCallbacks.onContextCleared) activeCallbacks.onContextCleared()
        break
      case 'error':
        statusMessage.value = ''
        if (activeCallbacks.onError) activeCallbacks.onError(data)
        break
      case 'pong':
        break
      default:
        break
    }
  }

  const sendQuery = (text: string, clientMsgId?: string) => {
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
      console.warn('Cannot send query; WebSocket is not open.')
      return false
    }

    socket.value.send(
      JSON.stringify({
        type: 'query',
        text,
        client_msg_id: clientMsgId,
      })
    )
    return true
  }

  const clearContext = () => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify({ type: 'clear_context' }))
    }
  }

  const cancelStream = () => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify({ type: 'cancel' }))
    }
  }

  const startHeartbeat = () => {
    stopHeartbeat()
    pingInterval = setInterval(() => {
      if (socket.value && socket.value.readyState === WebSocket.OPEN) {
        socket.value.send(JSON.stringify({ type: 'ping' }))
      }
    }, 25000)
  }

  const stopHeartbeat = () => {
    if (pingInterval) {
      clearInterval(pingInterval)
      pingInterval = null
    }
  }

  const scheduleReconnect = () => {
    if (reconnectTimeout) clearTimeout(reconnectTimeout)
    isReconnecting.value = true
    reconnectAttempts++
    
    // Exponential backoff: 1s, 2s, 4s, 8s, max 30s
    const backoffTime = Math.min(1000 * Math.pow(2, reconnectAttempts - 1), 30000)
    statusMessage.value = `Connection lost. Reconnecting in ${Math.round(backoffTime / 1000)}s...`

    reconnectTimeout = setTimeout(() => {
      if (currentSessionId && currentToken) {
        connect(currentSessionId, currentToken, activeCallbacks)
      }
    }, backoffTime)
  }

  const disconnect = () => {
    stopHeartbeat()
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
    if (socket.value) {
      socket.value.close(1000, 'Component unmounted or session changed')
      socket.value = null
    }
    isConnected.value = false
    isReconnecting.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    socket,
    isConnected,
    isReconnecting,
    statusMessage,
    connect,
    disconnect,
    sendQuery,
    clearContext,
    cancelStream,
  }
}
