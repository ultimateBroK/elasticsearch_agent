from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, bool] = Field(..., description="Individual service health (elasticsearch, redis, gemini)")


class ElasticsearchQuery(BaseModel):
    """Elasticsearch query request model."""
    index: str = Field(..., description="Elasticsearch index name")
    query: Dict[str, Any] = Field(..., description="Elasticsearch query body")
    size: Optional[int] = Field(10, description="Number of results to return")


class ElasticsearchResponse(BaseModel):
    """Elasticsearch query response model."""
    total_hits: int = Field(..., description="Total number of hits")
    data: List[Dict[str, Any]] = Field(..., description="Query results")
    aggregations: Optional[Dict[str, Any]] = Field(None, description="Aggregation results")


class ChatMessage(BaseModel):
    """Chat message model."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Chat session ID")
    chart_config: Optional[Dict[str, Any]] = Field(None, description="Chart configuration for visualization")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Data for visualization")


class ChartConfig(BaseModel):
    """Chart configuration model."""
    chart_type: str = Field(..., description="Type of chart (line, bar, pie)")
    title: str = Field(..., description="Chart title")
    x_axis: Optional[str] = Field(None, description="X-axis field")
    y_axis: Optional[str] = Field(None, description="Y-axis field")
    options: Dict[str, Any] = Field(default_factory=dict, description="Additional chart options") 