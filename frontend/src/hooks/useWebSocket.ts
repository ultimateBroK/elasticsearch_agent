"use client"

import { useEffect, useRef, useState, useCallback } from 'react'
import { useChatStore } from '@/store/chatStore'
import { WebSocketMessage, WebSocketResponse, MessageType } from '@/types/api'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
const MAX_RETRY_ATTEMPTS = 5
const INITIAL_RETRY_DELAY = 1000 // 1 second
const MAX_RETRY_DELAY = 30000 // 30 seconds
const PING_INTERVAL = 30000 // 30 seconds

interface UseWebSocketReturn {
  isConnected: boolean
  isTyping: boolean
  sendMessage: (message: string) => void
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
  retryConnection: () => void
  disconnect: () => void
}

export function useWebSocket(): UseWebSocketReturn {
  const ws = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  
  const pingInterval = useRef<NodeJS.Timeout | null>(null)
  const retryTimeout = useRef<NodeJS.Timeout | null>(null)
  const retryAttempts = useRef(0)
  const isManualDisconnect = useRef(false)
  
  const { 
    addMessage, 
    setSessionId, 
    sessionId,
    setConnectionStatus: setStoreConnectionStatus,
    incrementRetryCount,
    resetRetryCount,
    addErrorMessage
  } = useChatStore()

  // Calculate retry delay with exponential backoff
  const getRetryDelay = useCallback(() => {
    const delay = Math.min(
      INITIAL_RETRY_DELAY * Math.pow(2, retryAttempts.current),
      MAX_RETRY_DELAY
    )
    return delay + Math.random() * 1000 // Add jitter
  }, [])

  // Start ping interval to keep connection alive
  const startPingInterval = useCallback(() => {
    if (pingInterval.current) {
      clearInterval(pingInterval.current)
    }
    
    pingInterval.current = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        try {
          ws.current.send(JSON.stringify({ type: MessageType.PING }))
        } catch (error) {
          console.error('Failed to send ping:', error)
        }
      }
    }, PING_INTERVAL)
  }, [])

  // Stop ping interval
  const stopPingInterval = useCallback(() => {
    if (pingInterval.current) {
      clearInterval(pingInterval.current)
      pingInterval.current = null
    }
  }, [])

  // Handle WebSocket messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data: WebSocketResponse = JSON.parse(event.data)
      
      switch (data.type) {
        case MessageType.MESSAGE:
          if (data.sender && data.content) {
            addMessage({
              content: data.content,
              sender: data.sender,
              sessionId: sessionId || undefined,
              chartConfig: data.chart_config,
              data: data.data,
              intent: data.intent,
              queryInsight: data.query_insight,
              personalizedSuggestions: data.personalized_suggestions,
              intelligenceMetrics: data.intelligence_metrics
            })
          }
          break
          
        case MessageType.TYPING:
          setIsTyping(true)
          // Auto-clear typing indicator after 5 seconds
          setTimeout(() => setIsTyping(false), 5000)
          break
          
        case MessageType.ERROR:
          console.error('WebSocket error:', data.error)
          addErrorMessage(data.error || 'WebSocket error occurred', true)
          break
          
        case MessageType.PONG:
          // Connection is alive
          break
          
        default:
          console.log('Unknown WebSocket message type:', data.type)
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
    }
  }, [addMessage, sessionId, addErrorMessage])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.CONNECTING || 
        ws.current?.readyState === WebSocket.OPEN) {
      return // Already connecting or connected
    }

    try {
      setConnectionStatus('connecting')
      setStoreConnectionStatus('connecting')
      
      const url = sessionId ? `${WS_URL}?session_id=${sessionId}` : WS_URL
      ws.current = new WebSocket(url)
      
      ws.current.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setConnectionStatus('connected')
        setStoreConnectionStatus('connected')
        
        // Reset retry attempts on successful connection
        retryAttempts.current = 0
        resetRetryCount()
        
        // Start ping interval
        startPingInterval()
      }
      
      ws.current.onmessage = handleMessage
      
      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        setIsTyping(false)
        stopPingInterval()
        
        if (isManualDisconnect.current) {
          setConnectionStatus('disconnected')
          setStoreConnectionStatus('disconnected')
          isManualDisconnect.current = false
          return
        }
        
        // Auto-reconnect if not a manual disconnect
        if (event.code !== 1000 && retryAttempts.current < MAX_RETRY_ATTEMPTS) {
          setConnectionStatus('error')
          setStoreConnectionStatus('error')
          scheduleReconnect()
        } else {
          setConnectionStatus('disconnected')
          setStoreConnectionStatus('disconnected')
          
          if (retryAttempts.current >= MAX_RETRY_ATTEMPTS) {
            addErrorMessage(
              'Connection lost. Maximum retry attempts reached. Please refresh the page.',
              true
            )
          }
        }
      }
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('error')
        setStoreConnectionStatus('error')
      }
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionStatus('error')
      setStoreConnectionStatus('error')
      scheduleReconnect()
    }
  }, [sessionId, handleMessage, startPingInterval, stopPingInterval, setStoreConnectionStatus, resetRetryCount, addErrorMessage])

  // Schedule reconnection with exponential backoff
  const scheduleReconnect = useCallback(() => {
    if (retryTimeout.current) {
      clearTimeout(retryTimeout.current)
    }
    
    if (retryAttempts.current >= MAX_RETRY_ATTEMPTS) {
      return
    }
    
    const delay = getRetryDelay()
    retryAttempts.current++
    incrementRetryCount()
    
    console.log(`Scheduling reconnect attempt ${retryAttempts.current} in ${delay}ms`)
    
    retryTimeout.current = setTimeout(() => {
      if (!isManualDisconnect.current) {
        connect()
      }
    }, delay)
  }, [connect, getRetryDelay, incrementRetryCount])

  // Manual retry connection
  const retryConnection = useCallback(() => {
    retryAttempts.current = 0
    resetRetryCount()
    
    if (retryTimeout.current) {
      clearTimeout(retryTimeout.current)
      retryTimeout.current = null
    }
    
    connect()
  }, [connect, resetRetryCount])

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    isManualDisconnect.current = true
    
    if (retryTimeout.current) {
      clearTimeout(retryTimeout.current)
      retryTimeout.current = null
    }
    
    stopPingInterval()
    
    if (ws.current) {
      ws.current.close(1000, 'Manual disconnect')
      ws.current = null
    }
    
    setIsConnected(false)
    setIsTyping(false)
    setConnectionStatus('disconnected')
    setStoreConnectionStatus('disconnected')
  }, [stopPingInterval, setStoreConnectionStatus])

  // Send message through WebSocket
  const sendMessage = useCallback((content: string) => {
    // Input validation
    if (!content || !content.trim()) {
      console.error('Cannot send empty message')
      return
    }
    
    if (content.length > 1000) {
      addErrorMessage('Message too long. Please keep messages under 1000 characters.')
      return
    }
    
    if (ws.current?.readyState === WebSocket.OPEN) {
      try {
        const message: WebSocketMessage = {
          type: MessageType.MESSAGE,
          message: content.trim(),
          timestamp: new Date().toISOString()
        }
        
        ws.current.send(JSON.stringify(message))
        
        // Add user message to store
        addMessage({
          content: content.trim(),
          sender: 'user',
          sessionId: sessionId || undefined
        })
        
      } catch (error) {
        console.error('Failed to send message:', error)
        addErrorMessage('Failed to send message. Please try again.')
      }
    } else {
      console.error('WebSocket is not connected')
      addErrorMessage('Connection lost. Attempting to reconnect...')
      retryConnection()
    }
  }, [addMessage, sessionId, addErrorMessage, retryConnection])

  // Initialize connection on mount
  useEffect(() => {
    connect()
    
    // Cleanup on unmount
    return () => {
      disconnect()
    }
  }, []) // Empty dependency array - only run on mount/unmount

  // Reconnect when sessionId changes
  useEffect(() => {
    if (sessionId && ws.current?.readyState === WebSocket.OPEN) {
      // Close current connection and reconnect with new session
      disconnect()
      setTimeout(connect, 100) // Small delay to ensure clean disconnect
    }
  }, [sessionId])

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      if (retryTimeout.current) {
        clearTimeout(retryTimeout.current)
      }
      stopPingInterval()
    }
  }, [stopPingInterval])

  return {
    isConnected,
    isTyping,
    sendMessage,
    connectionStatus,
    retryConnection,
    disconnect
  }
}