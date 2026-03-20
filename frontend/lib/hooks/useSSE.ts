import { useEffect, useState, useRef } from 'react'

interface UseSSEOptions {
  onMessage?: (data: any) => void
  onError?: (error: Error) => void
  onComplete?: (data: any) => void
  autoConnect?: boolean
}

export function useSSE(url: string, options: UseSSEOptions = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)
  const [error, setError] = useState<Error | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  const connect = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    eventSource.onopen = () => {
      setIsConnected(true)
      setError(null)
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setLastMessage(data)
        options.onMessage?.(data)
      } catch (err) {
        console.error('Failed to parse SSE message:', err)
      }
    }

    eventSource.addEventListener('complete', (event: any) => {
      try {
        const data = JSON.parse(event.data)
        options.onComplete?.(data)
        eventSource.close()
        setIsConnected(false)
      } catch (err) {
        console.error('Failed to parse complete event:', err)
      }
    })

    eventSource.onerror = (err) => {
      setIsConnected(false)
      setError(new Error('Connection lost'))
      options.onError?.(new Error('Connection lost'))
      eventSource.close()
    }
  }

  const disconnect = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
      setIsConnected(false)
    }
  }

  useEffect(() => {
    if (options.autoConnect !== false && url) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [url])

  return {
    isConnected,
    lastMessage,
    error,
    connect,
    disconnect,
  }
}