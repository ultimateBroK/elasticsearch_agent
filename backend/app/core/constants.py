"""Application constants and enums."""

from enum import Enum


class ChartType(str, Enum):
    """Supported chart types."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"


class QueryIntent(str, Enum):
    """Query intent types."""
    SEARCH = "search"
    AGGREGATE = "aggregate"
    FILTER = "filter"
    CHART = "chart"
    COUNT = "count"
    GENERAL = "general"


class ServiceStatus(str, Enum):
    """Service health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class MessageType(str, Enum):
    """WebSocket message types."""
    MESSAGE = "message"
    TYPING = "typing"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


# Cache keys
CACHE_KEYS = {
    "session": "session:{session_id}",
    "query": "query_cache:{query_hash}",
    "user_context": "user_context:{user_id}",
}

# Default values
DEFAULT_VALUES = {
    "query_size": 10,
    "max_query_size": 1000,
    "session_ttl": 3600,  # 1 hour
    "query_cache_ttl": 300,  # 5 minutes
    "chart_height": 400,
    "chart_width": "100%",
}

# Supported field types for chart mapping
FIELD_TYPES = {
    "numeric": ["integer", "long", "float", "double", "short", "byte"],
    "text": ["text", "keyword"],
    "date": ["date", "date_nanos"],
    "boolean": ["boolean"],
}

# Chart type recommendations based on data characteristics
CHART_RECOMMENDATIONS = {
    "categorical_single": ChartType.PIE,
    "categorical_multiple": ChartType.BAR,
    "time_series": ChartType.LINE,
    "correlation": ChartType.SCATTER,
    "cumulative": ChartType.AREA,
}