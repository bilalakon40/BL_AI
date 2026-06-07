import { useEffect, useRef, useCallback } from 'react'

type MessageHandler = (data: any) => void

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws'

export function useWebSocket(onMessage: MessageHandler) {
  const wsRef = useRef<WebSocket | null>(null)
  const handlersRef = useRef<MessageHandler>(onMessage)
  handlersRef.current = onMessage

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(WS_URL)
    ws.onopen = () => console.log('WebSocket connected')
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handlersRef.current(data)
      } catch {
        handlersRef.current(event.data)
      }
    }
    ws.onclose = () => {
      console.log('WebSocket disconnected, reconnecting in 5s...')
      setTimeout(connect, 5000)
    }
    ws.onerror = () => ws.close()
    wsRef.current = ws
  }, [])

  useEffect(() => {
    connect()
    return () => {
      wsRef.current?.close()
    }
  }, [connect])

  return wsRef
}
