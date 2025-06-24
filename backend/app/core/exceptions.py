"""Custom exceptions for the application."""

from typing import Any, Dict, Optional


class ElasticsearchAgentException(Exception):
    """Base exception for Elasticsearch Agent."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ServiceUnavailableError(ElasticsearchAgentException):
    """Raised when a required service is unavailable."""
    
    def __init__(self, service_name: str, details: Optional[Dict[str, Any]] = None):
        message = f"Service '{service_name}' is unavailable"
        super().__init__(message, details, status_code=503)


class ConfigurationError(ElasticsearchAgentException):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=500)


class ValidationError(ElasticsearchAgentException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=400)


class ElasticsearchError(ElasticsearchAgentException):
    """Raised when Elasticsearch operations fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=500)


class GeminiAPIError(ElasticsearchAgentException):
    """Raised when Gemini API operations fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=502)


class RedisError(ElasticsearchAgentException):
    """Raised when Redis operations fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=500)


class AgentError(ElasticsearchAgentException):
    """Raised when agent processing fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=500)


class RateLimitError(ElasticsearchAgentException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=429)