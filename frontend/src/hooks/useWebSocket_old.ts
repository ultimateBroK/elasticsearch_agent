"use client"

import { useEffect, useRef, useState, useCallback } from 'react'
import { useChatStore } from '@/store/chatStore'

interface WebSocketMessage {
  type: 'connection' | 'message' | 'typing' | 'error' | 'pong'
  sender?: 'user' | 'agent'
  content?: string
  chart_config?: any
  data?: any[]
  intent?: string
  timestamp?: string
  is_typing?: boolean
  message?: string
  session_id?: string
  status?: string
}

interface UseWebSocketReturn {
  isConnected: boolean
  isTyping: boolean
  sendMessage: (message: string) => void
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
}

export function useWebSocket(): UseWebSocketReturn {
  const ws = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  
  const { addMessage, setSessionId, sessionId } = useChatStore()
  
  // Ping interval to keep connection alive
  const pingInterval = useRef<NodeJS.Timeout | null>(null)
  
  const connect = useCallback(() => {
    try {
      setConnectionStatus('connecting')
      
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
      const url = sessionId ? `${wsUrl}?session_id=${sessionId}` : wsUrl
      
      ws.current = new WebSocket(url)
      
      ws.current.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setConnectionStatus('connected')
        
        // Start ping interval
        pingInterval.current = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'ping' }))
          }
        }, 30000) // Ping every 30 seconds
      }
      
      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        setConnectionStatus('disconnected')
        setIsTyping(false)
        
        if (pingInterval.current) {
          clearInterval(pingInterval.current)
          pingInterval.current = null
        }
        
        // Only auto-reconnect if it wasn't a manual close
        if (event.code !== 1000) {
          setTimeout(() => {
            if (!isConnected) {
              console.log('Attempting to reconnect...')
              connect()
            }
          }, 3000)
        }
      }
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('error')
      }
      
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      setConnectionStatus('error')
    }
  }, [sessionId, isConnected])
  
  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'connection':
        if (message.session_id) {
          setSessionId(message.session_id)
        }
        if (message.message) {
          addMessage({
            content: message.message,
            sender: 'agent'
          })
        }
        break
        
      case 'message':
        if (message.sender && message.content) {
          addMessage({
            content: message.content,
            sender: message.sender,
            chartConfig: message.chart_config,
            data: message.data
          })
        }
        break
        
      case 'typing':
        setIsTyping(message.is_typing || false)
        break
        
      case 'error':
        if (message.message) {
          addMessage({
            content: `Error: ${message.message}`,
            sender: 'agent'
          })
        }
        break
        
      case 'pong':
        // Heartbeat response - connection is alive
        break
        
      default:
        console.log('Unknown message type:', message.type)
    }
  }, [addMessage, setSessionId])
  
  const sendMessage = useCallback((content: string) => {
    // Input validation
    if (!content || !content.trim()) {
      console.error('Cannot send empty message')
      return
    }
    
    if (content.length > 1000) {
      addMessage({
        content: 'Message too long. Please keep messages under 1000 characters.',
        sender: 'agent'
      })
      return
    }
    
    if (ws.current?.readyState === WebSocket.OPEN) {
      try {
        const message = {
          type: 'message',
          message: content.trim(),
          timestamp: new Date().toISOString()
        }
        
        ws.current.send(JSON.stringify(message))
      } catch (error) {
        console.error('Failed to send message:', error)
        addMessage({
          content: 'Failed to send message. Please try again.',
          sender: 'agent'
        })
      }
    } else {
      console.error('WebSocket is not connected')
      addMessage({
        content: 'Connection lost. Please wait while we reconnect...',
        sender: 'agent'
      })
    }
  }, [addMessage])
  
  // Connect on mount
  useEffect(() => {
    connect()
    
    return () => {
      if (pingInterval.current) {
        clearInterval(pingInterval.current)
      }
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [connect])
  
  return {
    isConnected,
    isTyping,
    sendMessage,
    connectionStatus
  }
} 