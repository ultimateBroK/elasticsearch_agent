"use client"

import React from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useConnectionStatus } from '@/hooks/useConnectionStatus'
import { useChatStore } from '@/store/chatStore'
import { ServiceStatus } from '@/types/api'

interface StatusIndicatorProps {
  onRetry?: () => void
  onToggleMode?: () => void
  useWebSocketMode?: boolean
  className?: string
}

export function StatusIndicator({ 
  onRetry, 
  onToggleMode, 
  useWebSocketMode = true,
  className 
}: StatusIndicatorProps) {
  const { 
    isConnected, 
    backendReachable, 
    connectionQuality, 
    checkBackendHealth,
    retryCount 
  } = useConnectionStatus()
  
  const { connection } = useChatStore()

  const getStatusInfo = () => {
    if (!isConnected) {
      return {
        icon: '🔴',
        text: 'Offline',
        variant: 'destructive' as const,
        description: 'No internet connection'
      }
    }

    if (!backendReachable) {
      return {
        icon: '🔴',
        text: 'Backend Unavailable',
        variant: 'destructive' as const,
        description: `Backend service is not responding ${retryCount > 0 ? `(${retryCount} retries)` : ''}`
      }
    }

    if (useWebSocketMode) {
      switch (connection.status) {
        case 'connected':
          return {
            icon: connectionQuality === 'excellent' ? '🟢' : '🟡',
            text: 'WebSocket Connected',
            variant: 'default' as const,
            description: `Connection quality: ${connectionQuality}`
          }
        case 'connecting':
          return {
            icon: '🟡',
            text: 'Connecting...',
            variant: 'secondary' as const,
            description: 'Establishing WebSocket connection'
          }
        case 'error':
          return {
            icon: '🔴',
            text: 'Connection Error',
            variant: 'destructive' as const,
            description: `WebSocket failed ${connection.retryCount > 0 ? `(${connection.retryCount} retries)` : ''}`
          }
        default:
          return {
            icon: '🔴',
            text: 'Disconnected',
            variant: 'destructive' as const,
            description: 'WebSocket connection lost'
          }
      }
    } else {
      return {
        icon: '🟢',
        text: 'REST API Ready',
        variant: 'default' as const,
        description: 'Using HTTP API mode'
      }
    }
  }

  const statusInfo = getStatusInfo()
  const shouldShowRetry = !isConnected || !backendReachable || connection.status === 'error'

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Badge variant={statusInfo.variant} className="text-xs">
        <span className="mr-1">{statusInfo.icon}</span>
        {statusInfo.text}
      </Badge>
      
      {shouldShowRetry && onRetry && (
        <Button
          size="sm"
          variant="outline"
          onClick={onRetry}
          className="text-xs h-6"
        >
          Retry
        </Button>
      )}
      
      {onToggleMode && (
        <Button
          size="sm"
          variant="ghost"
          onClick={onToggleMode}
          className="text-xs h-6"
        >
          {useWebSocketMode ? 'Use REST' : 'Use WebSocket'}
        </Button>
      )}
    </div>
  )
}

// Detailed status card for debugging
export function DetailedStatusCard() {
  const { 
    isOnline,
    backendReachable, 
    lastChecked, 
    retryCount,
    connectionQuality,
    checkBackendHealth 
  } = useConnectionStatus()
  
  const { connection } = useChatStore()

  return (
    <Card className="w-full max-w-md">
      <CardContent className="p-4 space-y-3">
        <div className="font-medium text-sm">Connection Status</div>
        
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span>Internet:</span>
            <Badge variant={isOnline ? "default" : "destructive"} className="text-xs">
              {isOnline ? '🟢 Online' : '🔴 Offline'}
            </Badge>
          </div>
          
          <div className="flex justify-between">
            <span>Backend:</span>
            <Badge variant={backendReachable ? "default" : "destructive"} className="text-xs">
              {backendReachable ? '🟢 Reachable' : '🔴 Unreachable'}
            </Badge>
          </div>
          
          <div className="flex justify-between">
            <span>WebSocket:</span>
            <Badge 
              variant={connection.status === 'connected' ? "default" : "destructive"} 
              className="text-xs"
            >
              {connection.status === 'connected' ? '🟢' : '🔴'} {connection.status}
            </Badge>
          </div>
          
          <div className="flex justify-between">
            <span>Quality:</span>
            <span className="text-muted-foreground">{connectionQuality}</span>
          </div>
          
          {retryCount > 0 && (
            <div className="flex justify-between">
              <span>Retries:</span>
              <span className="text-muted-foreground">{retryCount}</span>
            </div>
          )}
          
          {lastChecked && (
            <div className="flex justify-between">
              <span>Last Check:</span>
              <span className="text-muted-foreground">
                {lastChecked.toLocaleTimeString()}
              </span>
            </div>
          )}
        </div>
        
        <Button
          size="sm"
          variant="outline"
          onClick={checkBackendHealth}
          className="w-full text-xs"
        >
          Check Now
        </Button>
      </CardContent>
    </Card>
  )
}