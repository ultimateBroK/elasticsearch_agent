/**
 * API types that match the backend schemas
 */

// Enums matching backend constants
export enum ChartType {
  BAR = "bar",
  LINE = "line", 
  PIE = "pie",
  SCATTER = "scatter",
  AREA = "area"
}

export enum QueryIntent {
  SEARCH = "search",
  AGGREGATE = "aggregate",
  FILTER = "filter",
  CHART = "chart",
  COUNT = "count",
  GENERAL = "general"
}

export enum ServiceStatus {
  HEALTHY = "healthy",
  UNHEALTHY = "unhealthy",
  DEGRADED = "degraded"
}

export enum MessageType {
  MESSAGE = "message",
  TYPING = "typing",
  ERROR = "error",
  PING = "ping",
  PONG = "pong"
}

// API Request/Response interfaces
export interface ChatRequest {
  message: string
  session_id?: string
}

export interface ChatResponse {
  response: string
  session_id: string
  chart_config?: ChartConfig
  data?: any[]
}

export interface ChartConfig {
  chart_type: ChartType
  title: string
  has_data: boolean
  data_count?: number
  use_aggregations?: boolean
  aggregation_data?: any
  suggested_fields?: {
    numeric: string[]
    text: string[]
    date: string[]
  }
  x_axis_suggestion?: string
  y_axis_suggestion?: string
  label_field?: string
  value_field?: string
}

export interface HealthResponse {
  status: ServiceStatus
  timestamp: Date
  services: {
    elasticsearch: boolean
    redis: boolean
    gemini: boolean
  }
}

export interface ElasticsearchQuery {
  index: string
  query: any
  size?: number
}

export interface ElasticsearchResponse {
  total_hits: number
  data: any[]
  aggregations?: any
}

export interface ElasticsearchInfo {
  cluster_info: any
}

export interface IndicesResponse {
  indices: string[]
}

export interface SessionData {
  last_message: string
  last_response: string
  intent: QueryIntent
  timestamp: string
}

export interface SessionResponse {
  session: SessionData
}

// Error response from backend
export interface ApiError {
  error: string
  details: Record<string, any>
  type: string
}

// WebSocket message types
export interface WebSocketMessage {
  type: MessageType
  message?: string
  timestamp?: string
}

export interface WebSocketResponse {
  type: MessageType
  sender?: 'user' | 'agent'
  content?: string
  chart_config?: ChartConfig
  data?: any[]
  intent?: QueryIntent
  timestamp?: string
  error?: string
}