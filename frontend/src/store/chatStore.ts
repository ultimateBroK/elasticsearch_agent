import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { ChartConfig, QueryIntent, ServiceStatus } from '@/types/api'

export interface Message {
  id: string
  content: string
  sender: 'user' | 'agent'
  timestamp: Date
  chartConfig?: ChartConfig
  data?: any[]
  sessionId?: string
  intent?: QueryIntent
  error?: boolean
  retryable?: boolean
}

export interface ConnectionState {
  status: 'connected' | 'disconnected' | 'connecting' | 'error'
  lastConnected?: Date
  retryCount: number
  backendHealth?: ServiceStatus
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  sessionId: string | null
  connection: ConnectionState
  
  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  setLoading: (loading: boolean) => void
  setSessionId: (sessionId: string) => void
  clearMessages: () => void
  updateLastMessage: (update: Partial<Message>) => void
  setConnectionStatus: (status: ConnectionState['status']) => void
  setBackendHealth: (health: ServiceStatus) => void
  incrementRetryCount: () => void
  resetRetryCount: () => void
  addErrorMessage: (error: string, retryable?: boolean) => void
}

export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set, get) => ({
        messages: [],
        isLoading: false,
        sessionId: null,
        connection: {
          status: 'disconnected',
          retryCount: 0,
        },
        
        addMessage: (message) => {
          const newMessage: Message = {
            ...message,
            id: crypto.randomUUID(),
            timestamp: new Date(),
          }
          
          set((state) => ({
            messages: [...state.messages, newMessage],
          }))
        },
        
        setLoading: (loading) => set({ isLoading: loading }),
        
        setSessionId: (sessionId) => set({ sessionId }),
        
        clearMessages: () => set({ messages: [] }),
        
        updateLastMessage: (update) => {
          set((state) => {
            const messages = [...state.messages]
            const lastIndex = messages.length - 1
            
            if (lastIndex >= 0) {
              messages[lastIndex] = { ...messages[lastIndex], ...update }
            }
            
            return { messages }
          })
        },

        setConnectionStatus: (status) => {
          set((state) => ({
            connection: {
              ...state.connection,
              status,
              lastConnected: status === 'connected' ? new Date() : state.connection.lastConnected,
            }
          }))
        },

        setBackendHealth: (health) => {
          set((state) => ({
            connection: {
              ...state.connection,
              backendHealth: health,
            }
          }))
        },

        incrementRetryCount: () => {
          set((state) => ({
            connection: {
              ...state.connection,
              retryCount: state.connection.retryCount + 1,
            }
          }))
        },

        resetRetryCount: () => {
          set((state) => ({
            connection: {
              ...state.connection,
              retryCount: 0,
            }
          }))
        },

        addErrorMessage: (error, retryable = false) => {
          const errorMessage: Message = {
            id: crypto.randomUUID(),
            content: error,
            sender: 'agent',
            timestamp: new Date(),
            error: true,
            retryable,
          }
          
          set((state) => ({
            messages: [...state.messages, errorMessage],
          }))
        },
      }),
      {
        name: 'chat-store',
        partialize: (state) => ({
          sessionId: state.sessionId,
          messages: state.messages.slice(-50), // Keep only last 50 messages
        }),
      }
    ),
    {
      name: 'chat-store',
    }
  )
) 