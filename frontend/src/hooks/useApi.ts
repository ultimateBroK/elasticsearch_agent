"use client"

import { useState, useCallback } from 'react'
import { apiClient, ApiError } from '@/lib/api'
import { useChatStore } from '@/store/chatStore'

interface UseApiOptions {
  onSuccess?: (data: any) => void
  onError?: (error: ApiError) => void
  showErrorMessage?: boolean
}

export function useApi<T = any>(options: UseApiOptions = {}) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [data, setData] = useState<T | null>(null)
  
  const { addErrorMessage } = useChatStore()

  const execute = useCallback(async (apiCall: () => Promise<T>) => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await apiCall()
      setData(result)
      
      if (options.onSuccess) {
        options.onSuccess(result)
      }
      
      return result
    } catch (err) {
      const apiError = err instanceof ApiError ? err : new ApiError('Unknown error', 0)
      setError(apiError)
      
      if (options.showErrorMessage !== false) {
        let errorMessage = 'An unexpected error occurred'
        
        switch (apiError.status) {
          case 400:
            errorMessage = 'Invalid request. Please check your input.'
            break
          case 401:
            errorMessage = 'Authentication required.'
            break
          case 403:
            errorMessage = 'Access denied.'
            break
          case 404:
            errorMessage = 'Resource not found.'
            break
          case 408:
            errorMessage = 'Request timed out. Please try again.'
            break
          case 429:
            errorMessage = 'Too many requests. Please wait before trying again.'
            break
          case 500:
            errorMessage = 'Server error. Please try again later.'
            break
          case 503:
            errorMessage = 'Service temporarily unavailable.'
            break
          default:
            errorMessage = apiError.message || errorMessage
        }
        
        addErrorMessage(errorMessage, apiError.status !== 400)
      }
      
      if (options.onError) {
        options.onError(apiError)
      }
      
      throw apiError
    } finally {
      setLoading(false)
    }
  }, [options, addErrorMessage])

  const reset = useCallback(() => {
    setLoading(false)
    setError(null)
    setData(null)
  }, [])

  return {
    loading,
    error,
    data,
    execute,
    reset
  }
}

// Specialized hooks for common operations
export function useHealthCheck() {
  return useApi({
    showErrorMessage: false // Health checks shouldn't show error messages
  })
}

export function useChatApi() {
  return useApi({
    onError: (error) => {
      console.error('Chat API error:', error)
    }
  })
}

export function useElasticsearchApi() {
  return useApi({
    onError: (error) => {
      console.error('Elasticsearch API error:', error)
    }
  })
}