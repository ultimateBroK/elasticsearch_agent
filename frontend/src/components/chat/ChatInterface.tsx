"use client"

import { useEffect, useState } from "react"
import { useChatStore } from "@/store/chatStore"
import { apiClient, ApiError } from "@/lib/api"
import { useWebSocket } from "@/hooks/useWebSocket"
import { MessageList } from "./MessageList"
import { MessageInput } from "./MessageInput"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ServiceStatus } from "@/types/api"
import { StatusIndicator } from "@/components/StatusIndicator"
import { useConnectionStatus } from "@/hooks/useConnectionStatus"
import { useSession } from "@/hooks/useSession"

export function ChatInterface() {
  const { 
    messages, 
    isLoading, 
    connection,
    setBackendHealth,
    addErrorMessage,
    sessionId,
    setSessionId
  } = useChatStore()
  
  // WebSocket for real-time communication
  const { 
    isConnected, 
    isTyping, 
    sendMessage, 
    connectionStatus: wsConnectionStatus,
    retryConnection,
    disconnect
  } = useWebSocket()
  
  const [useWebSocketMode, setUseWebSocketMode] = useState(true)
  
  // Use enhanced connection status
  const connectionStatus = useConnectionStatus()
  
  // Use session management
  const session = useSession()

  // Health checking is now handled by useConnectionStatus hook

  const handleSendMessage = async (messageContent: string) => {
    if (useWebSocketMode && isConnected) {
      // Use WebSocket for real-time communication
      sendMessage(messageContent)
    } else {
      // Fallback to REST API
      await handleRestApiMessage(messageContent)
    }
  }

  const handleRestApiMessage = async (messageContent: string) => {
    const { addMessage, setLoading } = useChatStore.getState()
    
    // Add user message
    addMessage({
      content: messageContent,
      sender: 'user',
      sessionId: sessionId || undefined
    })

    setLoading(true)

    try {
      // Send to backend with timeout
      const response = await apiClient.sendMessage({
        message: messageContent,
        session_id: sessionId || undefined
      })

      // Update session ID if new
      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id)
      }

      // Add agent response
      addMessage({
        content: response.response,
        sender: 'agent',
        sessionId: response.session_id,
        chartConfig: response.chart_config,
        data: response.data,
        queryInsight: response.query_insight,
        personalizedSuggestions: response.personalized_suggestions,
        intelligenceMetrics: response.intelligence_metrics
      })

    } catch (error) {
      console.error('Failed to send message:', error)
      
      let errorMessage = 'Sorry, I couldn\'t process your message.'
      let retryable = true
      
      if (error instanceof ApiError) {
        switch (error.status) {
          case 400:
            errorMessage = 'Invalid message format. Please try again.'
            retryable = false
            break
          case 408:
            errorMessage = 'Request timed out. Please try a simpler query.'
            break
          case 429:
            errorMessage = 'Too many requests. Please wait a moment before trying again.'
            break
          case 503:
            errorMessage = 'Service temporarily unavailable. Please try again later.'
            break
          default:
            errorMessage = error.message || errorMessage
        }
      }
      
      addErrorMessage(errorMessage, retryable)
      
    } finally {
      setLoading(false)
    }
  }

  const handleRetryConnection = () => {
    if (useWebSocketMode) {
      retryConnection()
    } else {
      connectionStatus.checkBackendHealth()
    }
  }

  const handleRetryMessage = (messageId: string) => {
    // Find the message and get the original user message that caused the error
    const messageIndex = messages.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    // Look for the user message that preceded this error
    let userMessage = null
    for (let i = messageIndex - 1; i >= 0; i--) {
      if (messages[i].sender === 'user') {
        userMessage = messages[i].content
        break
      }
    }

    if (userMessage) {
      // Remove the error message and retry
      const { messages: currentMessages, setLoading } = useChatStore.getState()
      const filteredMessages = currentMessages.filter(m => m.id !== messageId)
      useChatStore.setState({ messages: filteredMessages })
      
      // Retry the message
      handleSendMessage(userMessage)
    }
  }

  const handleUserFeedback = async (feedback: { satisfaction: number; chart_rating: number }) => {
    try {
      // Send feedback to backend for learning
      await apiClient.submitFeedback({
        session_id: sessionId,
        satisfaction: feedback.satisfaction,
        chart_rating: feedback.chart_rating,
        response_quality: feedback.satisfaction, // Use satisfaction as proxy for response quality
        timestamp: new Date().toISOString()
      })
      
      console.log('Feedback submitted successfully')
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      // Don't show error to user for feedback submission failures
    }
  }

  return (
    <div className="flex flex-col h-screen max-h-screen">
      <Card className="flex-1 flex flex-col">
        <CardHeader className="flex-none">
          <div className="flex items-center justify-between">
            <CardTitle>Elasticsearch Agent</CardTitle>
            <StatusIndicator
              onRetry={handleRetryConnection}
              onToggleMode={() => setUseWebSocketMode(!useWebSocketMode)}
              useWebSocketMode={useWebSocketMode}
            />
          </div>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col p-0">
          <MessageList 
            messages={messages} 
            isLoading={isLoading || isTyping}
            onRetryMessage={handleRetryMessage}
            onSuggestionClick={handleSendMessage}
            onFeedback={handleUserFeedback}
          />
          <MessageInput 
            onSendMessage={handleSendMessage}
            isLoading={isLoading || isTyping}
            placeholder={
              connectionStatus.isConnected
                ? "Ask me about your Elasticsearch data..."
                : "Waiting for connection..."
            }
          />
        </CardContent>
      </Card>
    </div>
  )
} 