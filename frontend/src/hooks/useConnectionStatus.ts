"use client"

import { useState, useEffect, useCallback } from 'react'
import { useChatStore } from '@/store/chatStore'
import { useHealthCheck } from '@/hooks/useApi'
import { ServiceStatus } from '@/types/api'

interface ConnectionStatus {
  isOnline: boolean
  backendReachable: boolean
  lastChecked: Date | null
  retryCount: number
}

export function useConnectionStatus() {
  const [status, setStatus] = useState<ConnectionStatus>({
    isOnline: navigator.onLine,
    backendReachable: false,
    lastChecked: null,
    retryCount: 0
  })

  const { connection, setBackendHealth } = useChatStore()
  const healthCheck = useHealthCheck()

  // Check if browser is online
  useEffect(() => {
    const handleOnline = () => {
      setStatus(prev => ({ ...prev, isOnline: true }))
      // When coming back online, check backend immediately
      checkBackendHealth()
    }

    const handleOffline = () => {
      setStatus(prev => ({ ...prev, isOnline: false, backendReachable: false }))
      setBackendHealth(ServiceStatus.UNHEALTHY)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [setBackendHealth])

  const checkBackendHealth = useCallback(async () => {
    if (!status.isOnline) {
      return false
    }

    try {
      const result = await healthCheck.execute(() => 
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`, { 
          method: 'GET',
          signal: AbortSignal.timeout(5000) // 5 second timeout
        }).then(res => res.json())
      )

      const isHealthy = result?.status === ServiceStatus.HEALTHY
      
      setStatus(prev => ({
        ...prev,
        backendReachable: isHealthy,
        lastChecked: new Date(),
        retryCount: isHealthy ? 0 : prev.retryCount + 1
      }))

      setBackendHealth(result?.status || ServiceStatus.UNHEALTHY)
      
      return isHealthy
    } catch (error) {
      setStatus(prev => ({
        ...prev,
        backendReachable: false,
        lastChecked: new Date(),
        retryCount: prev.retryCount + 1
      }))
      
      setBackendHealth(ServiceStatus.UNHEALTHY)
      return false
    }
  }, [status.isOnline, healthCheck, setBackendHealth])

  // Periodic health checks
  useEffect(() => {
    // Initial check
    checkBackendHealth()

    // Check every 30 seconds
    const interval = setInterval(checkBackendHealth, 30000)

    return () => clearInterval(interval)
  }, [checkBackendHealth])

  // Exponential backoff for failed connections
  useEffect(() => {
    if (!status.backendReachable && status.retryCount > 0 && status.retryCount < 5) {
      const delay = Math.min(1000 * Math.pow(2, status.retryCount), 30000) // Max 30 seconds
      
      const timeout = setTimeout(() => {
        checkBackendHealth()
      }, delay)

      return () => clearTimeout(timeout)
    }
  }, [status.backendReachable, status.retryCount, checkBackendHealth])

  return {
    ...status,
    checkBackendHealth,
    isConnected: status.isOnline && status.backendReachable,
    connectionQuality: getConnectionQuality(status, connection)
  }
}

function getConnectionQuality(
  status: ConnectionStatus, 
  connection: { retryCount: number; status: string }
): 'excellent' | 'good' | 'poor' | 'offline' {
  if (!status.isOnline || !status.backendReachable) {
    return 'offline'
  }

  if (connection.retryCount === 0 && connection.status === 'connected') {
    return 'excellent'
  }

  if (connection.retryCount <= 2) {
    return 'good'
  }

  return 'poor'
}