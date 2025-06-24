"use client"

import { useState, useEffect, useCallback } from 'react'
import { useChatStore } from '@/store/chatStore'
import { apiClient } from '@/lib/api'
import { SessionData } from '@/types/api'

interface SessionState {
  isLoading: boolean
  error: string | null
  sessionData: SessionData | null
}

export function useSession() {
  const { sessionId, setSessionId, clearMessages } = useChatStore()
  const [state, setState] = useState<SessionState>({
    isLoading: false,
    error: null,
    sessionData: null
  })

  // Load session data when sessionId changes
  useEffect(() => {
    if (sessionId) {
      loadSession(sessionId)
    }
  }, [sessionId])

  const loadSession = useCallback(async (id: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await apiClient.getSession(id)
      setState(prev => ({
        ...prev,
        isLoading: false,
        sessionData: response.session
      }))
    } catch (error) {
      console.error('Failed to load session:', error)
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Failed to load session data'
      }))
    }
  }, [])

  const createNewSession = useCallback(() => {
    const newSessionId = crypto.randomUUID()
    setSessionId(newSessionId)
    clearMessages()
    setState({
      isLoading: false,
      error: null,
      sessionData: null
    })
    return newSessionId
  }, [setSessionId, clearMessages])

  const deleteSession = useCallback(async (id?: string) => {
    const targetId = id || sessionId
    if (!targetId) return

    try {
      await apiClient.deleteSession(targetId)
      
      // If deleting current session, create a new one
      if (targetId === sessionId) {
        createNewSession()
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
      setState(prev => ({
        ...prev,
        error: 'Failed to delete session'
      }))
    }
  }, [sessionId, createNewSession])

  const clearSession = useCallback(() => {
    clearMessages()
    setState({
      isLoading: false,
      error: null,
      sessionData: null
    })
  }, [clearMessages])

  // Auto-create session if none exists
  useEffect(() => {
    if (!sessionId) {
      createNewSession()
    }
  }, [sessionId, createNewSession])

  return {
    sessionId,
    sessionData: state.sessionData,
    isLoading: state.isLoading,
    error: state.error,
    loadSession,
    createNewSession,
    deleteSession,
    clearSession
  }
}