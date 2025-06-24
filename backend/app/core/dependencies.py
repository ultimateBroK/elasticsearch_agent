"""Dependency injection for FastAPI."""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError
from app.services.elasticsearch import ElasticsearchService
from app.services.gemini import GeminiService
from app.services.redis import RedisService
from app.services.vector_db import VectorDBService
from app.agents.elasticsearch_agent import ElasticsearchAgent


# Service instances (will be initialized in lifespan)
_elasticsearch_service: ElasticsearchService = None
_gemini_service: GeminiService = None
_redis_service: RedisService = None
_vector_db_service: VectorDBService = None
_elasticsearch_agent: ElasticsearchAgent = None


async def get_elasticsearch_service() -> ElasticsearchService:
    """Get Elasticsearch service dependency."""
    if _elasticsearch_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch service not initialized"
        )
    
    # Check if service is healthy
    if not await _elasticsearch_service.health_check():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch service is unhealthy"
        )
    
    return _elasticsearch_service


async def get_gemini_service() -> GeminiService:
    """Get Gemini service dependency."""
    if _gemini_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini service not initialized"
        )
    
    # Check if service is healthy
    if not await _gemini_service.health_check():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini service is unhealthy"
        )
    
    return _gemini_service


async def get_redis_service() -> RedisService:
    """Get Redis service dependency."""
    if _redis_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not initialized"
        )
    
    # Check if service is healthy
    if not await _redis_service.health_check():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service is unhealthy"
        )
    
    return _redis_service


async def get_vector_db_service() -> VectorDBService:
    """Get Vector DB service dependency."""
    if _vector_db_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector DB service not initialized"
        )
    
    # Check if service is healthy
    if not await _vector_db_service.health_check():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector DB service is unhealthy"
        )
    
    return _vector_db_service


async def get_elasticsearch_agent() -> ElasticsearchAgent:
    """Get Elasticsearch agent dependency."""
    if _elasticsearch_agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch agent not initialized"
        )
    
    return _elasticsearch_agent


# Service initialization functions
def initialize_services():
    """Initialize all services."""
    global _elasticsearch_service, _gemini_service, _redis_service, _vector_db_service, _elasticsearch_agent
    
    _elasticsearch_service = ElasticsearchService()
    _gemini_service = GeminiService()
    _redis_service = RedisService()
    _vector_db_service = VectorDBService()
    _elasticsearch_agent = ElasticsearchAgent(
        gemini_service=_gemini_service,
        elasticsearch_service=_elasticsearch_service,
        redis_service=_redis_service,
        vector_db_service=_vector_db_service
    )


async def cleanup_services():
    """Cleanup all services."""
    global _elasticsearch_service, _gemini_service, _redis_service, _vector_db_service, _elasticsearch_agent
    
    if _elasticsearch_service:
        await _elasticsearch_service.close()
    
    if _redis_service:
        await _redis_service.close()
    
    if _vector_db_service:
        await _vector_db_service.close()
    
    # Reset instances
    _elasticsearch_service = None
    _gemini_service = None
    _redis_service = None
    _vector_db_service = None
    _elasticsearch_agent = None